---
title: Building Private Cloud: Hosting Web Service
date: 2024-02-02 05:34:15
tags: ["k8s", "Traefik", "Network", "Private Cloud", "HTTPS"]
category: tech
---

In my [previous post](/blog/post/building_private_cloud_basic_setup/), the basic setup of a private cloud with [Turing Pi 2](https://turingpi.com/) board and rpi cm4 is presented. Now we can talk about how to start using the cluster for some simple web services.

The [k3s](https://docs.k3s.io/) system is very convenient in terms of supporting systems, as it comes with pre-installed [Traefik](https://github.com/traefik/traefik) ingress controller, which will be an important part of the cluster's network management system. First let's go over how to work with Traefik in a k8s context.

#### Traefik

Traefik is a complex system with some internal structures and works with many other services. But for now we mostly care about it's role as a network proxy for our internal services. As shown in this graph I got from [Traefik docs](https://doc.traefik.io/traefik/routing/overview/), it clearly defines components corresponding to each logic abstraction related to the problem it's solving:

<img src="https://doc.traefik.io/traefik/assets/img/architecture-overview.png" style="width: 100%"/>

- Entrypoint: What are the overall entrypoints of the cluster? There might be many more services in the cluster than the number of ports we're reasonably able to expose, so this is a very important abstraction in network engineering.
- Routers: This is the part where we apply different rules to determine where the the request goes, and we might do some modification to the request, among which the most common one is [SSL termination](https://en.wikipedia.org/wiki/TLS_termination_proxy). This is the part that contains most logic.
- Service: This is the k8s native `Service` component, using which we claim that some other component is to be served.

Note that this set of abstraction doesn't care about the physical layout of the deployment, which means that it has a load balancer under the hood. With that we can deploy our service to the most proper host, and optimize for resource efficiency.

In our k3s setup, we already have 4 entrypoints configured for us, which are `:9100` for metrics, `:9000` for Traefik dashboard, `:8000` for HTTP requests and `:8443` for HTTPS requests. We can check that either with proxied traefik dashboard:
```shell
kubectl -n kube-system port-forward $(kubectl -n kube-system get pods --selector "app.kubernetes.io/name=traefik" --output=name) 9000:9000
```
and visit [http://localhost:9000/dashboard/#/](http://localhost:9000/dashboard/#/), or just check the Traefik k8s `Deployment` for details:
```shell
$ kubectl describe deployment -n kube-system traefik
Name:                   traefik
Namespace:              kube-system
...
Pod Template:
  ...
  Containers:
   traefik:
    Image:       rancher/mirrored-library-traefik:2.10.5
    Ports:       9100/TCP, 9000/TCP, 8000/TCP, 8443/TCP
    Host Ports:  0/TCP, 0/TCP, 0/TCP, 0/TCP
    Args:
      --global.checknewversion
      --global.sendanonymoususage
      --entrypoints.metrics.address=:9100/tcp
      --entrypoints.traefik.address=:9000/tcp
      --entrypoints.web.address=:8000/tcp
      --entrypoints.websecure.address=:8443/tcp
      --api.dashboard=true
      --ping=true
...
```
We will be able to add new entrypoints if we want to serve some special services, but for now these should suffice.

Note that these entrypoints are not yet publicly accessible to external requesters, and some of them shouldn't be (e.g. metrics and dashboard). Traefik also deploys a service load balancer as a k8s `Deamonset`, which will start a pod on each host to listen on certain ports:
```shell
$ kubectl describe daemonsets -n kube-system svclb-traefik
Name:           svclb-traefik-70522e78
Selector:       app=svclb-traefik-70522e78
...
Pods Status:  4 Running / 0 Waiting / 0 Succeeded / 0 Failed
Pod Template:
  ...
  Containers:
   lb-tcp-80:
    Image:      rancher/klipper-lb:v0.4.4
    Port:       80/TCP
    Host Port:  80/TCP
    Environment:
      SRC_PORT:    80
      SRC_RANGES:  0.0.0.0/0
      DEST_PROTO:  TCP
      DEST_PORT:   80
      DEST_IPS:    10.43.219.43
    Mounts:        <none>
   lb-tcp-443:
    Image:      rancher/klipper-lb:v0.4.4
    Port:       443/TCP
    Host Port:  443/TCP
    Environment:
      SRC_PORT:    443
      SRC_RANGES:  0.0.0.0/0
      DEST_PROTO:  TCP
      DEST_PORT:   443
      DEST_IPS:    10.43.219.43
...
```
The listened ports (80 and 443) are all redirected to destination IP `10.43.219.43` which matches the cluster IP of the Traefik k8s `Service`:
```shell
$ kubectl describe service -n kube-system traefik 
Name:                     traefik
Namespace:                kube-system
...
Selector:                 app.kubernetes.io/instance=traefik-kube-system,app.kubernetes.io/name=traefik
Type:                     LoadBalancer
IP Family Policy:         PreferDualStack
IP Families:              IPv4
IP:                       10.43.219.43
IPs:                      10.43.219.43
...
Port:                     web  80/TCP
TargetPort:               web/TCP
NodePort:                 web  32764/TCP
Endpoints:                10.42.1.29:8000
Port:                     websecure  443/TCP
TargetPort:               websecure/TCP
NodePort:                 websecure  32135/TCP
Endpoints:                10.42.1.29:8443
...
```

The Traefik service will send the request from 80, 443 ports to endpoints 8000, 8443, which matches the entrypoints defined for Traefik.

#### Basic Setup

Let's say you want to host your personal website on the cluster. What we need is 3 components: the `Deployment` for the website server itself (which will automatically create `ReplicaSet` and `Pod` for the server), the `Service` to expose the deployment, and an `IngresRoute` to connect with Traefik system (fits into the "routers" component we talked about). A basic setup should look like this:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysite
  labels:
    app: mysite
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysite
  template:
    metadata:
      labels:
        app: mysite
    spec:
      containers:
      - image: nginx
        name: mysite-nginx
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: mysite
spec:
  ports:
  - name: mysite
    port: 80
    targetPort: 80
  selector:
    app: mysite
---
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: mysite
spec:
  entryPoints:
    - web
  routes:
  - kind: Rule
    match: Host(`mysite.domain.com`)
    services:
    - name: mysite
      port: 80
```

Save this to file `mysite.yaml` and run the following command to deploy:
```shell
kubectl apply -f /path/to/mysite.yaml
```
In this example the server just runs [Nginx](https://nginx.org/en/) and probably serves some static web pages, but the shape and behavior of your website can be anything that works for you. The only important thing is to expose a container port for external access.

In `IngressRoute` we specify which entrypoint to use. For this example we're using `web` which corresponds to the HTTP entrypoint. The routing rule basically means that for requests into the specified entrypoint that access host name `mysite.domain.com`, redirect to `mysite` service port 80. Note that we can have arbitrarily many services getting request from the same entrypoint, the way to distinguish them is by the matching rules, and we can do much more fancy stuff with that.

There are 2 ways to test this:
- Go to the domain's provider, point the domain to your home public IP address ([what's my IP address?](https://whatismyipaddress.com/)); log into your home router and setup firewall rules and port forwarding (`external 80 -> <subnet IP of a node>:80`). 
- Map the domain name to subnet IP of a node by adding this line in `/etc/hosts` file:

```text
<subnet IP of a node>   mysite.domain.com
```

Either way should work, but the first one is better since that's the eventual approach of deployment. You can try that by go to `http://mysite.domain.com` in your browser.

#### HTTPS

Although it's [not our choice](https://news.ycombinator.com/item?id=26555873), it's close to impossible to host a website with decent user experience without an SSL certificate. Luckily Traefik makes it fairly easy to create, verify and maintain a widely recognized TLS certificate with [Let's Encrypt](https://letsencrypt.org/).

First, use `kubectl apply` to apply the following change to the existing Traefik service, with `YOUR_EMAIL` replaced with your email:
```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    additionalArguments:
      - "--log.level=DEBUG"
      - "--certificatesresolvers.le.acme.email=YOUR_EMAIL"
      - "--certificatesresolvers.le.acme.storage=/data/acme.json"
      - "--certificatesresolvers.le.acme.tlschallenge=true"
      - "--certificatesresolvers.le.acme.caServer=https://acme-v02.api.letsencrypt.org/directory"
```
This creates a certificate resolver named `le` using Let's Encrypt server, which can be used in your services. To enable https, update the `IngressRoute` part from previous example to:
```yaml
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: mysite
spec:
  entryPoints:
    - websecure # <- changed
  routes:
  - kind: Rule
    match: Host(`mysite.domain.com`)
    services:
    - name: mysite
      port: 80
  tls:                # <- added
    certResolver: le  # <- added
```
And run the `kubectl apply` command to update the deployment. Note that the port exposed by `mysite` is still 80, and the server can serve everything in pure HTTP, because the SSL termination happens in this `IngressRoute` component.

For more detailed instruction about supporting HTTPS services, check [this blog](https://traefik.io/blog/https-on-kubernetes-using-traefik-proxy/) from Traefik, which covers more about testing and caveats you might run into e.g. use staging acme server for testing to avoid rate limiting, or how to test the TLS quality etc.

#### Up Next

When I was learning the k3s and Traefik networking stuff, I got some strange issue: with all the setup above, I can only access my service from outside of my home subnet, but not inside. In following posts I'll cover how to resolve this issue by hosting a local DNS server and more.

Happy hacking! :)

*For the list of the series of blog posts about building private cloud, click [here](/blog/tag/Private%20Cloud/).*