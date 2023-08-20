--- 
title: The Little Joys of Code: Proc Macros
categories: programming
tags: Rust, Macros
permalink: /blog/proc_macros.html
excerpt_separator: <!--more-->
---

Most of the code software engineers write is pretty mundane, which is good.
Simple code is easier to read, to maintain, and has less bugs.
However, sometimes we write code that feels super cool, and makes us want to
show it off to our peers. Well, at least for me that's the case. And this is
precisely what this post is about: a cool piece of code, that made me smile,
and that I want to share with other people that might appreciate it too.

<!--more-->

## The Motivation

I was writing a new http server using
[warp](https://github.com/seanmonstar/warp). In warp you generate an API by
chaining filters, e.g. like this:

```rust
// ...
let routes = warp::post()
    .and(warp::body::content_length_limit(1024 * 16))
    .and(or_them!(
        warp::path("api1").and(warp::body::json()).and_then(api1_handler),
        warp::path("api2")
            .and(warp::body::json())
            .and_then(api2_handler),
        //...
  ));

warp::serve(routes).run(([127, 0, 0, 1], 3030)).await
// ...
```

For a function to be usable as handler it must fulfill certain conditions,
that are encoded in the function signature of `and_then`

```rust
fn and_then<F>(self, fun: F) -> AndThen<Self, F>where
    Self: Sized,
    F: Func<Self::Extract> + Clone,
    F::Output: TryFuture + Send,
    <F::Output as TryFuture>::Error: CombineRejection<Self::Error>,
```

However, an `anyhow::Result` does not fulfill them. And I want those
`anyhow::Result`s. Without [anyhow](https://docs.rs/anyhow/latest/anyhow/),
Rust's error handling is exhausting. So I needed to transform my handler
functions so that their return type matches. In Python I would've used a
decorator function for that:

```python
def eat_error(f):
  def inner(*args, **kwargs):
    return some_transformation(f(*args, **kwargs))
  return inner
```

And I knew that there was this one type of Rust macros that looked suspiciously
similar to Python decorators. So I read up on them, and tried to do the same in
Rust ... And ran into the first problem. You cannot just forward arguments in
Rust like in the Python example, because your function signature might look
something like this: 

```rust
fn use_foo(Foo {a, ..}: Foo) {
  println!("{}", a);
}
```

in which case you don't have the necessary information in the function to
forward it to a function with the same signature. It would have been possible
to check that the function only has "normal" parameters, but I didn't want that
restriction. 

This isn't going to be a tutorial about proc macros (if you want to learn them,
I'd recommend
[this](https://dev.to/dandyvica/rust-procedural-macros-step-by-step-tutorial-36n8)
or
[this](https://blog.jetbrains.com/rust/2022/03/18/procedural-macros-under-the-hood-part-i/)),
but they take two token streams, the first one contains the "arguments" of the
proc macro, and the second one the annotated function. You can transform them
however you like, and return a new token stream, that replaces the annotated
function. Since you cannot really work with token streams, you use the
[syn-crate](https://docs.rs/syn/latest/syn/) to transform the token stream into
abstract syntax trees, and use the
[quote-crate](https://docs.rs/quote/latest/quote/) to generate the token stream
that is then returned, by combining normal code with placeholder variables that
contain elements of the input code.

I ended up with something like this:

```rust
#[proc_macro_attribute]
pub fn eat_err(_ : TokenStream, input: TokenStream) -> TokenStream {
    let orig_fn = parse_macro_input!(input as ItemFn);
    let ItemFn {
        attrs,
        vis,
        mut sig,
        block,
    } = orig_fn;
    assert!(
        sig.asyncness.is_some(),
        "eat_err can only be attached to async functions"
    );
    let name = sig.ident.clone();

    // generate TreeNode for the new result type
    let new_result_type_tokens: TokenStream =
        quote! { std::result::Result<warp::http::StatusCode, warp::Rejection> }.into();
    let new_result_type = parse_macro_input!(new_result_type_tokens as syn::Type);

    let old_result_type: Box<syn::Type>;
    // replace the output type in the function signature
    match &mut sig.output {
        ReturnType::Default => panic!("Return type must be a Result"),
          ReturnType::Type(_, t) => {
              old_result_type = t.clone();
            *t = Box::new(new_result_type);
        }
    }

    // generate the new body
    let new_fn_tokens: TokenStream = quote! {
        #vis #sig {
            let result: #old_result_type = (async #block).await;
            result.map_err(|e| {
                error!("{:?}", e.context(stringify!(#name)));
                warp::reject()
            })
        }
    }
    .into();

    // convert the new function tokens back into a TreeNode, so we can attach the attributes which
    // were lost when we generated the new body
    let mut new_fn = parse_macro_input!(new_fn_tokens as ItemFn);
    new_fn.attrs = attrs;
    quote! { #new_fn }.into()
}
```

This is a whole lot more complicated than the Python version. I first
deconstruct the `ItemFn`, which is the syntax tree node type for a function,
into it's components, check that it's an async function, store the function
name, generate a new return type using the
[quote-crate](https://docs.rs/quote/latest/quote/) and put it in the signature,
and then, finally, generate the code for the function, that is going to replace
the annotated function. I wrap the old body of the function into an async
block, which allows to use the `?` operator. Without the async this wouldn't
have worked, because then the `?` would return from the function instead of the
block.

If an error is returned, it is printed using the
[log-crate](https://docs.rs/log/latest/log/), and then it's replaced by a
`warp::Rejection`.

Then I parse The token stream into an `ItemFn` again, to reattach the function
attributes. So this works:

```rust
#[eat_err]
pub async fn new_run(data: RequestData) -> Result<StatusCode> {
    let mut conn = connect_db().await?;
    let info = some_db_query(&mut conn, &data.field1, &data.field1).await?;
    schema::insert_something(&mut conn, &data.field3, &info).await?;
    Ok(StatusCode::OK)
}
```

Kinda. Because now it wants us to import `log::error`. Event though it's not to
be seen anywhere. So I adjusted the Macro a little, and now, you provide the
macro that is used for error reporting as an argument:

```rust

#[proc_macro_attribute]
pub fn eat_err(logger_ident_token_stream: TokenStream, input: TokenStream) -> TokenStream {
    let logger_ident = parse_macro_input!(logger_ident_token_stream as syn::Ident);
    let orig_fn = parse_macro_input!(input as ItemFn);
    let ItemFn {
        attrs,
        vis,
        mut sig,
        block,
    } = orig_fn;
    assert!(
        sig.asyncness.is_some(),
        "eat_err can only be attached to async functions"
    );
    let name = sig.ident.clone();

    // generate TreeNode for the new result type
    let new_result_type_tokens: TokenStream =
        quote! { std::result::Result<warp::http::StatusCode, warp::Rejection> }.into();
    let new_result_type = parse_macro_input!(new_result_type_tokens as syn::Type);

    let old_result_type: Box<syn::Type>;
    // replace the output type in the function signature
    match &mut sig.output {
        ReturnType::Default => panic!("Return type must be a Result"),
        ReturnType::Type(_, t) => {
            old_result_type = t.clone();
            *t = Box::new(new_result_type);
        }
    }

    // generate the new body
    let new_fn_tokens: TokenStream = quote! {
        #vis #sig {
            let result: #old_result_type = (async #block).await;
            result.map_err(|e| {
                #logger_ident!("{:?}", e.context(stringify!(#name)));
                warp::reject()
            })
        }
    }
    .into();

    // convert the new function tokens back into a TreeNode, so we can attach the attributes which
    // were lost when we generated the new body
    let mut new_fn = parse_macro_input!(new_fn_tokens as ItemFn);
    new_fn.attrs = attrs;
    quote! { #new_fn }.into()
}
```

And now it can be called like this:

```rust
#[eat_err(error)]
pub async fn new_run(data: RequestData) -> Result<StatusCode> {
    let mut conn = connect_db().await?;
    let info = some_db_query(&mut conn, &data.field1, &data.field1).await?;
    schema::insert_something(&mut conn, &data.field3, &info).await?;
    Ok(StatusCode::OK)
}
```

In general, I'm pretty happy with this. It's not too complicated, allows me to
use `anyhow::Result` in the handler, without having to wrap all handler
functions into a similar closure for result transformation, and allows handlers to
have different signatures.

However, a grain of salt is left: I really dislike parsing the new function back
into an `ItemFn` just to reattach the attributes. If someone knows a better way,
please let me now.

---

**Edit:**

Thanks to 
[u/MichiRecRoom's comment on Reddit](https://www.reddit.com/r/rust/comments/y5g1wg/comment/isnv23k/?context=3)
I was able to clean the code up a little, and it looks like this now:


```rust
pub fn eat_err(logger_ident_token_stream: TokenStream, input: TokenStream) -> TokenStream {
    let logger_ident = parse_macro_input!(logger_ident_token_stream as syn::Ident);
    let orig_fn = parse_macro_input!(input as ItemFn);
    let ItemFn {
        attrs,
        vis,
        mut sig,
        block,
    } = orig_fn;
    assert!(
        sig.asyncness.is_some(),
        "eat_err can only be attached to async functions"
    );
    let name = sig.ident.clone();

    // generate TreeNode for the new result type
    let new_result_type =
        syn::parse_quote! { std::result::Result<warp::http::StatusCode, warp::Rejection> };

    let old_result_type: Box<syn::Type>;
    // replace the output type in the function signature
    match &mut sig.output {
        ReturnType::Default => panic!("Return type must be a Result"),
        ReturnType::Type(_, t) => {
            old_result_type = t.clone();
            *t = Box::new(new_result_type);
        }
    }

    // generate the new function
    quote! {
        #(#attrs)*
        #vis #sig {
            let result: #old_result_type = (async #block).await;
            result.map_err(|e| {
                #logger_ident!("{:?}", e.context(stringify!(#name)));
                warp::reject()
            })
        }
    }
    .into()
}
```
