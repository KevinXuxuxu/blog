---
title: Building Private Cloud with Turing Pi 2
date: 2024-01-09 18:55:48
tags: ["k8s", "k3s", "infra", "Turing Pi", "Raspberry Pi", "Private Cloud"]
category: tech
thumbnail: /static/image/turingpi_official.webp
---

![turingpi_official](/static/image/turingpi_official.webp "Turing Pi 2 Board;;70")

I was one of the backers when [Turing Pi 2](https://turingpi.com/product/turing-pi-2/) was on kickstarter, and received the stuff around April 2023. But at that time there wasn't any available [rpi cm4](https://www.raspberrypi.com/products/compute-module-4/) for me to buy, so the plan was postponed util just last Thanksgiving. I got 4 rpi cm4 4G lite version, and finally started to build a private cloud out of these.

The plan was simple, boot everything up, install some container orchestration (most likely [k3s](https://k3s.io)) and start to move my web services (probably also my GF's) to local. Just going full "self-hosted". But later I realized that there are much more details that I need to learn or deal with, including but not limited to:
- Casing and thermals. Turing Pi 2 is supposed to fit in any mini-ITX case, but I have some personal preference and also cooling is another thing to worry about.
- Supporting hardwares and compatibility. I will need additional storage (preferably performant ones) to go with the cluster but hardware of specific form factor needs sourcing, and there's some specifications about the Turing Pi 2 board IO connectivity and rpi cm4 compatibility issues that needs some attention.
- Software to learn and try. Although I have quite some experience working with k8s from work, setting up k3s in a more embedded environment with all the networking, security and resource constraint to deal with is going to be a challenge to me.
- The most underrated challenge is going to be finding stuff to achieve with the setup that actually make sense and meaningful. I have a handful of services that I could try to run on the cluster, but that's probably not the best idea for all of them.

My current progress is that I have a cluster with 4 rpi cm4 setup with k3s and ready to run some of my workload, but the casing and cooling is not resolved so not in a long-running state. I will update to this post (or link to new posts) about my previous setups and lessons learnt, and also new progress I would make in the future. Wish me luck!

*2024/01/29 Update:*

I have (finally) started writing the series, check [here](/blog/tag/Private%20Cloud/) for a running list of posts :)
