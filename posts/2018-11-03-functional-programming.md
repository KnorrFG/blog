--- 
title: Functionalish Programming
categories: programming
permalink: /blog/functionalish_programming.html
excerpt_separator: <!--more-->
--- 

There already is a myriad of blog posts on functional programming, with this
post, I don't try to give an introduction to it, but I want to highlight, how
we can get inspirations from it, to improve our code. This is why the post is
called "functionalish" programming, instead of "functional" programming.

<!--more-->

But before I can talk about what can be learned from it, it is necessary to
talk about what functional programming actually is. Let's see what Wikipedia
has to say:

> In computer science, functional programming is a programming paradigm - a style
> of building the structure and elements of computer programs - that treats
> computation as the evaluation of mathematical functions and avoids
> changing-state and mutable data.

There are already two important principles in there:

1. Avoid changing state
2. Avoid mutable data

The first one, avoiding state change, is a no brainer. Most of us learn very
early that it is a bad idea to make a function depend on a global variable.
There are some rare cases where that might be a good idea, but generally it's
not. If a function is pure, that is its output only depends on its input, and
it does not change any sort of global state, like a display for example, then
it's easy to test and reliable. Great. But wait, if we aren't allowed to do any
i/o because that's state change we cannot write any useful programs. So yeah,
we should try to keep functions pure, but only where applicable.

I want to showcase two bugs that cost me a lot of time:

1. I used the "choose directory" dialog of a GUI-toolkit which did not only return
   the path of the selected folder, but also changed the programs working
   directory to the chosen folder. I was absolutely unaware of this second part,
   which way later in the program resulted in plugin-loading errors. 
2. I was using pythons random.shuffle() function. The code looked something
   like this: `shuffeled_elems = random.shuffle(elems)`. This
   function shuffles its argument, it does not return a shuffled version of it.
   I was not aware of that, and the fact, that 
   [this](https://stackoverflow.com/questions/976882/shuffling-a-list-of-objects)
   is the first result when googling "python random shuffle" shows that I'm not
   the only one. Since in python, a function without return value simply returns
   `None` there was no easily catchable error.

Admittedly, both of those problems could have been prevented by reading the
documentation more carefully, or at all in the second case, but avoiding this
kind of behavior in your own functions will reduce the probability of errors,
which is a good thing. 

The second point, "Avoid mutable data", is more controversial. In C++ it would
translate to: only use `const` variables, and in python it would translate to:
don't change a variable after its creation. 
Of course, I don't want to tell you to not use lists anymore. Since python
lacks some important concepts that functional languages tend to have, like
e.g. tail recursion, it would really not be wise to ban all mutability from your
code. But still, I'd advice to use [namedtuple]s or tuples whenever possible.
If I had used a tuple instead of a list, I would have caught that second bug
instantly.

Another important point in functional programming is to use functions as
arguments, and return values. This does not come intuitively, but it can
increase code readability a lot.

An example:
```python
coords_of_interest = pipe(mat_acc_map.shape, iter_3D_vol_coords, 
                                             filter(lambda coord: mat_acc_map[coord] != 0), 
                                             tuple)
```

I guess two things need to be explained before this becomes clear:

* `pipe` is a function that takes anything as first argument, and then a bunch
of functions for its varargs. It then feeds the first argument as input to the
first function, the output of the first function as input to the second
function, and so on, and in the end it will return the return value of the last
function. (And in the above example, the input is a numpy array)
* `filter` is curried, which means that if you call it with an incomplete set
of arguments, it will return a function which only takes the remaining
arguments, and remembers the one, that were already set. So if you have a
curried version of `filter` you can define a function that takes an iterable
and only returns those elements that are even with 
`even_only = filter(lambda x: x % 2 == 0)`

(By the way, `pipe` and `filter` are both defined in the awesome [toolz] library)

So, provided the knowledge over `pipe` and curried functions, the source code
example above becomes quite easy to read: "the coordinates of interest are
those coordinates where the value in the array is not zero"

The Code above also has another advantage which does not immediately become obvious.
`iter_3D_vol_coords` and `filter` both return generators. Which means every
result is computed lazily, i.e. when it's queried. So, `tuple` looks at the
first element, that `filter` returns, then `filter` looks at the first element,
that is returned by `iter_3D_vol_coords`, if it is suitable it will be
returned, otherwise the next element will be tested. This avoids to first have
a complete list of coordinates, and then filter it. In this example the
difference isn't too big, but in a lot of scenarios it can reduce the memory
consumption by a lot. If you don't know generators, I recommend 
[this](https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do)
answer on stackoverflow.

I want to conclude this post with a few rules of thumb, which I try to respect
 as much as possible:

* write pure functions whenever possible
* use immutable types whenever possible, especially [namedtuple] (you can also
derive classes from it)
* use [toolz], especially `pipe` and `curry` (but it also has a lot of other
very convenient functions)
* use generators whenever possible

Following these few rules has made my code safer, easier to read, easier to
parallelize, and less RAM intensive.

[toolz]: https://toolz.readthedocs.io/en/latest/index.html
[namedtuple]: https://docs.python.org/3.7/library/collections.html#collections.namedtuple
