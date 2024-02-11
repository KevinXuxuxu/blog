---
title: Building Private Cloud: Local DNS
date: 2024-02-11 02:54:12
tags: ["k8s", "Private Cloud", "Network", "DNS", "CoreDNS"]
category: tech
---

I have mentioned a strange problem in [a previous post](/blog/post/building_private_cloud_hosting_web_service/#up_next) that I'm not able to access services hosted in my cluster from within my home subnet, but it works from outside. This issue bothered me quite a while, once I was even considering that the whole Traefik stack is broken with this k3s distribution. (Which is reasonable because honestly who would turn off phone wifi to check home cluster network issue?)

The solution I have is to utilize the [CoreDNS](https://coredns.io/) service that comes with k3s as a local self-hosted DNS server, and resolve my inter-cluster services directly to my cluster IP, so that it doesn't have to go the long way, avoiding whatever problem that way had. Plus, having a local DNS is very convenient when you have some internal service, but want cool domain name and TLS enabled for them.

So let's get right into it.

#### CoreDNS Service

CoreDNS is an [important component](https://docs.k3s.io/networking#coredns) of the k3s network infrastructure, serving as the [cluster DNS](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/) of the k8s system. We can check the existing deployment status of the service in the `kube-system` namespace:

```shell
$ kubectl get deployment -n kube-system -o wide
NAME                     READY   UP-TO-DATE   AVAILABLE   AGE     CONTAINERS               IMAGES                                    SELECTOR
...
coredns                  1/1     1            1           53d     coredns                  rancher/mirrored-coredns-coredns:1.10.1   k8s-app=kube-dns

$ kubectl get pod -n kube-system
NAME                                      READY   STATUS      RESTARTS   AGE
...
coredns-6799fbcd5-wn6pm                   1/1     Running     0          22h

$ kubectl describe pod -n kube-system coredns
Name:                 coredns-6799fbcd5-wn6pm
Namespace:            kube-system
Priority:             2000000000
Priority Class Name:  system-cluster-critical
Service Account:      coredns
...
Containers:
  coredns:
    ...
    Ports:         53/UDP, 53/TCP, 9153/TCP
    Host Ports:    0/UDP, 0/TCP, 0/TCP
    Args:
      -conf
      /etc/coredns/Corefile
    ...
    Mounts:
      /etc/coredns from config-volume (ro)
      /etc/coredns/custom from custom-config-volume (ro)
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-x77ml (ro)
...
Volumes:
  config-volume:
    Type:      ConfigMap (a volume populated by a ConfigMap)
    Name:      coredns
    Optional:  false
  custom-config-volume:
    Type:      ConfigMap (a volume populated by a ConfigMap)
    Name:      coredns-custom
    Optional:  true
  kube-api-access-x77ml:
    Type:                     Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:   3607
    ConfigMapName:            kube-root-ca.crt
    ConfigMapOptional:        <nil>
    DownwardAPI:              true
...
```
From the config we got important pieces of information:
- CoreDNS has very high priority and is in `system-cluster-critical` priority class.
- CoreDNS is opening port `53` on UDP and TCP for the main service, and port `9153` for metrics. `53` is the default port used to serve most DNS requests.
- The main configuration source is `/etc/coredns/Corefile`, which is mounted from a k8s `ConfigMap` named `coredns`. But there're 2 other volumes mounted:
    - `coredns-custom`, which is used for custom DNS rules, which will be covered later.
    - `kube-root-ca.crt` which is the k8s root ca provider. The volume type is `Projected` which means that the content inside is managed by other service and subject to change.

#### the Corefile

Now let's take a look at the `Corefile` used to configure the DNS behaviors:

```shell
$ kubectl describe configmap coredns -n kube-system
Name:         coredns
Namespace:    kube-system
...
Data
====
Corefile:
----
.:53 {
    errors
    health
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {
      pods insecure
      fallthrough in-addr.arpa ip6.arpa
    }
    hosts /etc/coredns/NodeHosts {
      ttl 60
      reload 15s
      fallthrough
    }
    prometheus :9153
    forward . /etc/resolv.conf
    cache 30
    loop
    reload
    loadbalance
    import /etc/coredns/custom/*.override
}
import /etc/coredns/custom/*.server

NodeHosts:
----
192.168.0.10 rpicm4n1
192.168.0.11 rpicm4n2
192.168.0.12 rpicm4n3
192.168.0.13 rk1
...
```

The `Corefile` itself has only one rule that starts with `.:53`, which means this rule resolves DNS requests to port `53` of all domains. Within it are a few important components:
- `kubernetes` is [the plugin](https://coredns.io/plugins/kubernetes/) used for k8s service discovery, just leave it there so that nothing gets broken.
- `hosts` [plugin](https://coredns.io/plugins/hosts/) reads a hosts file and use that for domain resolution. For now it read the file `/etc/coredns/NodeHosts` whose content is from the same config map. We'll be mostly changing this for now.
- `forward` [plugin](https://coredns.io/plugins/forward/) defines the behavior that delegates name resolution to other nameservers. In this case it forwards requests to whatever server that's in `/etc/resolv.conf`, which should be populated by the containers network environment. For a homelab, that's mostly being configured by your ISP.
- Custom plugins in the main rule is imported from `/etc/coredns/custom/*.override` and custom rules are imported from `/etc/coredns/custom/*.server`, which is not configured by default but is something to consider if you want to do more fancy stuff.

To edit this existing `ConfigMap`, use the following command:

```shell
$ kubectl edit configmap coredns -n kube-system
```

This will open a default commandline editor for you to change the content. To solve my problem, all I need is to resolve all my external services to the master node IP by adding the following lines in the `NodeHosts` section:

```text
192.168.0.10    service1.example.com
192.168.0.10    service2.example.com
192.168.0.10    service.local.example.com
```

Note that the "external" in this context means "external of the cluster". So we will need to add here even if we want to host a service only locally in the home internet.

#### Is that all?

Not yet. As we mentioned before, any service within the cluster has to use Traefik to expose to requesters outside of the cluster. The CoreDNS by default only serves the inter-cluster use case, so we need to add the missing pieces.

Remember [the piece of YAML](/blog/post/building_private_cloud_hosting_web_service/#https) we applied for Traefik that configures the auto certificate signing with Let's Encrypt? Add the following to it and apply again. This will add a new Traefik entrypoint for port `53`:

```yaml
...
spec:
  valuesContent: |-
    ...
    ports:
      dns:
        protocol: UDP
        port: 53
        expose: true
        exposedPort: 53
```
Note that we're using UDP protocol for this entrypoint, since most DNS requests are in UDP not TCP. Then, the last pieces are the corresponding `Service` and `IngressRoute` for CoreDNS service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: coredns
  namespace: kube-system
spec:
  ports:
    - name: coredns-udp
      protocol: UDP
      port: 53
      targetPort: 53
  selector:
    k8s-app: kube-dns
---
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRouteUDP
metadata:
  name: coredns
  namespace: kube-system
spec:
  entryPoints:
    - dns
  routes:
  - services:
    - name: coredns
      port: 53
```

After applying this everything should work. For any device to access these services freely, change the DNS config of the wifi (or ethernet) network to favor the local DNS server, which is accessible from the cluster IP (IP of master node). Another benefit is that all the node names are also being resolved automatically. Now I can do `ssh rpicm4n1` without changing `/etc/hosts` anymore.

#### Conclusion

Although I'm able to find a relatively good solution, it's still not clear what the actual problem is. My guess is that when you go "the long way" only trying to get back to your home public IP, the places you're from are being ignored during the jumps. Kinda like the "not visiting a visited point" rule in search algorithms.

Anyways, that's all for this post. In following posts we'll shift gears and talk about storage solutions for private cloud (if I get all the work done), as well as hosting local container registry in a k8s context. Hope you enjoy :)

BTW Happy Chinese New Year!

*For the list of the series of blog posts about building private cloud, click [here](/blog/tag/Private%20Cloud/).*
