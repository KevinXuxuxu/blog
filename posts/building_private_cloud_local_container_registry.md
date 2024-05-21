---
title: Building Private Cloud: Local Container Registry
date: 2024-04-14 04:47:45
tags: ["Private Cloud", "k8s", "Docker", "Container Registry"]
category: tech
---
In this short post we're going to cover my experience on setting up a local container registry that runs within my cluster. This greatly helps reduce the overall ingress traffic throughout the development and maintenance of applications on the cluster, and also removed the necessity of exposing image on public registries (e.g. [Docker Hub](https://hub.docker.com/)) that force you to pay for better security.

#### Options
Our requirement is simple: we want to host a container registry on the cluster to serve docker images within our local network; we should be able to push and pull image from the registry just like we use Docker Hub; performance, scalability and security should be good enough, but with lower priority. After all light-weight and convenience are the main purposes our home cluster. After some research, I found the following potential candidates:
- [Harbor](https://goharbor.io/): Probably the most famous and trusted solution, with all the high-availability and security support.  it's probably a bit too heavy for me.
- [**CNCF Distribution**](https://distribution.github.io/distribution/): "The Registry is a stateless, highly scalable server side application that stores and lets you distribute container images and other content". Aside from its confusing name, this is quite a decent solution for a self-hosted registry.
- Some other solutions: [Quay.io](https://quay.io/), [Portus](https://github.com/SUSE/Portus), [Gitlab Container registry](https://docs.gitlab.com/ee/user/packages/container_registry/), all supporting more than docker images and providing more features that might not be useful for me.

I decided to use CNCF Distribution for obvious reasons, plus it seems to be [actively maintained](https://github.com/distribution/distribution).

#### Deployment

At the beginning I imagined it to be a pretty standard web service deployment, but later found out that there is a few twists to it:
- Obviously it is going to need persistent local storage support, so we'll need to utilize the setup we covered in [Storage Solution](/blog/post/building_private_cloud_storage_solution/#implementation), and we'll cover that in a bit.
- Most container registry client prefers SSL connection to the registry[^1], so we need to properly handle that.
- Do we need authentication support? Some solution might force that as a security feature.
[^1]: This is a conclusion from a tremendous amount of trial and failure 🥹.

Long story short, here's the overall k8s deployment config:

```yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: registry
  namespace: kube-system
  labels:
    app: registry
spec:
  replicas: 1
  selector:
    matchLabels:
      app: registry
  template:
    metadata:
      labels:
        app: registry
    spec:
      containers:
        - name: registry
          image: registry:2
          volumeMounts:
            - name: registry-storage
              mountPath: /var/lib/registry
          ports:
            - name: registry
              containerPort: 5000
      volumes:
        - name: registry-storage
          hostPath:
            path: /mnt/m2/shared/registry
            type: Directory
```
For the persistent storage, we're creating a directory `registry` in the shared NFS dir `/mnt/m2/shared`. Since no node selector is specified, we're not guaranteed to run registry on the NFS server node. As a result we should make registry have open permission[^2] to guarantee accessibility from any node. With that, we can create a `hostPath` volume on that dir and mount it into the container to `/var/lib/registry` where the registry is going to store all the images and metadata.

[^2]: 777 permission. I know this is very dangerous security wise, but it's entirely internally used, and I'll try to enforce a group based permission very soon.

For network access, we'll first generate SSL certificates for the registry service:
```shell
$ openssl req -x509 -newkey rsa:4096 -days 365 -nodes -sha256 \
-keyout certs/tls.key -out certs/tls.crt \
-subj "/CN=cr.local.example.com" \
-addext "subjectAltName = DNS:cr.local.example.com"
# stdout:
Generating a RSA private key
...........................................................................................................................................++++
.............................................................++++
writing new private key to 'certs/tls.key'
-----
$ ls
tls.key tls.crt
```
Replace `cr.local.example.com` with the domain name you want to use for the local container registry service. Then we add this pair of cert/key to k8s secrets to be used later by Treafik ingress.
```shell
$ kubectl create secret tls registry-certs --cert=tls.crt --key=tls.key
```
Finally we have the k8s definition for the `Service` and `IngressRoute`, together they will use the certs and serve the registry service within the cluster.
```yaml
apiVersion: v1
kind: Service
metadata:
  name: registry
  namespace: kube-system
spec:
  ports:
    - name: registry
      port: 5000
      targetPort: registry
  selector:
    app: registry
---
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: registry
  namespace: kube-system
spec:
  entryPoints:
    - registry
  routes:
  - kind: Rule
    match: Host(`cr.local.example.com`)
    services:
    - name: registry
      port: 5000
  tls:
    secretName: registry-certs
```
A few things to note:
- We use port 5000 all over the config because that's the default port for docker registry services.
- In Traefik `IngressRoute`, we provide the previously created secret so that Traefik can properly serve with SSL support.
- For the entry point, we need to create a new one for port 5000 called registry. Check [here](/blog/post/building_private_cloud_local_dns/#is_that_all?) about how to add entry points.

Since we're creating and using "self-signed" SSL certificates, we need to "trust" the cert from where you're trying to access it. The way of doing that varies by the OS/Distro you are running on your nodes.
- To access registry from docker client, add certs to `/etc/docker/certs.d/cr.local.example.com:5000/`[^3]
- To access registry from k8s cluster, the certs need to be trusted by from the OS on each node. For Debian based OS (Ubuntu, RPiOS), copy `.crt` file to `/usr/local/share/ca-certificates/`, and run `sudo update-ca-certificates` to make it effective.

[^3]: In my case I need to access from docker on my MacOS because I do all my work there, including building and managing images. To do that you should be able to open the `.crt` file using the Keychain Access program and trust it on OS level.

Finally, we need to add `cr.local.example.com` to our local DNS server, so that it's accessible not only from within the cluster, but also within your home subnet. As we introduced in [Local DNS](/blog/post/building_private_cloud_local_dns/#the_corefile), use the following command to edit CoreDNS config file and add `cr.local.example.com` as a new host in `NodeHosts` block, and point to any node IP.
```shell
$ kubectl edit configmap coredns -n kube-system
# opens an editor:
apiVersion: v1
data:
  Corefile: |
  ...
  NodeHosts: |
    192.168.0.10 rpicm4n1
    192.168.0.11 rpicm4n2
    192.168.0.12 rpicm4n3
    192.168.0.13 rk1
    192.168.0.10 cr.local.example.com
    ...
```

#### Usage

The usage is fairly simple. Any images that we use in the cluster, we can re-tag it and push to the local registry:
```shell
docker tag postgres cr.local.example.com:5000/postgres
docker push cr.local.example.com:5000/postgres
```
In the deployment config, use the image form local registry instead of docker hub (or any public registry) version:
```yaml
apiVersion: apps.openshift.io/v1alpha1
kind: DeploymentConfig
metadata:
  ...
spec:
  ...
  template:
    ...
    spec:
      containers:
      - name: postgres-example
        image: cr.local.example.com:5000/postgres
  ...
```
For any publicly available images you should be able to use the local registry as a proxy (or cache) by setting up proxy configuration ([ref](https://distribution.github.io/distribution/about/configuration/#proxy)). But for now I'm just manually managing all the images.

According to my experience the image pulling speed is not significantly faster than pull from public registry, probably because my in-house network infrastructure is not in any way advanced. But it does greatly reduce the network bandwidth usage by a lot, especially when I'm constantly re-deploying images for development purposes.

That's all for this post and hope you enjoyed :)

*For the list of the series of blog posts about building private cloud, click [here](/blog/tag/Private%20Cloud/).*
