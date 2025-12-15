---
title: Building Private Cloud: 
subtitle: Network Security with Tunneling
date: 2024-05-19 04:20:09
tags: ["Private Cloud", "Cloudflare", "Reverse Proxy", "Tunnel", "Network"]
category: tech
thumbnail: /static/image/cf_tunnel.png
---
As mentioned in [a previous post](/blog/post/building_private_cloud_hosting_web_service/), I'm using Traefik to manage incoming public traffic to my private cloud. To achieve that, the public IP of my home internet will need to be exposed and it's sort of dangerous no matter how secure my system is.

To address this, a proper way is to setup a reverse proxy server in a isolated environment with a separate public IP to expose[^1], an ideal choice of such environment would be a vm from a cloud provider like AWS or Google Cloud Platform. But I'm very reluctant to do that because (as I mentioned before) the whole point of building private cloud is to get rid of the "AWS tax". 

[^1]: I've done this before when I'm working as an infra engineer for a startup, seems to be a pretty common practice.

While recently[^2] I came across [this blog](https://eevans.co/blog/garage/) which mentioned that [Cloudflare](https://www.cloudflare.com/) has a tunneling service and it's free (!). Given that I also wanted to take advantage of the DDoS protection from Cloudflare DNS, this seems like an ideal choice for me.

[^2]: Not actually recently, I set this up in February, but didn't got time to write about it until now.

#### Cloudflare Tunnel

Some more detailed info about [Cloudflare tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/): it's a reverse proxy service that helps you protect your system from exposing public access. By running a client within your system ([cloudflared](https://github.com/cloudflare/cloudflared)), you're building connection to Cloudflare's systems. With rules that you can set either from client side or on their consoles, external access to your domain can be redirected safely to the client, and then to your internal services. This gives you many advantages:
- Safety. No need to expose your home public IP to the internet, not even just some particular ports. This greatly reduces the change of being HaCkEd, or more commonly DDosed by attackers.
- You don't even need a stable public IP to host service! I know quite some ISPs doesn't guarantee stable IP address (or at least without an expensive premium) so it would come really handy if that's the case. [^3]
- You could get some sort of access monitoring and statistics from the tunnel service, if you bother to do the research and set that up.

[^3]: I vaguely remember that back in collage years, I wanted to access my computer when I'm away from home (e.g. during the semester) and I tried to write some clever program to periodically detect my current IP address because it keeps changing from time to time. Good old innocent days :) 

![cloudflare_tunnel_arch](/static/image/cf_tunnel.png "Simple Architecture of Cloudflare Tunnel")

General setup is pretty clearly documented in [the official docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/). For my use case, I'm using a simple deployment (not even with a service because it's not necessary) to run the client side `cloudflared` in my cluster, which has an official docker image that works perfectly fine.

```yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: cloudflared
  namespace: kube-system
  labels:
    app: cloudflared
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cloudflared
  template:
    metadata:
      labels:
        app: cloudflared
    spec:
      containers:
        - name: cloudflared
          image: cloudflare/cloudflared
          env:
          - name: TOKEN
            valueFrom:
              secretKeyRef:
                name: cloudflared-token
                key: token
          args: [
            "tunnel",
            "--no-autoupdate",
            "run",
            "--token",
            "$(TOKEN)"
          ]
```

Note that similar to most cloud services, an access token is needed. As suggested [here](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/get-started/create-remote-tunnel/#1-create-a-tunnel), the token will be generated when you create the the tunnel in the console. Here we save the token into k8s secret, and access it with env variable.[^4]

[^4]: Maybe I'm just stupid but I stuck here for a good 2 hours (and to the point of doubting if the official image is broken and if I need to build my own) just because referencing a env variable in `args` field has to be done *exactly* like `$(TOKEN)` but not any other way like `$TOKEN` or `${TOKEN}` (or even worse, with some sort of escaping). Anyways a good TIL.

In order to start using this I transferred my domain's nameserver (and my GF's as well) to Cloudflare, and then I could set up the proxy rules for all the subdomains to my internal service's cluster IP.

```shell
$ kubectl get services
NAME             TYPE        CLUSTER-IP        EXTERNAL-IP   PORT(S)     AGE
kubernetes       ClusterIP   192.168.0.1       <none>        443/TCP     151d
v2ray            ClusterIP   192.168.40.198    <none>        10000/TCP   78d
jupyter-server   ClusterIP   192.168.97.149    <none>        8888/TCP    55d
...
```

#### Caveats

There is a caveat that I spent quite some time getting that I think I should mention here. It is about the capability of cloudflare tunnel service. It works very well for regular public services, but **mostly websites** and some sort of web based services. So HTTP and HTTPS definitely works, that's why I can run my v2ray VPN service (SSL + websocket) over it (thankfully). But other types of services doesn't seem to work, at least not directly.

Cloudflare is cryptic about a general way to access other types of services in their docs (probably because they want you to use their other solutions e.g. WARP, especially if you're an enterprise customer), but I figured that you'll need to run another `cloudflared` client on the other side (where you want to access your service). Something like this
```shell
cloudflared access tcp --hostname foo.example.com --url localhost:1234
```
will connect to the `foo` service which is TCP based, and (for whatever reason) create a proxy on port `1234` of client host to access. I imagine another reason is that Cloudflare doesn't want to this to be "too powerful" to be used by enterprise as e.g. public db service for security and cost reasons.

#### Future Work

There're 2 other things I probably need to work to make this more of a thoroughly working solution. One is that I'm *manually* checking the cluster IPs of my internal services and adding them to the tunnel rules. This will definitely break if I do any re-deployment, at which time I'll need to reconfigure the rules again. I should probably take advantage of some load-balancer resource on top of services, or form my maintenance practice, split configuration files of services and deployments, so that they get deployed separately.

Another security measurement to take is to do network lockdown for the `cloudflared` deployment. Basically I can label my internal services to be publicly accessible or not, and restrict network traffic from `cloudflared` strictly to those services. This help tighten the access control of public traffic even if there's misconfiguration of worse things happening.

Hope you enjoyed and until next time!

*For the list of the series of blog posts about building private cloud, click [here](/blog/tag/Private%20Cloud/).*
