---
title: Mini Rack
date: 2025-11-28 14:35:00
tags: ["Private Cloud", "rack", "hardware", "PoE"]
category: tech
thumbnail: /static/image/rack_dark.jpg
---
*I have been procrastinating on this blog post for an astonishing 10 month, so finally here it is.*

![rack_dark](/static/image/rack_dark.jpg "Mini-rack with accessory components on a storage rack;;60")

Early this year I saw [Project MINI RACK](https://mini-rack.jeffgeerling.com/) by [Jeff Geerling](https://www.jeffgeerling.com/) and got inspired to make my own mini-rack, as an upgrade to my existing cluster.

So what is a mini-rack? Simply speaking it refers to racks built according to a 10-inch wide standard (instead of the 19-inch standard more commonly used in the industry) and more focused on small scale systems, usually for embedded hardware, homelab or household network scenarios. Not that I have any immediate need for it, but as they alway say: Increase supply and demand will follow, so here we go :)

### Components

![rack_wireframe](/static/image/rack_wireframe.png "Rack Composition (Produced with Google Slides™);;80")

Throughout the year I have built the rack to this current status and here's a reference of all the components used.
- [GeeekPi 8U Server Cabinet](https://www.amazon.com/dp/B0CSCWVTQ7?th=1), which comes with a few rack mounts, but I also get the following:
    - [1U Mini-ITX Shelf](https://www.amazon.com/dp/B0D5XNDFDZ?th=1) for the TuringPi
    - [0.5U Shelf](https://www.amazon.com/dp/B0DFHCM3YG?th=1) for the network switch
- [APC UPS BE600M1, 600VA/330 Watts](https://www.amazon.com/dp/B01FWAZEIU?th=1)
- [NETGEAR 8 Port PoE Gigabit Ethernet](https://www.amazon.com/dp/B08MBFLMDC?th=1)
- [Raspberry Pi 4B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) with:
    - [LoveRPi PoE HAT](https://www.amazon.com/dp/B07XB5PR9J?th=1)
- [TuringPi 2](https://turingpi.com/product/turing-pi-2-5/) with:
    - 3x [Raspberry Pi CM4](https://www.raspberrypi.com/products/compute-module-4/?variant=raspberry-pi-cm4001000) + [CM4 Adapter](https://turingpi.com/product/cm4-adapter/)
    - [Turing RK1](https://turingpi.com/product/turing-rk1/?attribute_ram=16+GB)
    - 24 pin PSU, heatsink, power supply, [some random 60x60x10 fan](https://www.amazon.com/dp/B0DN6LGKQB)...
- QNAP NAS which I already have long before this.
- My old 2009 Mackbook Pro.

The Geeekpi mini rack is a very nice option for hobbyists like me. It comes with a variety of sizes (4U, 8U and 10U at least) and many different types of shelves you can choose according to your need (e.g. this [0.5U DC PDU](https://www.amazon.com/GeeekPi-Rack-Mount-Distribution-Rackmate-Cabinet/dp/B0DGFZVXF6/ref=sr_1_3) seems very good for cable management), and enables you to expand and explore many different things (and potentially create new demands).

The good thing about this setup is that everything in this system (including the router) is connected to the UPS. So in case of a power outage (which is [not rare in the great Seattle area](https://www.fox13seattle.com/news/wind-rain-power-outages-puget)) my Internet and all the services will still be alive for an extended amount of time[^1]. With this setup, I'm able to scale my [k3s cluster](/blog/post/building_private_cloud_with_turing_pi/) beyond just the nodes on Turing Pi. It now include an extra RPi 4B I had lying around, and also my ancient Macbook Pro (more on that see [this post](/blog/post/Reviving-My-Old-Macbook-Pro/)).

[^1]: As for exactly how long time, the UPS providers are all very much cryptic about it. e.g. what does 600VA/330W mean? Just tell me a number with energy units (J or kWH) and I can calculate the time from my average demand.

This whole setup (as you can tell from the photo) is in my storage closet which is rather small. So I 3D printed a simple wall-mount for the router [^2] and after mounting I can enjoy the accessibility of the cluster right at the door, and also pull the whole storage rack (together with all the hardware on it) all the way out and make way for any thing I need to do in the storage closet.

[^2]: The 3D model is from [here](https://makerworld.com/en/models/2004911-xfinity-router-wall-mount?from=search)

### What's next?

I might want to explore more PoE options since it's cool and appeals to the desire for simplicity. The NETGEAR switch I have is the smallest one that supports PoE. Although I have everything jacked into it, only the RPi 4B is utilizing PoE. It's a shame that TuringPi 2 doesn't support PoE (maybe it needs too much power?) and I still need to keep the power cable from the back. A fun thing to do is to get WiFi APs in other rooms where we have bad signal, and use PoE to power through the ethernet alone, although it's not related to mini-rack anymore.

Another thing I've been thinking is to make a DIY NAS as a replacement for my old (3+ years old) QNAP NAS. I watched a few videos about DIY NAS [^3] and found in the comment that [CM3588](https://www.friendlyelec.com/index.php?route=product/product&product_id=294) might be a good thing to start trying. It would fit nicely in a 1U space on the mini-rack, instead of where the QNAP NAS is at (taking up about 4U and not properly attached). The only reason I haven't made up my mind is that NVME drives are expensive, and I could also just buy another 3 RK1s and use the Turing Pi as a NAS, since it also has 4 NVME slots on the back (which might be more expensive).

[^3]: Some of Jeff Geerling's videos: [NucBox G9](https://www.youtube.com/watch?v=M_Ft8OAPQ3g), [Fixing NucBox G9](https://www.youtube.com/watch?v=TlsIuA8rBRg&t=7s), [TrueNAS on Raspberry Pi](https://www.youtube.com/watch?v=XvaXemGDSpk&t=196s)

[![nvidia_meme](/static/image/nvidia_meme.webp "Randomly inserted NVIDIA meme from Reddit;;50")](https://www.reddit.com/r/pcmasterrace/comments/17xg8el/i_felt_this_meme_was_more_true_with_nvidia_than/)

Finally I want to have a local environment that's powerful enough to run full-sized opensource LLM inference (e.g. [Qwen3-235B-A22B](https://qwenlm.github.io/blog/qwen3/), [gpt-oss-120b](https://openai.com/index/introducing-gpt-oss/)). Some possible candidates include:
- [NVIDIA DGX Spark](https://nvdam.widen.net/s/tlzm8smqjx/workstation-datasheet-dgx-spark-gtc25-spring-nvidia-us-3716899-web) ($3999, 128G unified memory, 301G/s memory bandwidth ([ref](https://www.techpowerup.com/342321/nvidia-dgx-spark-reportedly-runs-at-half-the-power-and-performance)), 31 TFLOPS for FP32 ([ref](https://www.techpowerup.com/342321/nvidia-dgx-spark-reportedly-runs-at-half-the-power-and-performance)), 5.9in x 5.9in dimensions)
- [Similar hardwares from other manufacturers equipped with NVIDIA Blackwell](https://marketplace.nvidia.com/en-us/enterprise/personal-ai-supercomputers/?limit=15)
- [Apple Mac Studio](https://www.apple.com/mac-studio/specs/), 7.7in x 7.7in dimensions
    - M3 Ultra chip: at the same price point ($3999) has 96G unified memory, 819G/s memory bandwidth, 28.2 TFLOPS for FP23 ([ref](https://www.reddit.com/r/macgaming/comments/1m9517i/m_chip_and_gpu_tflops/))
    - M3 Max chip: $1999, 36G unified memory, 410G/s memory bandwidth, 16.3 TFLOPS for FP32 ([ref](https://www.reddit.com/r/macgaming/comments/1m9517i/m_chip_and_gpu_tflops/))
    - Other combinations of chip/memory is also available.
- [Apple Mac Mini](https://www.apple.com/mac-mini/specs/) with M4 Pro: $1399, 24G unified memory, 273G/s memory bandwidth, 9.3 TFLOPS for FP32 ([ref](https://www.reddit.com/r/macgaming/comments/1m9517i/m_chip_and_gpu_tflops/)), 5.0in x 5.0in dimensions
- Cheaper and less powerful options like [NVIDIA Jetson Orin series](https://marketplace.nvidia.com/en-us/enterprise/robotics-edge/?productLine=robotics-edge&locale=en-us&category=developer_kit&page=1&limit=15)

I have always believed in the potential of OSS AI models and their ability to be self-hosted, and it's unlikely to be dominated by NVIDIA. All the above choices could fit nicely in my mini-rack, but as a long-time Apple user I might stop buying new Macbook and finally get a Mac Studio, who knows.


