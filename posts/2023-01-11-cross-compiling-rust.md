--- 
title: Rust Cross-compilation pitfalls
categories: programming
tags: Macros, Cross-Compiling
permalink: /blog/pkg-conf-cross-compiling.html
excerpt_separator: <!--more-->
---

## Basics

When you want to cross compile Rust programs, you have two options: You either
use [cross](https://github.com/cross-rs/cross), or you do it manually. The
first approach is easier, but only until you run into problems. I want to talk
about the problems and corresponding solutions that you might encounter with
the second approach.

<!--more-->

The first step to compile for another architecture is quite easy:
You install the target tool chain, e.g. `rustup target add armv7-unknown-linux-gnueabihf`
and add a corresponding linker to `.cargo/config.toml`

```toml
[target.armv7-unknown-linux-gnueabihf]
linker="arm-linux-gnueabihf-gcc"
```

Now you can already cross compile with 
`cargo build --target armv7-unknown-linux-gnueabihf`

This will give you a binary that *might* be able to run on, let's say, a
raspberry pi.

I say "might", because if you run something on a Raspberry, you probably run on
Raspbian, which typically lacks behind most other distributions in terms of
software versions. One software, that will probably cause you trouble is libc.
If your system links a version that is too new for Raspbian, you won't be able
to run your binary there. So, how do we solve this?

## Introducing Docker

Raspbian is mostly just Debian, so if we build the binary in a Debian docker
container, it will link a libc version that exists on the Raspberry (if both
are up to date). So lets create a Dockerfile (preferably in a project
sub-folder, because that reduces dockers build-context by a lot, which might
otherwise take a lot of time to send to the docker daemon).

A minimal Dockerfile would look like this:

```Dockerfile
FROM debian:bullseye

RUN apt update && apt install -y curl gcc-arm-linux-gnueabihf 

RUN mkdir /project
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID -o felix && \
    useradd -u $UID -g $GID -m felix && \
    usermod -aG sudo felix && \
    echo "felix:felix" | chpasswd

USER felix

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
#for some reason, $HOME is not /home/felix
ENV PATH=/home/felix/.cargo/bin:$PATH
RUN rustup target add armv7-unknown-linux-gnueabihf

WORKDIR /project
```

"That's a lot of Stuff for a minimal Dockerfile", you might think. Well ...
yes. Let's go through it:

The first line should be clear (unless you have no experience with Docker, in
which case you might want to learn its basics first).

The second line might already make you suspicious: "No upgrade, you say?" I hear
you ask. The thing is, those upgrades tend to cause problems, which you then
have to work around, and so far, I haven't encountered any problems from not
running the upgrade.

Then we create a new user. This has two reasons: 1. Programs that don't expect
to be run as root sometimes behave strangely when being run as root. 2. We are
going to map our project folder into the container, and ugly things will happen
due to file permissions if the UID and GID of the Docker user don't match the
ones you have on your system. Then we install rustup, and with it Rust.

Let's build the container:

```bash
# assumes the dockerfile is in a folder called docker-cross-compile
$ docker build docker-cross-compile \
   --build-arg UID=$(id -u) --build-arg GID=$(id -g) \
   -t raspi-cross-compile-image
```

and now, you could compile within the container like this:

```Dockerfile
$ docker run \
    -v "$(realpath .):/project" \
    -v "cargo-dir:/home/felix/.cargo" \
    -it --network="host" \
    raspi-cross-compile-image \
    cargo build --target armv7-unknown-linux-gnueabihf
```

We map the project folder into the `/project` folder in the container, and we use
a managed volume for `~/.cargo`, to speed up repeated compilations. Without
this, you will have to recompile all dependencies on every invocation. 
We put `-it` to make the shell interactive. In this case it's probably not
necessary, but it won't hurt, and if we want to do something interactive
later, it will work. Also the container needs internet access, to download the
build dependencies.

And now you actually have a binary that should be executable on the Raspberry
... unless you have dependencies to C-libraries, in which case you will
probably not even be able to compile your program.

## C-Dependencies and pkg-config

For many interesting things, you will actually have C-dependencies (other than
libc). A few examples include Cairo, most Guis, Openssl, audiostuff on linux,
which typically involves Alsa and maybe Pulse, etc. These Dependencies need to
be installed on the target machine, and on the host machine, with the
architecture of the target machine. How you install libraries for non-native
architectures depends on your distribution, for Debian, you have to first
enable the architecture:

```bash
dpkg --add-architecture armhf
```

and then install the required libraries for that architectures, e.g. 

```bash
apt install -y --no-install-recommends libx11-dev:armhf
```

armhf means arm with floating point hardware, and is
basically Debians name for what is called armv7-unknown-linux-gnueabihf by
rust and arm-linux-gnueabihf by gcc. Yeah, 3 names, for the same thing.
In our case, you would have to add the apropriate RUN statements to the
Dockerfile.

The tool that is mostly involved here, is pkg-config. It's a utility that tells you
where on the system a library is installed, and produces the appropriate
aruments for gcc. An example usage would be like this: 
`gcc $(pkg-config --libs --cflags cairo) main.c -o drawing_app`
It is used by most rust libraries with c-dependencies to track down the
dependencies. And it will almost certainly cause trouble when cross compiling.

pkg-config knows where the libraries are, because the libraries contain a file
called `<libname>.pc` which is installed to `/usr/lib/pkgconfig/` when the
library is installed and contains all necessary information. 
pkg-config reads the pc files in this path, and thus knows what it needs to
know. The problem that arises when cross compiling, is that the target
architecture is not contained in the library name, so pkg-config will return
the arguments that are required to compile a library for your host system.

There are three important environment variables that you can use to configure
pkg-config:

- `PKG_CONFIG_PATH`: is searched for pc files. Afterwards the normal system
  path is searched
- `PKG_CONFIG_LIBDIR`: overwrites the path, so ONLY the given location is
  searched
- `PKG_CONFIG_SYSROOT_DIR`: will be prepended to every path in PKG_CONFIG_PATH.
  It seems setting it to "" is a good idea, unless you work with a fake root
  environment

You can append a target architecture like this:
`PKG_CONFIG_PATH_armv7_unknown_linux_gnueabihf` and cargo will forward the
variable to pkg-config only for the architecture. I first had set
`PKG_CONFIG_LIBDIR` to `/usr/lib/arm-linux-gnueabihf/pkgconfig` and
`PKG_CONFIG_SYSROOT_DIR` to `""` (in the Dockerfile) because I thought, "I
don't want any native (= host architecture) libraries in my linking process
anyway". But that sent me into the next trap.

On Debian, some packages are labeled to be compatible with all architectures
(those that don't contain binaries, basically), and if you install
`x11proto-dev:armhf` it will default to the native version, and it will
not install a `.pc` file to the directory for `.pc` files for your target
platform. So I had to change `PKG_CONFIG_LIBDIR` to `PKG_CONFIG_PATH`. This
however has the consequence, that you will get linker errors because of
incompatible binary formats, instead of linker errors because of missing
libraries, if you are missing a library for your target architecture, but have
it installed for your host architecture (which is actually a common case). This
is easily solved by installing the library for the target architecture, but the
error is misleading, and you need to be aware of it.

## Other Pitfalls

Even though the information in this article will allow you to solve most
problems you will encounter when cross compiling rust programs, some libraries
just need the special treatment. For example, FLTK needs you to set the
following environment variables:

```bash
export CFLAGS="-isystem /usr/include/harfbuzz -isystem /usr/include/cairo"
export CXXFLAGS="-isystem /usr/include/harfbuzz -isystem /usr/include/cairo"
```

This kind of stuff can only be solved by carefully reading the documentation of
the linked libraries (fltk-rs has a great documentation), and/or googling the
error messages.

I hope this information helps. Thanks for reading.

