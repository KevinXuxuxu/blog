---
title: Reviving My Old Macbook Pro
date: 2025-06-14 10:34:56
tags: ["Apple", "MacBookPro", "macOS", "Ubuntu", "Private Cloud", "Architecture"]
category: tech
thumbnail: /static/image/old_macbook_inside.png
---

![old_macbook_back](/static/image/old_macbook_back.jpg "Backside of my old Macbook Pro;;60")

Recently I got my hands on one of my old Macbook Pro from college time. It was a 2009 model high-end 15-inch Macbook Pro, which is supposed to be among [the last models of Macbook Pro that's still user repairable and upgradable](https://www.quora.com/What-is-the-last-upgradable-15-MacBook-Pro-model-number-where-I-can-swap-RAM-and-HD). Which is exactly what I did back in my sophomore year: The machine already has 16G RAM which is more than enough at the time, but I did remove the CD drive (yes, they come with CD drive at the time), moved the original HDD to where the CD drive was, and installed a SSD where the HDD was. It was really fun at the time, and since it has an Intel x86 CPU, I want to revive it now and (possibly) use it in my [cluster](/blog/post/building_private_cloud_with_turing_pi/).

![old_macbook_proc](/static/image/old_macbook_proc.png "Inside of Macbook Pro Model A1286 (source: iFixit) with my repairs and upgrades")

#### (Minor) Repair

Before I took it, it was being used as a movie player for my parents, sitting on the TV stand, streaming videos from the NAS I installed for them. Most of the hardware and the system works ok-ish, but the UI sometimes feels sluggish and less responsive, and the backside was bulgy where the battery was at, which is a more serious issue.

Luckily this model lived up to its reputation, and it was fairly easy to find a reliable [shop on Taobao](https://item.taobao.com/item.htm?_u=f22vneqg59eb&id=684035837392&spm=a1z09.2.0.0.60742e8dvSjI9r) who sells replacement batteries from the original manufacturer at a reasonable price[^1]. And replacement was easy following the [MacBook Pro 15" Unibody Mid 2010 Battery Replacement tutorial from iFixit](https://www.ifixit.com/Guide/MacBook+Pro+15-Inch+Unibody+Mid+2010+Battery+Replacement/3024). 

[^1]: You can also find decent ones from [AliExpress](https://www.aliexpress.us/w/wholesale-A1286-battery.html?spm=a2g0o.productlist.search.0) if you're e.g. in the US.

#### New OS and Drivers

The next step is to get rid of the old MacOS and install some lightweight linux. It took me an afternoon to go through my old files on the system and backup meaningful files to my NAS, which is a painful thing to do because everything has so much memory attached XD.

After some consideration, I still went with [Ubuntu 24.04 Desktop](https://ubuntu.com/download/desktop) just because I'm going to add it to my cluster and Ubuntu is something I already worked with. After downloading the ISO (5.9G? Why?) I used [balenaEtcher](https://etcher.balena.io/) to create an installing medium with a spare usb drive, which is pretty straight forward.

Next is to install Ubuntu with our prepared install medium. Plugin the usb drive, start the machine while pressing Alt[^2], will get you into the boot page. Make sure there isn't any other usb plugged on the machine[^3], and you should see a yellow disk named "EFI Boot". That is the usb installer and we should boot from it. After that just choose "Try or Install Ubuntu" and select the correct hard drive to wipe and install the system, and follow the instructions from there.

[^2]: This works for the older firmware that comes with earlier models (2009-2012) of Macbook. For later versions the procedure might be different.

[^3]: I did try to install Ubuntu from a Logitech wireless mouse receiver, and no, it didn't work.

Ubuntu Desktop works smoothly on Macbook Pro! The display compatibility is perfect and all the hardware drivers seem to be working except for Wifi. No need to fret as I have seen and dealt with this many times. Luckily the ethernet works out of the box, so I can plug it with a network cable, and install necessary wifi firmware from apt:
- Check for the wireless network hardware model, the important part is at the end.
```shell
$ lspci -nn -d 14e4:
02:00.0 Network controller [0280]: Broadcom Inc. and subsidiaries BCM4331 802.11a/b/g/n [14e4:4331] (rev 02)
```
- Check the corresponding firmware package name from [Broadcom Wireless Table section in this answer](https://askubuntu.com/questions/55868/installing-broadcom-wireless-drivers), and install if with `apt`
```shell
$ sudo apt update
$ sudo apt install firmware-b43-installer linux-firmware 
```
- Restart machine.

Although I don't really need Wifi if I'm running it as a cluster node, it's still easier that I don't have to be pinned around my router to work on it.

#### On to the Cluster!

Due to certain design choices and limitations (as documented sparsely around [a few posts in the series](http://localhost:8000/blog/tag/Private%20Cloud/)), there're some non-trivial steps to setup a new node. I have done this quite a few times, but it would still be nice to keep the setup routine spelled out here for future references.
- Setup nfs mount for the shared storage solution following instructions [here](/blog/post/building_private_cloud_storage_solution/#mount_nfs_on_clients)
- Add local container registry service (e.g. `cr.local.example.com`) to `/etc/hosts` for local image pulling[^4].
- Follow [k3s quick start](https://docs.k3s.io/quick-start#install-script) to add the current machine as an additional agent node.
- For some unknown reason (probably some special configuration k3s did to the host system), the machine's DNS resolution will start to fail. Usually I need to manually set a valid nameserver in `/etc/resolv.conf` (e.g. `nameserver 8.8.8.8` Google official DNS) for it to work at the moment. The file will be overwrite back to `127.0.0.53` later but everything seems to work just fine going forward.

[^4]: This used to be unnecessary because of the [local DNS](/blog/post/building_private_cloud_local_dns/) setup, but that turns out to be unstable for some reason. Will look into that later XD

Now that my cluster have my old Macbook connected, it has officially become what they call a system with [Heterogeneous Architecture](https://en.wikipedia.org/wiki/Heterogeneous_System_Architecture), i.e. distributed system with multiple different compute architectures (x86_64 or amd64, and arm64) to support.

This immediately brings a problem. I have a [promtail](https://grafana.com/docs/loki/latest/send-data/promtail/) daemonset deployed in the cluster and the image is from my own container registry. Before now all my environment has been Arm based, so the promtail image is only built for Arm. As a result, the promtail pod on macbook starts to crash-loop with this (not so informative) error message[^5]:

```text
exec /usr/bin/sh: exec format error
```

This means that the image arch is different from the host arch. Luckily just like Docker Hub, my container registry ([CNCF Distribution Registry](https://distribution.github.io/distribution/)) also supports hosting multi-arch images out-of-the-box. All I need is to find a way to port the official multi-arch image from Docker Hub to my registry.

Thankfully we have [skopeo](https://github.com/containers/skopeo), a commandline tool for various operations with container images and container image registries. For MacOS just do `brew install skopeo` and it can directly copy image from one registry to another without storing to local file system and with multi-arch natively supported:

```shell
skopeo copy --all \
  docker://docker.io/grafana/promtail:3.3.2 \
  docker://cr.local.example.com:5000/grafana/promtail:3.3.2
```

[^5]: This also happened later when my postgresql backup cronjob choose to run on the macbook.

After that, the image on my registry will be multi-arch, and k3s automatically chooses the image version with the correct arch depending on the target host arch, voila!

Ok so this solves the case when I'm just porting and using an official image with existing multi-arch support, which is the majority of the case for me. But for the cases where I build my own image, there's 2 choices:
- find a way to build/cross-build image versions for different archs and compile them together (doable but exhausting)
- restrict k3s deployment to only provision pods on hosts with specific arch (arm64) (lazy but much easier)

And you know which one I would choose XD
