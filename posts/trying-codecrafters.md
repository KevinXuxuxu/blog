---
title: Trying Codecrafters.io: 
subtitle: Not Recommended (for now)
date: 2022-08-27 13:03:08
tags: ["Go", "Redis", "RESP", "Codecrafters"]
category: tech
---

Recently I came upon this interesting online interactive learning program called [Codecrafters](https://codecrafters.io/), which is a series of small projects with guidance for you to learn along the way. In their own words:
> Recreate Redis, Git, Docker -- with your own hands. Gain expert-level confidence by taking action and diving deep, learning from the world's best.
So I've been told. I tried to sell the idea to my manager and got quickly approved (with a bunch of valuable comments that I really appreciate), and I proceed to start the 3-day free trail, followed by a 3-month subscription for $200 (wow), with 2/3 of that covered by my company.

Well, you only get charged if you still like it _after_ the free trail, after all that's what free trail means.

So I started with [Build Redis with Go](https://app.codecrafters.io/courses/redis?fresh=false&track=go) project, which seems to be their main attraction. I had to be honest that they're using some very interesting technology to interact with users. You need a Github account to login, but it doesn't interact with Github system during the process (except for OAuth), while they let you clone repo and interact with their own git system which apparently have some CI hook behind it to run tests on your version of code on each stage.

Back to the project itself. I was expecting it to touch various interesting design and intuitions behind Redis such as
- how it achieved high throughput / low latency with [WAL](https://en.wikipedia.org/wiki/Write-ahead_logging)
- how it combines point-in-time snapshots with [AOF](https://redis.com/ebook/part-2-core-concepts/chapter-4-keeping-data-safe-and-ensuring-performance/4-1-persistence-options/4-1-2-append-only-file-persistence/) for durable data persistance.
- various approach for distributed scalability (e.g. [Redis Cluster](https://redis.io/docs/manual/scaling/))

But apparently **none** of that was covered. The project is centered around implementing a simple redis server that complies with [RESP](https://redis.io/docs/reference/protocol-spec/) and support only a small subset of commands (`PING`, `ECHO`, `SET`, `GET`). The real complexity of this project lies in the following points:
- Get the TCP-based server to work properly with test client in your target language
- Parse the RESP string which has some recursive/nested structure
- Handle some concurrent operations with locks to avoid racing issues

To be fair, these points are interesting to work on by themselves. I spent around 7 hours through 2-3 days to finish it (Credit to my GF for pushing me to save money for my company), during which I spent most time on dealing with the RESP string in an elegant and extensible way, which made the experience more like "a coding fever on [a hard Leetcode question](https://leetcode.com/problems/parse-lisp-expression/)" than "Build your own Redis".

So to wrap it up, some pros'n'cons for codecrafters.io:
- Cons:
    - The scope of projects is falsely advertised. They don't get to touch any system design as deep as you would want to explore as a senior developer.
    - The guidance is poor. There's nearly nothing between "here's your target" and "here's the solution", so you'll need to basically self-teach if you don't already know the answer and don't want to look at the solution directly.
    - The interactive test case is far from comprehensive. For the last 2 parts of the Redis project I spent 70% of my time, while the test cases are so simple that no concurrent access, highly nested structure, or even some common edge cases are tested. It shows that the creators didn't pay much attention on the quality which is sad.
    - The solution is not very crafted. I didn't get the chance to save their given solution, but I guess you can find it somewhere in Github. As far as I remember, it neglected some edge cases, is not very readable or extensible, basically written to barely pass their only tests.
    - Given the previous points, quite over priced. You can see that they're just targeting employees for expensing.
- Pros:
    - It's good (enough) if you want to get you hands dirty on multiple new programing language you're trying to learn (it has quite some to choose from, with Go as their most mature choice), at least that's half of the reason for me. I had lots of interesting learning/thinking about Go programing practices in the mean time.
    - The project is relatively small, so it should be good for junior engineers to try building more standalone projects with exposure of some level of system design knowledge, as a good supplement for their day job.
    - Since the project is small, you can manage to finish one project within 3-day free trail, and use another Github account for the next run (Given the charge is ridiculously high LOL)

Anyways, here's my code if you're interested: [KevinXuxuxu/codecrafters-redis-go](https://github.com/KevinXuxuxu/codecrafters-redis-go) (the README is generated and I didn't bother to change it) There're 4 projects (Redis, Docker, git, SQLite) in different languages available, so I'm thinking of doing the other 3 when I got time. Let's see if they can change my mind later.
