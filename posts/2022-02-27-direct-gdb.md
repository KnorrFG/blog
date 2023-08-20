--- 
title: Debugging with GDB
categories: programming
tags: C, GDB
permalink: /blog/using_gdb_directly.html
excerpt_separator: <!--more-->
---

My first programming language was C++ and for a long time, I was using Visual
Studio Express in Windows. When I had to debug something, I would click on the
line number to set a breakpoint and press F5. Maybe I'd add some variables to
the watch window, and press some F-keys a couple of times. Recently, I switched
jobs and I'm now mostly developing firmware in C. Since I switched to using
Linux and Vim ~7 years ago, I needed to update my debugging workflow. I
actually didn't find a neat tutorial that covers the whole picture, so I
figured I could write one myself.

<!--more-->

During the last 5 years, I mostly worked with Python, and I really like
debugging in Python. You'd just put a `breakpoint()` function call into your
code somewhere and repl into the program. I wanted to see how close I get to
that in C. As C is not an interpreted language, my hopes weren't that high, but
it turns out debugging in C is quite comfortable. As a bonus, you can use GDB
not only to debug C and C++, but also Rust, Nim, and probably any language that
respects the C-ABI (althoug I don't know this for a fact).

## GDB Basics

First, we need a program to debug. Let's take this one:

```c
// program.c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void print_product(int a, int b) {
    int product = a * b;
    printf("Product: %d\n", product);
}

void print_arguments(int argc, char **argv) {
    for (int i = 1; i < argc; i++) {
        printf("%s ", argv[i]);
    }
    printf("\n");
}

int main(int argc, char **argv) {
    print_arguments(argc, argv);
    srand(time(NULL));
    for (int i = 0; i < 10; i++) {
        print_product(rand(), rand());
    }
    return 0;
}
```

To debug the program, it's important that it contains debugging symbols. To
add debugging symbols when compiling with gcc add the `-g` flag. So let's
compile this program:

```bash
gcc -g -o program program.c
```

We can now debug this program by running:

```bash
gdb program
```

this will launch us into a
[repl](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop). To
run the program until it hits the main function, type `start`. Now you have the
typical debugger actions that you can execute by typing them into the repl. You
can go to the next line by entering `n` (of course you have to press return
too), `s` to step into the current function call, `r` to run until you hit a
breakpoint, and 
[some more](https://www.tutorialspoint.com/gnu_debugger/gdb_commands.htm). To
set a breakpoint, type `b <line>` where `<line>` is the line number you want
it in. If your project consists of multiple files, you'll have to type 
`b <filename>:<line>` however, `<filename>` does not need to be a complete path,
just the name is enough. Btw, gdb allows for tab completion. Alternatively you can
set a breakpoint to a function like this `b <functionname>`.

To see the context of a variable, we can use `p` like `p product` if we break
at line 6. But we can also evaluate nearly arbitrary c expressions e.g. `p
product * 5`.

## Using gdb scripts

This is still not nice though, now we'd have to enter all breakpoints over and
over again, when we restart the debugging session. But there is a
way out of this: gdb scripts. If you invoke gdb with the -x option, you can
pass it a file containing gdb commands, that it should execute.

```bash
gdb -x gdbscript program
```

we can now write our breakpoints into the script, e.g. 

```gdb
# gdbscript
b 6
b 11
r
```

And now our breakpoints are stored. But there is more to it. Typically I want
to check some variables, and I'm not very interested in running the program
further than that. Let's say, we wanted to see the value of the product
variable, for all loops, and dont care about the rest:

```gdb
# gdbscript
b 6
commands
    p product
    c
end

run
```

and then run gdb with `--batch` like this:

```bash
gdb -x gdbscript program --batch
```

Now gdb will quickly print out the value of `product` for all iterations, and
exit again. A `commands` statement after a breakpoint will execute all
contained commands once a breakpoint is hit. The last command, the `c` means
`continue` and will resume the program flow until the next breakpoint is hit,
once the breakpoint was hit the last time, gdb will end execution thanks to the
`--batch` parameter.

Another cool example: let's say, for whatever reason, we are interested in the
value of `product` only during the third call of `print_product()`. (Which is
of course silly, since the program prints it anyway, but in real world
debugging, a situation like this might arise)

```gdb
set $n = 0

b 6
commands
    set $n = $n + 1
    if $n == 3
        printf "Product is: %d\n", product
    else
        c
    end
end

run
```

As you can see we define a variable `$n` and use it to count up, and print our
required information in the third round. After the third round, gdb quits
automatically thanks to `--batch`. For a more complete tour through gdb's
scripting capabilities, I recommend the tutorial on adacore.com: 
[part 1](https://www.adacore.com/gems/gem-119-gdb-scripting-part-1) and
[part 2](https://www.adacore.com/gems/gem-120-gdb-scripting-part-2).

## The .gdbinit file

There is a script, that gdb will always implicitly load if it exists: ~/.gdbinit
You can put functions you use often in there, or configuration. Mine looks like
this:

```gdb
set width 0
set height 0
set print pretty on
set confirm off
```

Setting width and height to 0, will prevent gdb from paging long outputs, the
third line makes gdb prettify the output, and the last line prevents it from
asking if we really want to quit.

## Conclusion

This is largely what I have. In general, I'm quite happy with the power and
flexibility. It might be a little more work than placing a breakpoint in an
IDE, but you get so much more out of it. Also, in IDEs I always found it
annoying to call the debugger with arguments, because you'd have to find the
right options dialog. Here you can simply append them to the debugger
invocation:

```bash
gdb -x gdbscript --batch --args program --flags and some args
```

Also, if you require a more complex setup for debugging, e.g. because you have
to start other programs too, you can put all of that together in a bash script.

Of course, there is much more to know about gdb, and this is barely an
introduction.
