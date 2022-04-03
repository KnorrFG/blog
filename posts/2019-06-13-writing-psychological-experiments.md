--- 
title: How to code basic psychological experiments with Python quickly
categories: programming 
tags: python pyparadigm
permalink: /blog/basic_paradigm.html
excerpt_separator: <!--more-->
--- 

A few days ago, I read an article: [How to code basic psychological experiments with Python](https://www.codementor.io/mathiasgatti/how-to-code-basic-psychological-experiments-with-psychopy-vrve71wxm)
by Mathias Gatti.
It advertises PsychoPy, which is a python library to create psychological
paradigms, which is really just  a fancy name for what is basically a very
simple mini game that will usually measure reaction times or the like. In his
post, he walks the reader through the code necessary for a very simple
paradigm that consist of only 2 screens, the first one says "press any
key to continue", and once you do, you are taken to the second screen which
says "press [ n ] to continue" and "press [ q ] to exit". It will then measure
your reaction time and take you back to the beginning if you press *n* or exit
and save the results to a csv-file if you press *q*. 

In this post I will implement exactly the same paradigm but using
[PyParadigm](https://pyparadigm.readthedocs.io),
which is a library for paradigm creation that I wrote. The advantage that I
want to demonstrate is that it requires much less code to write paradigms with
PyParadigm than with PsychoPy, therefore you can work more quickly.
Also, less code means less bugs.

<!--more-->
Use pip to install PyParadigm:

```bash
pip install pyparadigm
```

So let's jump right in.  The first thing are the imports and some color codes:

```python
import pyparadigm as pp
import pygame as pg
import pandas as pd

import time
import datetime

gray = 0x969696
black = 0
white = 0xFFFFFF
```

Pygame is game development library, and automatically installed with
PyParadigm. For those that know Pygame: PyParadigm will create
`pygame.Surface` objects, and can be used in conjunction with Pygame.

The next thing is the main function:
```python
def main():
    pp.init((300, 300), display_pos=(200, 200))
    results = run_experiment()
    outfile = 'experiment_' + str(datetime.date.today()) + '.csv'
    pd.DataFrame(results, columns=["Key", "Time"]).to_csv(outfile)
    print("Experiment saved as:", outfile)
```
`pp.init()` will create the window, it has a size of (300, 300) and is
displayed at position (200, 200) on the screen.
Then the experiment is run, and the results are stored as csv-file.
So now let's take a look at `run_experiment()` function:
```python
def run_experiment():
    el = pp.EventListener()
    keys_mappings = {pg.K_q: "q", pg.K_n: "n"}
    result_key = None
    results = []
    while result_key != "q":
        display_text("press any key to start", gray)
        el.wait_for_unicode_char()
        display_text("press [ q ] to exit\npress [ n ] to continue", black)
        start_time = time.time()
        code = el.wait_for_keys(*keys_mappings)
        result_key = keys_mappings[code]
        rt = time.time() - start_time
        print(f"You pressed the {result_key} key on {rt:.3} seconds")
        results.append((result_key, rt))
    return results
```
In the first line of the function, an `EventListener` object is created, which
is needed to get user input. Since the pressed letters should be used later and
PyParadigm uses Pygame keycodes, we need a mapping from key-code to character,
which is created in the next line.
The whole thing will then run, until the subject (which means who ever executes
the paradigm) will press *q*. We then display the first text and call 
`el.wait_for_unicode_char()` which will react to any key that represents a valid
unicode character. Then, the second text is displayed and a time stamp is recorded,
which will allow us to measure a reaction time after the subject pressed *q* or
*n*. `code = el.wait_for_keys(*keys_mappings)` will then wait for the subject
to press *q* or *n* and ignore all other inputs (except for *ctrl-c*, which will
instantly quit the program), and return the code of the pressed key.
Afterwards, a reaction time is computed, and in the end the results are
returned.

This function is pretty similar to Mathias' implementation, but I used just one
function to display text, and my event handling is a little different, as there
is no need to iterate the return values of the `el` object.

Now for  the `display_text()` function:
```python
def display_text(text, bg_color):
    pp.display(pp.compose(pp.empty_surface(bg_color))(
        pp.Text(text, pp.Font(size=60), color=pp.rgba(white))
    ))
```
And this is all you need. The `pp.compose()` function will take a tree of elements,
which describes the screen you want to create and return an image. This image
is then displayed in the window using `pp.display()`. For more ambitious
examples take a look at PyParadigm's 
[documentation](https://pyparadigm.readthedocs.io).

Let's compare the implementations: mine has 36 lines of code, while the
PsychoPy version has 61 (after breaking lines that are longer than 80
characters). But there are also many lines that are
just subject to the general logic and not to the library. 
If I count the lines directly involving PyParadigm I get 9 lines, and that
includes one line only consisting of `))` and the lines for the character
mappings (which I counted because PsychoPy does not need any mapping).
The PsychoPy implementation has 28 lines that are related to PsychoPy, but I
didn't count the lines for the clock, since I didn't count them in my code
either. Now you could say, that the PsychoPy implementation could also have had
one function for drawing a screen with text, so lets count only the longer of
the two rendering functions: it has 7 lines, therefore 21 lines remain. So even
with the friendliest way of counting PyParadigm needs less than half the lines
compared to PsychoPy, and if you do things in more of a PyParadigm way, the
advantage will be even larger.   Obviously, in a very small project this does
not matter, but it definitely makes a difference if you write 500, 1200
or even more lines. 

You can find the complete source code
[here](/assets/code/pyparadigm_mini_example.py).
