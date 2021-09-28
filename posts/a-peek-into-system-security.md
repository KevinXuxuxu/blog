---
title: A Peek into System Security
date: 2021-09-22 22:27:45
tags: ["index", "infra", "AWS", "Monitoring", "Security"]
category: "tech"
---

This morning I got reached out by 2 tech companies: [GitGuardian](https://www.gitguardian.com/) and Slack, about a same issue related to the repository I just created: [prometheus-ecs](https://github.com/KevinXuxuxu/prometheus-ecs), which is a flattering experience. Unfortunately it's not that my repo is so good that they want to initiate business collaboration or anything, it's just that they found out one of my Slack webhook url is exposed in my (apparently public) repository, and were kind enough to warn me of it. Slack even went as far as directly revoking the exposed URL and issuing a new one.

I know it sounds like a stupid mistake that any engineer with some minimum industry experience and proper practice training shouldn't make. But here's some context: Recently I have been working on a side project about system monitoring and alerting. As I build, setup and operate a bunch of web services (for myself and my gf), I would like to be aware of their availability, even being alerted when things go down. As a natural result, I choose to use the famous open source project [Prometheus](https://prometheus.io), and would like to explore [AWS Elastic Container Service](https://aws.amazon.com/cn/ecs/) for deployment (if which works out, will be a cheaper choice for hosting any of my service).

After some intense (and a little frustrating) learning, I figured out that I need 3 components to achieve what I wanted:
- Prometheus main service (of course)
- Blackbox exporter (for blackbox monitoring, as I'm tight on resources and don't want to run any side car services or do any extensive coding on my existing services)
- Alert manager (for sending out alert via email or Slack)

Luckily folks from Prometheus have everything covered by supporting each of them as a docker image for swift deployment. Just mount some custom config and run them on ECS should do the work, peice of cake. That's what I thought before I realised that ECS doesn't actually support any volume mount. Yes, there's no way for you to dynamically pass files into containers with ECS, you'll have to build the file into the docker image. I think this is how AWS is enforcing the security [Principal of Least Privilege](https://digitalguardian.com/blog/what-principle-least-privilege-polp-best-practice-information-security-and-compliance), since you can always build every file/logic you need into the image.

So I started writing Dockerfiles, which should be as easy as `FROM prom/prometheus` plus `COPY prometheus.yml /etc/prometheus`, where it overwrites the config file with my custom one (and same for the alert manager, and blackbox exporter is stateless). Since I already have custom config and Dockerfiles, I might as well create a Github repo for it.

The problem was with the config for the alert manager (I skipped the failure of trying to make Gmail SMTP server work, so anyways I ended up with slack for notification). For some [not-so-obvious reason](https://github.com/prometheus/alertmanager/issues/2207), Prometheus decides not to support templating for `slack_api_url`, aka. it will not automatically render env variables into config file (which is actually [a standard practice](https://12factor.net/config) for micro services to get config or credentials). After a long day of struggling with all the tech details, I took the liberty to hard-code my Slack webhook url into the config file, and got busted by 2 companies (I'm suspecting that Slack actually hired GitGuardian but whatever).

```python
def parse_post_metadata(md: str) -> ParsedPost:
    _, metadata_str, content = md.split('---\n')
    metadata = {'content': content}
    for line in metadata_str.strip().split('\n'):
        key, value = line.split(': ')
        if key == 'tags':
            metadata['tags'] = eval(value.strip())
        else:
            metadata[key] = value.strip()
    return ParsedPost(**metadata)
```

To my defense, I do know the correct way to solve this thing, which is to write a custom templating logic into dockerfile (which is a good opportunity to pick up some shell magic):
```bash
ENTRYPOINT \
    sed -i "s=WEBHOOK_URL=${WEBHOOK_URL}=g" \
        /etc/alertmanager/alertmanager.yml && \
    /bin/alertmanager --config.file=/etc/alertmanager/alertmanager.yml \
        --storage.path=/alertmanager
```
I think the takeaway here is that don't ever be lazy over security issues, or it's definitely going to be discovered. I'm just lucky to be discovered by some good(?) folks.
