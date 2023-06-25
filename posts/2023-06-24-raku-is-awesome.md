--- 
title: Raku is pretty damn Cool
categories: programming
tags: raku
excerpt_separator: <!--more-->
--- 

## Introduction

The first time, I've heard of [Raku](https://www.raku.org/) was maybe a year
ago. I was too busy to look into it though. I've done that now and BOY OH BOY,
do I like this language.

<!--more-->

Raku is a scripting language, and I'd describe it as a mix of Bash and Python.
And that is awesome. Why is that? Because I write a lot of Bash scripts, but
I'm not super happy with it. They always start harmless, just a couple of
program invocations, maybe some light string substitution ... it's alright.
Then you blink once, and suddenly they are 300 lines long, with 50 lines being
arg-parse code, and the rest feels like it might break any second. Also, bash
is hard to remember. Writing simple string parsing is NOT straight forward
[^1], and sometimes nested strings and quoting get extremely painful.

Additionally, Bash is not cross-platform. Ok, it is. I admit it. But most of my
colleagues are Windows users, and somehow, only a single one of them has
[MSYS](https://www.msys2.org/) installed. It might be hard to set up, I don't
know. Also, Bash is not nice on the eye. Its syntax is ... peculiar. So we're
maintaining a lot of bat and bash scripts that do the same thing.

But guess what: all of them have Python. So some scripts that would have been
Bash are Python instead. But Python is actually not that great for tasks that
are typically done by Bash. It's very verbose for that use case, and you have to
write quite some boilerplate.

Therefore, I was on the hunt for a Bash replacement for a long time. I tried
Ruby, but it didn't do that much better than Python. I was excited for
[Oil shell](https://www.oilshell.org/), but its own scripting language (YSH) is
not there yet. Raku hit this sweet spot. It is AWESOME at the things that Bash
is usually used for, and it does not have Bash's downsides.

## Some Raku Nuggets

This is not going to be a tutorial, but I'll show you my favorite Raku
features. There are many more, and these are not necessarily the biggest ones.

In general Raku has everything the typical scripting language has. Functions,
Classes, Exceptions, typical data types (like lists and dicts / hash maps),
modules, and all the usual control flow. An abundance of those. In all forms
and colors. One interesting thing that is unusual is the type system: you
don't need to type anything, and by default you get dynamic typing, but you
can, and then the (byte code) compiler will check the types for you.

### String Literal Lists

I actually don't know how they're named, but they're my favorite feature.

```raku
my @literal_list = <foo bar baz>;
```

This gives you a list of string literals split by the spaces. In Python, you'd have
to write `["foo", "bar", "baz"]` or `"foo bar baz".split()`. I hate writing
that. Both versions. I like this idea so much, that I wonder how this is the
first time I ever encountered it.

This is especially nice to execute external commands:

```raku
run <<rg 'ls -lah' -g "*.$file_type">>;
```

You might have notices that the first example uses `<...>` while the second one
uses `<< ... >>`. The difference is the same as between `'...'` and `"..."`
strings in Bash (and Raku): The second one allows for interpolation. And it
supports skipping spaces when splitting the list, if the spaces are between
quotes.

Raku is not without its quirks. Using `my` (among others) to declare variables,
and prefixing variable names with symbols (they call it sigils) are two of
those. I haven't found the quirks of Raku ruining my experience so far though.
Raku prefixes scalars ("single things") with a `$`, arrays (or lists or
sequences, "many things") with an `@` and hashes (== dicts / hash maps) with
`%`. It doesn't hurt to have this kind of visual reminder tbh.

### Junctions

My second favorite feature. Yes, I ordered them by how much I like them.
The two most important ones are *any* and *all* junctions:

```raku
if $x == 1 | 2 | 3 { say "yup"; }
```

This is an *any* junction. *all* junctions are written with the `&` instead of
the `|`. You can also create them from lists using the `any` or `all`
functions.

No more `if (x == 1 || x == 2 || x == 3)` (god I hate to write that). I have to
admit Python has `if x in { 1, 2, 3 }`, but that is way less flexible. Further
down this post, I'll show you another example of junction application.

### All the lambdas

Raku has many ways to define anonymous functions:
```raku
(1, 2, 3).map(* + 1)
```
Here, `* + 1` defines a function in the same manner as Scala's `_` operator. The
star represents the function argument.

Or, if the argument is not on the outmost level: `{ some_func( $_, "fix" ) }`,
or, if you want multiple arguments: `{ some_other_func( $^a, $^b, "fix" ) }`.
In the second example the lambda has two arguments (notice, that they start
with `$^` instead of just `$`), the order is alphabetical, so `$^a` is the
first one and `$^b` is the second one.

You can also make the args explicit: ` -> $a, $b { say "$a: $b"; }` which looks
a little strange, but makes a lot of sense when you look at it in the context
of raku's for loop:

```raku
for <foo bar baz quz> -> $a, $b { say "$a: $b"; }
```

Btw, this automatically "chunks" the list because I defined two
arguments. The output is:

```
foo: bar
baz: quz
```

In general, Raku is a very concise language.

### Multiple Dispatch 

A.k.a. function overloading. You can use functions like this:

```raku
multi foo(Str $a_str) {
    say "$a_str is a str";
}

multi foo(Int $a_int) {
    say "$a_int is an integer";
}

foo 1;
foo "2";
```

The only language I really used that has this is C++. WHY? This is so
convenient. I don't want to define a trait for this (looking at you, Rust)
and even if I do, it only overloads on a single arg. Here, you get it for all
args. Also, you get optional arguments, named arguments and default values.

### Arg parsing

And last but not least: Argparsing. No one writes argparse code by hand, right?
RIGHT, C? Rust has pretty good libraries, but you have to install them. Python
has it's argparse module, but that is also pretty verbose (and don't get me
started on using pip). Let's look at how Raku does it:

```raku
# inside "frobnicate.raku" 
sub MAIN(
  Str   $file where *.IO.f = 'file.dat',
  Int  :$length = 24,
  Bool :$verbose
) {
    say $length if $length.defined;
    say $file   if $file.defined;
    say 'Verbosity ', ($verbose ?? 'on' !! 'off');
}
```

and if you call it without an argument you get:

```
Usage:
  frobnicate.raku [--length=<Int>] [--verbose] [<file>]
```

Yes, you define a `MAIN` function, and the arg parsing is generated
automatically from its signature. 

You can even put a check on the value into it (look at the where clause in 3rd
line). The `:` in `Int :$length = 24` makes `$length` named argument, which is
the reason it is parsed as option.

### No imports

You might have missed it, but all of this works without any imports. When was
the last time you wrote a python script with less than 3 imports? This might
not seem significant, but if you take together the fact that raku is generally
very concise with not having to import stuff from the stdlib, you end up with scripts that
are less than half the size of their Python equivalent, especially since it's
absolutely not uncommon to have 10+ imports in Python.
 
## An Example

Those were all small, out of context examples. So I thought, I should at least
show you one real world script. I have a script that deletes all git branches
which have already been merged, and are safe to delete. That started out as a
Python script. Then became a Ruby script, and now a Raku script. 
What it does is: it checks if the current branch is main or master, and
switches to it if not. Then it calls `git branch -d` on each branch (which will
simply not delete the branch, if it is not merged). This is the script:

```raku
#! /usr/bin/env raku

sub MAIN {
  my @branches = run(<git branch>, :out).out.lines(:close)
    || die "something went wrong with git"; # this happens, when run fails

  if not on-master-or-main @branches { 
    switch "master" || switch "main"; # if the second case fails too, the
                                      # script will die
    @branches = run(<git branch>, :out).out.lines(:close);
  }

  for @branches {
    # this matches the regex that checks whether the string starts with a *
    # against $_, which contains the current branch.
    if not m/^\*/ {
      run <<git branch -d "{$_.trim}">>;
    }
  }
}

sub switch($branch) { run <<git switch "$branch">> }
sub on-master-or-main(@branches) { "* master" | "* main" ~~ any @branches }
```

The coolest part of this script is probably the body of `on-master-or-main`.
Told you junctions are more flexible. But this, in general, just oozes
efficiency (letter for effect wise). 

## A Confession

There is one thing, I didn't tell you so far: Raku is actually Perl 6. They
decided to rename it to Raku, because it's not backwards compatible, and maybe
to get rid of the negative associations with Perl.

So, Perl is dead, right? Or at least as dead as a once successful programming
language ever gets. So ... undead? Do you need to be afraid of Raku because
it's Perl 6? I don't think so. I tried to find out a little about why Perl was
so popular once, but isn't anymore. This is probably very incomplete but: Perl
is actually quite old (it came out in 1987), and back then, there wasn't as
much competition. In the early days of the web, Perl was THE language of the
backend, and I think that accounts for the majority of Perl applications. Then
PHP came around and became the new language of the backend, and Java, and C#. I
don't know Perl, but what I gather from the [Major changes from
Perl](https://en.wikipedia.org/wiki/Raku_(programming_language)#Major_changes_from_Perl)
section of the Raku wiki article is that Perl has some significant
shortcomings: You can't define function parameters in Perl, you use them
implicitely like in Bash, the sigils (the signs in the beginning of variable
names) could change depending on the context, and were very confusing at times.
And there was no easy way to create structs/records.

Additionally, Perl has this reputation of being a "write once" language,
because perl code became unreadable very quickly (allegedly). You can
definitely write unreadable code in Raku. Easily. Especially when you abuse its
ability to leave out parenthesis to the fullest. However, you can also write
unreadable code in every other programming language. It's your responsibility
as the programmer to not do that. I think one more reason for this reputation
is the fact that, at the time when Perl was heavily utilized for backends, it
wasn't common knowledge how to write a backend. Everyone did it differently,
and a lot was unclear. And Perl's other big use-case, shell-scripting, doesn't
help either. Shell script's just have a tendency of becoming unreadable if
you're not very careful, no matter what language.

## Conclusion

There is much more interesting stuff in Raku. Many features that I didn't
touch: grammars, meta operators (I LOVE them, but this article is long enough
as it is), async, and probably some more, and it's fascinating from a language
design perspective. I'll probably write at least one more article about it. If
you became interested in it, I recommend the following resources (in that
order):

1. [Learn Raku in Y minutes](https://learnxinyminutes.com/docs/raku/)
1. [A Raku guide](https://raku.guide/)
1. [Perl 6 at a glance](https://andrewshitov.com/perl6-at-a-glance/) (scroll
   down, there is a free PDF)

Imo, Raku shines as a Bash replacement. And it is cross-platform. More so than
Bash. You can write bigger stuff, e.g. backends, in it, but I'd refrain from
that. Not because of anything specifically Raku related, but because I think
you should write long-running processes in efficient, compiled languages. This
saves energy, and in turn CO2 and helps the climate. Oh, and because you will
want to use external libraries for that, and package management for scripting
languages is terrible.

Thanks for reading :)

[^1]: Yes we've got awk for that. Also not super straight forward. Hands
    up: who can write a Bash script involving awk and sed without googling and
    at least 10 attempts?
