---
title: Dark Mode Support
date: 2024-03-07 07:33:14
tags: ["frontend", "CSS", "Javascript", "npm"]
category: tech
thumbnail: /static/image/dark_mode_thumbnail.png
---
Recently I have been doing quite some frontend development involving improvement of my [blog](https://github.com/KevinXuxuxu/blog) framework as well as some new side projects (specifically [OpenCoder](https://github.com/KevinXuxuxu/opencoder) but I'll save it for a separate post). As a system/infra engineer I have always had a mixed feeling about frontend developing: they're both fascinating and boring, both super exciting when you make it right, and mindlessly dull when you fail. So here's a short post about my recent experience with too much detail that no one wants to read about.

#### The Dark Mode 🌒

I have always wanted dark mode for my site, because deep down I'm dark and evil person.

No, but seriously. I have everything in dark mode if possible and I feel like being flashbombed every time I have to open something without dark mode (like Google spreadsheet). So of course I want my own site to be more pleasant to read, at least for myself.

So a very brief intro about my blog framework: Getting inspired by [Death and Gravity](https://death.andgravity.com/about)[^1] I built this static site generator that enables you to write simple markdown, populate decent blog post and publish to Github.io. It uses [Mistune](https://mistune.lepture.com/en/latest/) for markdown rendering, [Pygments](https://pygments.org/docs/quickstart/) for code syntax highlighting, [Spectre.css](https://picturepan2.github.io/spectre/index.html) for frontend styling (this part is important and will be covered in test) and [Flask](https://flask.palletsprojects.com/en/3.0.x/quickstart/) + [Frozen Flask](https://frozen-flask.readthedocs.io/en/latest/) to host and populate the static site pages.

[^1]: What Adrian had is of course much more sophisticated, while my framework is built as simply as possible and specifically suits my requirements and habit, or you could say it's "opinionated".

I have been happily using this framework for a few years now, but my work is mostly on the backend side (markdown rendering, hosting, tooling, etc.). The frontend is mostly left as is, given that Spectre.css is pretty and simple enough for my aesthetics.

Unfortunately it doesn't support dark mode. And since it has been idle (abandoned?) for almost 4 years ([last commit](https://github.com/picturepan2/spectre/commit/8847251d71b4dac27e8407cbdb71ae89ce156a43)), I don't expect it to be supported anytime soon. There're some others forking the repo and making their own dark mode, but I still prefer the path of learning and making a dark mode myself.

#### Spectre.css

So the plan is simple: fork and clone the repo, try to compile it, read and understand it just enough to know the key part that controls the colors, and configure it using a beautiful dark mode pallet. So as suggested in the [doc](https://picturepan2.github.io/spectre/getting-started/custom.html), I used the npm of god knows what version I have on my mac and did `npm install`, and it failed without any surprise.

After struggling for a few hours[^2], I had to build my own dev container and finally successfully compiling it. Here's the [Dockerfile](https://github.com/KevinXuxuxu/spectre/blob/master/Dockerfile) in case anyone want to quickly compile a customized version of it. The compiling is simple, it uses [gulp.js](https://gulpjs.com/docs/en/getting-started/quick-start) to compile and make a distribution of css files of different purpose and size. Actually quite convenient.

[^2]: As an infra engineer, I first tried to build it in an [official node docker container](https://hub.docker.com/_/node/tags) and there are so many of them! They are so large that I'm reluctant to keep as a dev env, and they mostly don't work (🌚) because (I'm guessing) some old dependency of Spectre css is depending on Python 2.7 which is on none of the official images.

Now that I can safely dive into the codebase, here's some naive take from an amateur of frontend engineering. The source code are in the `src` folder, which contains lots of `.scss` files with relatively flat structure. My analogy is that css is like a sort of configuration language for styles; and [scss](https://sass-lang.com/) is like a more flexible, or a templating language which allows you to some crazy stuff (define variable, control flow, ...) and finally compile to css. Just like [Jsonnet](https://jsonnet.org/) or GCL[^3], which I'm fairly familiar with (but not too proud of)!

[^3]: Google Configuration Language, internally used by Google. Fun fact: infra engineers spend more time juggling configurations than writing actual code.

With some simple search I found the key file: [_variable.scss](https://github.com/picturepan2/spectre/blob/master/src/_variables.scss), which contains all the color definition, along with some other important stuff like fonts and sizes.

```css
...
// Core colors
$primary-color: #5755d9 !default;
$primary-color-dark: darken($primary-color, 3%) !default;
$primary-color-light: lighten($primary-color, 3%) !default;
$secondary-color: lighten($primary-color, 37.5%) !default;
$secondary-color-dark: darken($secondary-color, 3%) !default;
$secondary-color-light: lighten($secondary-color, 3%) !default;

// Gray colors
$dark-color: #303742 !default;
$light-color: #fff !default;
$gray-color: lighten($dark-color, 55%) !default;
$gray-color-dark: darken($gray-color, 30%) !default;
$gray-color-light: lighten($gray-color, 20%) !default;

$border-color: lighten($dark-color, 65%) !default;
$border-color-dark: darken($border-color, 10%) !default;
$border-color-light: lighten($border-color, 8%) !default;
$bg-color: lighten($dark-color, 75%) !default;
$bg-color-dark: darken($bg-color, 3%) !default;
$bg-color-light: $light-color !default;

// Control colors
$success-color: #32b643 !default;
$warning-color: #ffb700 !default;
$error-color: #e85600 !default;

// Other colors
$code-color: #d73e48 !default;
$highlight-color: #ffe9b3 !default;
$body-bg: $bg-color-light !default;
$body-font-color: lighten($dark-color, 5%) !default;
$link-color: $primary-color !default;
$link-color-dark: darken($link-color, 10%) !default;
$link-color-light: lighten($link-color, 10%) !default;
...
```

Apparently scss has some [builtin color functions](https://sass-lang.com/documentation/modules/color/) that compute the rest of the colors from some basic colors. But the way it computes here seems pretty arbitrary. It might work if you want to change a key color e.g. from purple-ish to blue-ish, but probably not going to work with dark mode.

![fail_dark_mode](/static/image/fail_dark_mode.png "Trust me, I tried")

To construct a customized dark mode pallet I choose to base off of [Penumbra](https://github.com/nealmckee/penumbra) color theme which is what I'm using for all my dev environments. It is very nice that they have all the color values listed [here](https://github.com/nealmckee/penumbra/blob/main/penumbra.tsv) to easily choose from. The objective is to use Penumbra as a reference but still keep the flavor and harmonic with the default Spectre color configuration. The result I came up with is just like this page if you switch to dark mode from up-right corner. It might need a little final touch but it's good enough for now.

#### The Switch

I'm talking about the little switch I used to switch between dark and light mode, not the Nintendo one. So it controls a simple binary state of the page, I've done this a few times before with JS so it should be fairly easy. The basic requirements are:
- Switch the css source file of the page.
- Know the current state of the page.
- Keep the state across refresh

The first 2 are pretty basic, but the 3rd one need some cookie handling. Basically cookie is this piece of memory (?) that is persistent between different pages, sites and browser sessions. It's quite confusing because when you write and read cookie, you do both in the form of string. But they are **not the same string**! The string you constructed when setting a cookie looks like this:
```javascript
document.cookie =
    "color_theme=dark; expires=Mon, 08 Apr 2024 05:12:10 GMT; path=/";
```
The actual key and value are in the front, followed by expiration and scope of effect. And to read the cookie, you parse the **exact same variable**
```javascript
console.log(document.cookie);
// color_theme=dark
```
This is very confusing because to anyone without frontend experience, this looks like the same variable! But in fact the `document.cookie` is just a sort of API for you to set and get cookies in the form of strings, and it doesn't work as it seems.

Anyways, I whipped up some rough JS on to a generic switch element from Spectre form components and here we are. I also added a pair of symmetrical moon emoji (🌒/🌖) to make it a bit cuter :)

There's still a bunch of work to do[^4] but that's mostly it. Hope you enjoyed and happy hacking!

[^4]: Mostly color adjustments for chip elements, code block, ... Also when you are in dark mode and going to a new page, the screen will quickly flash depending on the loading speed, and I don't have a very good solution yet. May be I'll have to use the `data-theme="dark"` approach ([ref](https://github.com/coliff/dark-mode-switch?tab=readme-ov-file#how-it-works)) instead of css switching, which involves much more complex change into Spectre's codebase.

*2024-09-01 Update*: [Followup blog](/blog/post/Dark-Mode-Support-%28Cont.%29/)