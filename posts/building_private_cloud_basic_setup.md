---
title: Building Private Cloud: Basic Setup
date: 2024-01-29 06:57:47
tags: ["k8s", "k3s", "infra", "Turing Pi", "Raspberry Pi", "Private Cloud"]
category: tech
---

As mentioned in [a previous post](/blog/post/building_private_cloud_with_turing_pi/), I have acquired enough parts that's needed for me to start working on building a private cloud (or homelab). This series of blog posts is to record my experience of building this hardware/software system, and hopefully serve as a guide or pointer to anyone trying to do similar things.

<img src="/static/image/private_cloud.jpg" style="width: 100%"/>

*Finished hardware setup and deployment, only software level work left*

#### Hardware
I have to admit that I underestimated the effort that would go into preparing the hardware needed for the setup. Especially when it's your first time, and you're not sure what is needed. So here's a list of hardwares I'm currently using:

- [Turing Pi 2](https://turingpi.com/product/turing-pi-2-5/)
    - [Pico PSU](https://turingpi.com/product/pico-psu/)
- [Raspberry Pi 4 Compute module 4G lite](https://www.raspberrypi.com/products/compute-module-4/?variant=raspberry-pi-cm4004000) x3
    - [Waveshare RPi CM4 Heatsink](https://www.amazon.com/gp/product/B094ZSZCSF/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) x3
    - [Turing CM4 Adapter](https://turingpi.com/product/cm4-adapter/) x3
    - [Sandisk mini SD card](https://www.amazon.com/dp/B08J4HJ98L?ref=ppx_yo2ov_dt_b_product_details&th=1) 32g x2, 512G x1
- [Turing RK1 16G](https://turingpi.com/product/turing-rk1/?attribute_ram=16+GB)
    - [RK1 Heatsink](https://turingpi.com/product/rk1-heatsink/)
- Random [mini-ITX case](https://www.amazon.com/dp/B07GYL5SW5?psc=1&ref=ppx_yo2ov_dt_b_product_details) from Amazon
- Some [2-pin fan](https://www.amazon.com/dp/B08135WS3H?psc=1&ref=ppx_yo2ov_dt_b_product_details) that fits in the case
- [12V DC Power Supply](https://www.amazon.com/dp/B01GEA8PQA?psc=1&ref=ppx_yo2ov_dt_b_product_details)
- ZHITAI TiPlus5000 NVME M.2 SSD 2T
- 3D printed IO-shield (instead of [this](https://turingpi.com/product/io-shield/)), you can modify from [this one](https://www.thingiverse.com/thing:5811444/files) based on your setup and print your own.

Important parts are the motherboard (Turing Pi 2) and the CM4 and RK1 compute modules. According to [Turing's documentation](https://docs.turingpi.com/docs/turing-pi2-specs-and-io-ports-case-and-cooling) and some discussion, some basic heatsink + any sort of active cooling should be good enough for most cases. Casing and fan choice depend on your design and aesthetics. But better thermal condition and planning is needed if you plan to do some crazy stuff.

Storage hardware is important and should be planned out, because reliable and performant storage solution is necessary if you intend to do anything serious with the cluster. Check Turing's documentation, specifically [specs and i/o ports](https://docs.turingpi.com/docs/turing-pi2-specs-and-io-ports) to get a clear idea of the i/o availability and connectivity, and plan on what storage you want based on your purpose.

I'm getting a 2T M.2 NVME to work with the RK1, which is a solution that will work with high probability. Turing Pi 2 has front-side mini-PCIe for node 1,2, but compatibility of PCIe hardwares with rpi is very [debatable](https://pipci.jeffgeerling.com/) and I spent quite some time struggling on this (I'll hopefully cover in following posts).

#### Operating Systems

As mentioned previously, I have 3 rpi CM4 and 1 RK1 in my setup, with the following OS installed:
- Node 1: rpi CM4 running [Raspberry Pi OS with desktop](https://www.raspberrypi.com/software/operating-systems/)
- Node 2,3: rpi CM4 running [Raspberry Pi OS Lite](https://www.raspberrypi.com/software/operating-systems/)
- Node 4: RK1 running [Ubuntu 22.04 LTS Server based on the BSP Linux 5.10](https://firmware.turingpi.com/turing-rk1/ubuntu_22.04_rockchip_linux/v1.32/) which seems to be a customized kernel for their hardware.

Following documentations ([rpi CM4](https://docs.turingpi.com/docs/raspberry-pi-cm4-flashing-os), [RK1](https://docs.turingpi.com/docs/turing-rk1-flashing-os)), there's multiple ways to flash OS into aforementioned hardware. For rpi CM4 I installed the [Raspberry Pi Imager](https://downloads.raspberrypi.org/imager/imager_latest.dmg) on my Macbook and it worked pretty well including pre-setting username/password and authorized_keys for very convenient ssh connection. For RK1 I'm just flashing it [with BMC](https://docs.turingpi.com/docs/turing-rk1-flashing-os#flashing-using-turing-pi-2-bmc) because I don't have a USB A-A cable which is needed for the other method.

There are other OS choices for rpi e.g. [dietPi](https://dietpi.com/) or a Ubuntu server version, which might come in handy for some specific use case.

Answers to some possible questions:
- *Why rpi OS with desktop for Node 1?* Because only Node 1 has exposed HDMI port, which becomes very handy when you have problem ssh to the server, or debugging kernel issue while starting up.
- *why RK1 on Node 4?* RK1 is the most powerful node I have, but if put on Node 1, its heat will directly blow to back of Node 2, which is very bad thermal condition. Only Node 4 make sense due to the parallel layout on the motherboard. I know, it's a stupid but interesting decision to make.

#### Virtualization

I know, this word is too big for a personal project. But it's just fun when you tell your friend that you're "practicing virtualization technology" in your garage. Jokes aside, for private cloud there's usually 2 choices, or 2 levels of abstraction when we talk about virtualization:
- Hardware level virtualization: An "old-fashioned" approach. Usually meaning you're creating virtual machines on your hosts. Typical technology would be running KVM using [Proxmox](https://www.proxmox.com/en/), or running VMware hypervisor.
- OS level virtualization: More modern solution, providing best level of isolation and efficiency with least hassle. Typical example would be using [Docker](https://docs.docker.com/) (with [Docker Compose](https://docs.docker.com/compose/) or [Docker Swarm](https://docs.docker.com/engine/swarm/)), or running a [Kubernetes](https://kubernetes.io/) cluster.

The solution I chose is [K3s](https://k3s.io/), which is a light-weight kubernetes distribution specifically designed for embedded use cases. It comes with lots of useful components already installed e.g. Traefik ingress controller and CoreDNS. Here's the steps of setting up k3s on the cluster (following [k3s doc](https://docs.k3s.io/quick-start)).

- Run the following on all machines if `curl` is not installed.

```Shell
sudo apt update && sudo apt install -y curl
```
- For rpi OS, add `cgroup_memory=1 cgroup_enable=memory` to `/boot/cmdline.txt`, before `rootwait`. OS level virtualization needs the host OS to have cgroup setup for resource isolation. For Ubuntu it should be already done.
- Run the following on the master node (for me it's node 1), k3s service will be installed along with useful CLIs, and service will be automatically started:

```Shell
curl -sfL https://get.k3s.io | sh -
```
- Run the following on the agent nodes (node 2,3,4), substitute `myserver` and `mynodetoken` with your server IP and content from `/var/lib/rancher/k3s/server/node-token` on master node. k3s-agent will be be installed and automatically started and registered to master:

```Shell
curl -sfL https://get.k3s.io | K3S_URL=https://myserver:6443 K3S_TOKEN=mynodetoken sh -
```

After this the k3s cluster should be setup perfectly, and you can verify this by running `kubectl get nodes` on the master node:

```Shell
$ kubectl get nodes
NAME       STATUS   ROLES                  AGE    VERSION
rpicm4n1   Ready    control-plane,master   41d    v1.28.4+k3s2
rpicm4n2   Ready    <none>                 6d1h   v1.28.5+k3s1
rpicm4n3   Ready    <none>                 26d    v1.28.5+k3s1
rk1        Ready    <none>                 6d     v1.28.5+k3s1
```

After deployment, you should setup kubectl on your own computer for remote control of the cluster.

#### Conclusion

I should probably stop here because it's already a long post. But now you can play around the cluster and try different stuff (and encounter tons of blockers and give up).

I will cover more detailed content in following posts, including how to utilize Traefik ingress controller, how to setup different services e.g. regular web server, DNS server (utilizing CoreDNS), network proxy service, and much more.

Hope you enjoy :)

*For the list of the series of blog posts about building private cloud, click [here](/blog/post/building_private_cloud_with_turing_pi/).*
