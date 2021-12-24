---
title: Work with ARM
date: 2021-12-24 11:46:00
tags: ["Docker", "Architecture", "devops"]
category: tech
---
After I got back to the States in mid November, I just couldn't wait to get myself a latest MBP, given my previous one is over 5 years old and sometimes refuses to charge. And of course, I just have to have the one with Apple M1 Pro silicon. Hence start my journey of [working with ARM](/post/working-with-arm/) began.

For those who is not familiar with computer architectures, specifically different instruction sets there is, here is a [simple explainer](https://www.section.io/engineering-education/arm-x86/):

> There are two most dominant computer architectures: x86 and arm. x86 architecture is based on CISC (Complex Instruction Set Computing), whose standard is setup by AMD in 1999. x86 architecture has a huge amount of different instructions, which as a result has longer and more complex instructions, and usually has worse power efficiency. On the contrary, arm architecture is based on RISC (Reduced Instruction Set Computing) proposed by ARM (the company). It has only around 50 instructions and usually considered more power effective and friendly for modification and customization.

### Local Environment

Considering the difference of CPU architecture and the fact that I gradually made a mess with my old MBP's file system, I didn't use the (suspiciously convenient) [Apple Time Machine](https://support.apple.com/en-us/HT201250) to directly migrate my system to the new hardware, and decided to setup from fresh.

The local environment setup process was pretty smooth. I transferred my important stuff (mostly code of my side projects) through ssh; downloaded and installed softwares I needed for my daily usage; and also tried something new such as [oh-my-zsh](https://ohmyz.sh/) for a more powerful and generic `zsh` customization (I might be the last one to realise this, but Apple somehow changed default shell of Terminal from `bash` to `zsh` from OS X one or two versions ago, which fucked up my previous customization setups a little.); as a Python programmer, I also (finally) adopted [conda](https://docs.conda.io/en/latest/) to setup my Python environments, since they seems to finally getting their shits together. So apparently after over a year of Apple M1 silicon's debut, the software eco-system is catching up pretty well.

### Devops with Docker

Here comes the harder part: most of my side projects works with a container as the devops environment, which (of course) are all built over the x86 arch (specifically x86_64, but we'll get to that later). I did try to run the docker image I built earlier, which does started with a unsettling warning:

```bash
$ docker run -it fzxu/nn-amd64 /bin/bash
# WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested
root@6dec62b3afc0:/nn#
```

And it doesn't really work well after further testing. So the only logical choice left for me is to build same image (or images for the same purpose) towards different target architectures.

#### Problem with pip

Ideally if you basically uses dependency/package managers (e.g. apt, pip, npm) to install things in Dockerfile, you would expect to use the same Dockerfile to build images with different target archs, and hopefully the package managers will automatically deal with the archs issue for you.

But I run into a strange problem when installing `notebook` with `pip`, which I'm not sure if it's specifically because of Apple silicon or it's a general arm issue:

```bash
command 'aarch64-linux-gnu-gcc' failed with exit status 1
```

I struggled for a whole day on this, and eventually rewrite my Dockerfile to use [`miniconda`](https://docs.conda.io/en/latest/miniconda.html) as a replacement for `pip`. While awkward as it is, as I'm trying to reproduce this error as I'm writing this blog, this issue seems to be mitigated and I don't know what my reactions should be now.

#### General solution with `docker manifest`

On the other hand, if your docker image depend on some particular arch sensitive binary (e.g. my [bazel installation](https://docs.bazel.build/versions/main/install-ubuntu.html#install-on-ubuntu)), you'll need to do something clever to either render in the arch info or just use different Dockerfiles. After that, you should be able to build images for different archs __under different tag__.

But what I wanted is to host images for different archs under the same docker image tag and be able to serve automatically according to host platform, something like [this](https://hub.docker.com/_/ubuntu?tab=tags) (note that it has images for different archs under same tag).

After some investigation, I figured that something called [manifest](https://docs.docker.com/engine/reference/commandline/manifest/) is needed to achieve this behavior with docker registries, and it is (even) still experimental for docker clients. Tutorials on the easiest way to do it is somehow hard to dig on the web (what I found was either too _old_ for a still experimental feature or doing something else), so here's how I did it for your reference:

1. Build different images for different archs under different image name or tag, you should be able use docker's cross-platform build feature with `buildx`

```bash
docker buildx build --platform linux/amd64 -t fzxu/blog:x86 -f Dockerfile_x86 .
docker buildx build --platform linux/arm64 -t fzxu/blog:arm -f Dockerfile_arm .
```

2. Push both images onto a registry in order to generate local manifest file

```bash
docker push fzxu/blog:x86
docker push fzxu/blog:arm
```

3. Use `docker manifest inspect` to check their manifests

```bash
docker manifest inspect fzxu/blog:x86
docker manifest inspect fzxu/blog:arm

```

4. Use `docker manifest create` to associate the images to a single tag (empty for `latest`)
```bash
docker manifest create fzxu/blog fzxu/blog:x86 fzxu/blog:arm
```

5. Use `docker manifest push` to push it to registry

```bash
docker manifest push fzxu/blog
```

Finally you'll get the multi-arch support under a single tag like [this](https://hub.docker.com/r/fzxu/blog/tags). I spent quite some time on building multi-arch support for my docker images that I'm using (github ci server, v2ray server, etc.). The reason for this effort other than my shiny new MBP is that I want to start using AWS EC2 spot t4g instances for a (much) [better price](https://aws.amazon.com/ec2/spot/pricing/), and t4g (`g` for [Graviton](https://aws.amazon.com/ec2/graviton/)) is based on arm arch. I'll (probably) have another blog to talk about my cloud solution visions since it's off topic for this post, but that's it for today and thanks for reading.
