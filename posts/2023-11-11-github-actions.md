--- 
title: GitHub Actions and CI-Pipelines are a Problem
categories: devops
excerpt_separator: <!--more-->
---

## The Problem

You push (or better, merge) to master, and the deployment happens automagically. No
further work required. That's the promise of GitHub-Actions (GHA), and probably
every other CI service provider.

However, things are not as shiny as they seem at first glance. There are many
problems with the approach that GHA and co. use. Some are addressable by more
disciplined usage behavior[^1], but others are not.

<!--more-->

My first and foremost problem with them is: you cannot run them locally. There
are some projects, that attempt to enable you to do that, e.g. 
[act](https://github.com/nektos/act), but they are very limited. And that is because
of my second-biggest issue with GHA: the runner is closed source.

Hosting a git repo is hardly more than providing a file system and SSH access.
The actual mechanism they use to keep you on their platform is the CI-pipelines
(and maybe the issue system and wiki, but less so). Half a year ago, I started
porting my teams Azure-Devops pipelines to GHA, investing ~1 day per week. AND I
AM STILL NOT DONE.

The fact that you have to push a commit to the repo to test a change, and then 
wait for a runner delays everything indefinitely, and makes iterating really
painful.

Additionally, writing pipelines in YAML is just painful. It's super verbose,
and you have a lot of "code" duplication. Quite soon in the process I invested
3 days to write a small DSL that compiles to GHA[^2]. This already took care
of the code duplication, and I integrated [actionlint](https://github.com/
rhysd/actionlint) to reduce the number of pushes I'd need. Sadly, actionlint
catches a similar percentage of your bugs like a C-compiler (which is not very
high). Originally, that DSL hat two backends: One to compile to GHA, and one
to run stuff locally. The second one is not in use anymore. Why? Because there
are tons of actions[^3] that you want to use, e.g. for terraform. To use those
locally, I'd have to reimplement the complete GHA runner, or at least, locally
reimplement all the actions I want to use.

Many of those actions are written by 3rd parties, not by GitHub/Microsoft,
but it benefits them a lot by strengthening their position against their
competition. It's a network effect. And it's bad for everyone except MS. I'm
only somewhat knowledgeable in Azure-Devops and GitHub actions (much to my own
dismay), but I assume that more or less every CI provider does its own thing,
and there is a lot of duplicated efforts. 

## An attempt at a solution

The base idea is the same for every CI provider: You define a "workflow" that
runs some scripts. Some of which run in parallel, some of which require others
to finish first. They need access to a git repository, and they might have
to interact with it. Defining a language to run scripts in parallel with some
constraints is actually quite easy if you just pass the script to an existing
interpreter and let the language mainly deal with the constraints around order
and parallelism (and code reuse). However, if this is then just a new solution,
little is gained. So it would be necessary to have different "generators" that
generate small wrappers for your CI-provider of choice that call the actual
definitions, and maybe to call a subset of functionality that is shared by
more or less everyone (e.g. creating issues, merging a branch, etc.). If people
who currently write "plugins" for different CI providers instead focus on this
hypothetical language, we would end up with an ecosystem of CI tools that can run
everywhere, including your PC. I'm thinking of something like this:

![Graph of the hypothetical System](/assets/img/common_action_runtime.svg)

And yes, I'm aware of [XKCD #927](https://xkcd.com/927/), but It's actually not the same
as a CI-Provider, and I'm not aware of a similar project. Corrections are welcome.
And while I'd love to work on this, I don't see myself having enough free time in the
foreseeable future to do this. So I hope, someone feels inspired.


[^1]: And let's be honest, that means they are basically not addressable
[^2]: I'm sorry, but it's not publicly available, it's in my company's repository,
      and since I hacked that together super quickly, I'm honestly quite happy that
      the code is not publicly available.
[^3]: I think some disambiguation is in order: The whole thing is advertised as
      "GitHub Actions", however doing something is defined in a "workflow", and
      workflows can be packaged, parameterized, and reused in other workflows, and this
      is then called an "action" again.
