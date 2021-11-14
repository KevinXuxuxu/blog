---
title: Simple Github CI Solution
date: 2021-10-31 22:12:12
tags: ["Github", "CI", "Docker"]
category: tech
---
For the past few weeks I've been working on enabling CI for one of my side project ([NN](https://github.com/KevinXuxuxu/NN)). I forced myself to add some unit/e2e tests while I was developing it, and it would be nice to automatically run them thoughout the dev-integration process. This solution needs to meet a few requirements:
- Automatically run all tests when new change is pushed to Github
    - On the main branch so that we know it's not broken
    - On every comment on every PR
- Blocks PR merge when test fails (obviously)
- Easy to build (relatively), since the side project itself is not big and I have limited spare time
- Doesn't cost too much money (relatively), for similar reasons

The general idea of the solution should be pretty straightforward: when a Github event that we care about (e.g. push to a PR) happens, Github sends request that triggers our CI server to do some jobs (e.g. unit testing), and returns the job result to Github.

Of course we're familiar with the traditional OSS solution that's widely adopted by startups (for budgets reasons), where a job scheduling service, usually [Jenkins](https://www.jenkins.io/) or [Argo Workflows](https://argoproj.github.io/workflows) if you're a k8s guy, serves as the CI server which will handle the job requests on your computing resources. They all have good support for communicating with Github, and seems to be mature solutions.

Unfortunately my spare time and energy are limited and more importantly easily distracted. Github has quite some docs regarding its CI support, but there's just so many concepts (Actions, Runners, Webhooks, Workflow, Checks, etc.) and they lack a straightforward introduction or summary on how these concepts should work together. After spending a whole Saturday two weeks ago without any meaningful progress (somehow I got stuck with generating valid [JWT](https://jwt.io/) for Github authentication, and fucked up my Python environment with `cryptography` package, and that was my last straw), I gave up on playing with Github APIs.

Then it comes this Wednesday, when I was reading [an article about what you could do with the new Raspberry Pi Zero 2 W](https://blog.alexellis.io/raspberry-pi-zero-2/), and the author mentioned something called [self-hosted actions runner](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners), which I immediately realised could be the answer I was looking for. The docs about it has all the information (or at least readable), but the idea is that Github have this stand-alone light-weight open-source executable that has the following feature:
- Automatically connects with Github and registers as a job runner, which is super smooth without any of the push-pull-base arguments or public interface security concerns
- Takes in part of a config file with e.g. shell commands as job definition, with which you can do pretty much anything with properly setup environment.
    - The other part of the config file is for Github to know on what condition to find a free runner and trigger the job. It even support labelling the runners based on the requirements of your job.

This literally blew my mind. Think about it: Given a bunch of these runners on k8s, you effectively have a powerful enough CI cluster that could do anything you would expect from e.g. Jenkins, and it has generic Github support and amazing scalability.

So I followed the docs to start a runner on a "droplet" (chose DigitalOcean this time for a cheaper price) and quickly wrote a Github workflow definition (the "config file" I just mentioned) and got a prototype running. After I finished implementing my solution, here are the only two pieces of code (or config files?) I wrote:

```yaml
name: CI
# Controls when the workflow will run
on:
  # Triggers the workflow on push or pull request events but only for the main branch
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:
# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:
  # This workflow contains a single job called "unit-test"
  unit-test:
    # The type of runner that the job will run on
    runs-on: self-hosted
    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:
      # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
      - uses: actions/checkout@v2
      # Run all unit tests
      - name: unit test
        run: bazel test //test:all --test_output=errors
```

This is the workflow definition I had, which varies very little from the example Github gave. Note that all I did was checkout the repo on a given state, and run `bazel test` for the result, since I already built this runner into my project environment with Docker.

```shell
FROM fzxu/nn

RUN mkdir actions-runner && cd actions-runner \
  && curl -o actions-runner-linux-x64-2.283.3.tar.gz -L https://github.com/actions/runner/releases/download/v2.283.3/actions-runner-linux-x64-2.283.3.tar.gz \
  && tar xzf ./actions-runner-linux-x64-2.283.3.tar.gz

ENV DEBIAN_FRONTEND=noninteractive

RUN cd /actions-runner && ./bin/installdependencies.sh

COPY scripts/config.sh /actions-runner/config.sh

COPY scripts/run.sh /actions-runner/run.sh

WORKDIR /actions-runner

ENTRYPOINT ./config.sh --url https://github.com/KevinXuxuxu/NN --token $TOKEN && ./run.sh
```

This is the Dockerfile I used to make it instantly runnable for better scaling (probably never going to need it), and it's build upon my devops environment to be able to run any build or test easily.

There's also a hack I need to confess. The runner doesn't want you to run it as a sudo user for security reasons, especially for open source projects because random PR is going to trigger runners to run possibly malicious code on your machine. While my devops environment is built with just a root user (which is probably not good), I bypassed the check just to quickly get it working since my runner runs in docker container which is already isolation (sort of). I'll put more research into this, specificly on how code within container could affect the host, how to properly not use root, and how is that safer anyways.

### Followup

OK, they got me again. Basically the Github self-hosted actions runner is as good as supporting automatic update when there is a new version available. When the update happens, old scripts are overwritten by the new version, which makes my "escape non-sudo user check" hack fail.

To do it the proper way, I learned now to create and switch users in Dockerfile, and this is how it looks now:
```shell
FROM fzxu/nn

RUN adduser --disabled-password --gecos "" actions-runner

USER actions-runner

RUN cd /home/actions-runner \
  && curl -o actions-runner-linux-x64-2.284.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.284.0/actions-runner-linux-x64-2.284.0.tar.gz \
  && tar xzf ./actions-runner-linux-x64-2.284.0.tar.gz

USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN cd /home/actions-runner && ./bin/installdependencies.sh

USER actions-runner

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /home/actions-runner

ENTRYPOINT ./config.sh --url https://github.com/KevinXuxuxu/NN --token $TOKEN && ./run.sh
```
Notice in this case I got rid of the custom config and run script hack, and the deployment now support automatic version upgrade.
