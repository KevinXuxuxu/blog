---
title: Self-hosting VPN
date: 2024-07-21 20:46:52
tags: ["Private Cloud", "VPN", "V2Ray", "GFW", "Network"]
category: tech
---

> TL;DR This blog is mainly talking about self-hosting proxy to visit blocked sites and services by GFW from mainland China, **not** talking about general network proxy and VPN concept. It's also mostly focused on overall technology and server side setups. For client side, please check [footnote 3](/blog/post/Self-hosting-VPN/#fn-3) for more information.

From my earliest days in US I have had the need of a 梯子[^1] against the [GFW](https://en.wikipedia.org/wiki/Great_Firewall), as I started to heavily rely on blocked services like Gmail, Google Map, Github etc. With the help from my collage roommate, I set up a simple solution with [Shadowsocks](https://en.wikipedia.org/wiki/Shadowsocks) on an AWS EC2 instance and wrote quite a detailed blog about it over 9 years ago.

[^1]: "ladder" in Chinese, cryptology for VPN service against GFW.

At the moment it was very popular topic among Chinese students abroad about which provider (or 机场[^2]) is the most stable and fast, or which tech and cloud provider combination is the cheapest solution (if you're a *NeRd* doing self-hosting). There were numerous blogs and communities about that and my solution was nowhere near novel or most economical: it used naked IP address with no traffic camouflage and need to replace VM and IP every few months. With the latest development of both GFW and VPN technology, I have been updating my solution over the past years and I believe it warrants a new blog.

[^2]: "airport" in Chinese, for-profit service providing abroad servers over open protocols like shadowsocks.

#### V2Ray

The core technology of my current solution is [V2Ray](https://www.v2fly.org/guide/start.html) under the [Project V](https://www.v2ray.com/index.html), which is a set of network protocols and their implementations. [V2Fly](https://github.com/v2fly) is the community-driven edition of V2Ray with some possibly messy history that I'm not clear about. [V2Fly official site](https://www.v2fly.org/guide/start.html) has some basic setup instructions, but I mostly refer to the Chinese version of [V2Ray Beginner's Guide](https://guide.v2fly.org/en_US/) as it covers not only the basics, but also into many possible detailed and complex solutions, one of which is the foundation of my current solution.

The doc has a comprehensive section for [FAQ](https://guide.v2fly.org/en_US/#frequent-questions-q-a) about V2Ray, but I'll just highlight a few points here:
- V2Ray takes a symmetric design, i.e. the client and server runs same software with same architecture, the functionality is fully determined by the configuration used.
- VMess protocol is the core protocol used in V2Ray across GFW, it only takes UUID for authentication, which is far more secure compare to passwords.
- V2Ray is able to directly run on most OS, but for common use cases it's more convenient to get a wrapped client.[^7]

[^7]: I've been using [Shadowrocket](https://www.shadowrocket.vip/) for most of my devices. It costs $3 for a one-time purchase and can be used across all Apple environments. For Windows/Android client consider some options [here](https://www.v2fly.org/en_US/awesome/tools.html#third-party-gui-clients) in the official docs. For linux you can always just run v2fly-core directly or in docker as mentioned later in this post.

The simplest possible configuration is like the following:

![basic_v2ray](/static/image/basic_v2ray.png "Basic setup")

Some key points to notice:
- V2Ray configuration mainly consists of 2 sections: `inbounds` and `outbounds`. In this basic example, [client side config](https://guide.v2fly.org/en_US/basics/vmess.html#client-side-configuration) has inbound [SOCKS](https://en.wikipedia.org/wiki/SOCKS) request from `localhost:1080` and outbound VMess request to `10.12.23.34:16823`, while [server side config](https://guide.v2fly.org/en_US/basics/vmess.html#server-side-configuration) has inbound VMess request on port `16823` and outbound to anywhere (`freedom`).
- The reason there's an extra layer on client side (the "system proxy" in the graph) is because most OS have a system level network manager to control overall proxy behavior[^3] and it usually support SOCKS protocol. This makes V2Ray works properly with client-side environment and unify all types of request under one protocol for proxy.
- The connection across GFW is on naked IP address, over VMess protocol and on an uncommon port (16823). Although VMess encrypts the data, all the public information easily makes it suspicious to GFW and automatically gets the IP address blocked, not even mentioning the more and more intelligent GFW technologies. This is very far from a stable solution.

[^3]: e.g. For MacOS and iOS, check Proxies config in the details of your connecting network.

#### WebSocket + TLS + Web

Although GFW has become very advanced and intelligent over the past years, overall it still works on a blacklist logic instead of whitelist. For most of the foreign sites and services (especially the new ones) it allows the traffic by default, monitors and runs analysis over the traffic, and blocks it (programmatically or manually) only when it decides that the site is no good.[^4]

Given that, our approach is to cover the traffic in a way that it's indistinguishable from a normal and random website minding its own business. We will be safe as long as it's not picked out by the automatic analysis and block procedure.

[^4]: This is of course an over simplification of how GFW works. I'm sure it has partial whitelist mechanism (default block) on some IP range or service provider, but that's out of scope of this post.

The solution is covered in [this section](https://guide.v2fly.org/en_US/advanced/wss_and_web.html#configuration-example) of V2Ray Beginner's Guide with all the needed configs, and it looks like this:

![tls_v2ray](/static/image/tls_v2ray.png "WebSocket + TLS + Web")

For the most important connection across GFW, client side sends the VMess request wrapped in WebSocket and TLS. With a properly configured domain name and valid SSL certificate, the traffic looks perfectly legitimate as an HTTPS request that happens all the time.

To achieve this we need an extra web server (could be Nginx, Caddy, Apache or whatever) that does the SSL termination. And since VMess is not a common recognized protocol we need the extra wrapping of WebSocket to work with these web servers. It also requires knowledge of setting up web server, maintaining a public domain[^5] name and proper certificates[^6] for that. Although adding a bunch of complexity, this is by far one of the most stable solutions out there, and I have been using this for over 5 years.

[^5]: Explore options like [GoDaddy](https://www.godaddy.com/) or [Squrespace](https://domains.squarespace.com/)
[^6]: The most common way is to get one from [Let's Encrypt](https://letsencrypt.org/), although many modern web server (like Caddy) can handle that for you.

#### Cloud Native Self-hosting

As you may have read, I've been building my [private cloud](/blog/tag/Private%20Cloud/) from early this year, and V2Ray has been a core service to be supported in order to get rid of any public cloud cost. This section is to cover any modification I made to the previous solution to integrate seamlessly with my private cloud infra.

![current_v2ray](/static/image/current_v2ray.png "Current setup on the cluster")

As shown in the graph, I'm using the [Cloudflare tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) to replace the web server in the last section. Obviously the Cloudflare reverse proxy service is able to handle the TLS + WebSocket traffic and properly does SSL termination. As designed, the tunnel avoid the need to somehow expose local network for direct access, greatly increases security for self-hosting from home. Note that you can host multiple services through the tunnel, so a sub-domain prefix is needed for the V2Ray service.

The following is the basic k8s config for the V2Ray deployment and service:

```yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: v2ray
  labels:
    app: v2ray
spec:
  replicas: 1
  selector:
    matchLabels:
      app: v2ray
  template:
    metadata:
      labels:
        app: v2ray
    spec:
      containers:
        - name: v2fly/v2fly-core
          command: ["v2ray", "run", "-c", "/etc/v2ray/config.json"]
          volumeMounts:
            - name: config-volume
              mountPath: /etc/v2ray
          ports:
            - name: v2ray
              containerPort: 10000
      volumes:
        - name: config-volume
          hostPath:
            path: /host-path-to/v2ray
            type: Directory
---
apiVersion: v1
kind: Service
metadata:
  name: v2ray
spec:
  ports:
    - name: v2ray
      port: 10000
      targetPort: v2ray
  selector:
    app: v2ray
```

Note that the `v2fly/v2fly-core` docker image is good for all the previous solutions if you prefer a containerized way, both on client and server side. Running that with just docker installed is as easy as:
```shell
# running on host port 10000
docker run -d -p 10000:10000 -v /host-path-to-config-dir:/etc/v2ray \
    v2fly/v2fly-core
```
For specific ways to setup and configure Cloudflare tunnel, please refer to my [previous post](/blog/post/building_private_cloud_network_security_with_tunneling/).

#### Conclusion

This post (sort of) concludes the history and current status of my journey of fighting against GFW in the recent years, and I hope this will help you in some way.

Some following works include some possible upgrade to "more advanced technology" like [HTTP/2](https://guide.v2fly.org/advanced/h2.html) or adding [CDN](https://guide.v2fly.org/advanced/cdn.html), and also exploring some fancy features like [enabling traffic statistics](https://guide.v2fly.org/advanced/traffic.html) or [load balancing](https://guide.v2fly.org/app/balance.html#%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1) when there's actually more traffic.

Hope you enjoyed this post and until next time :)