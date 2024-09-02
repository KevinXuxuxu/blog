---
title: Dark Mode Support (Cont.)
date: 2024-08-25 20:32:16
tags: ["frontend", "CSS", "Javascript", "Sass"]
category: tech
---

My previous version of [dark mode support](/blog/post/dark_mode_support/) is not very satisfactory: the color scheme is not very crafted, refreshing page under dark mode gives a blink of light color which is annoying, and switching between two CSS files is just pure ugly. With a bit more research, I realized that the standard way of supporting multiple "themes" in frontend is usually done by switching between `data-theme` on the document, with different styles defined separately in a single CSS file[^2]. Something like this:

```css
a {
  color: #807fe2;
}
[data-theme="dark"] a {
  color: #8c8cf3;
}
```

[^2]: I also did the same for the [`pygments_style.css`](https://github.com/KevinXuxuxu/blog/blob/main/static/style/pygments_style.css) file, which is for code block syntax highlighting and also needed some adjustments for dark mode.

#### Spectre.css

The initial plan was simple: all colors are defined in `_variables.scss` file, I should find a way to assign different values to them under different values of `data-theme` and it should just magically work. I couldn't be more wrong.

There are actually 2 types of variables we're dealing with here:
- [Native CSS variable](https://developer.mozilla.org/en-US/docs/Web/CSS/--*): look something like this `--background-color`, which you should see a lot when you inspect element on any web page. They are live in the browser and can be controlled by `data-theme`. I understand them as "run-time variable".
- [Sass variable](https://sass-lang.com/documentation/variables/): looks like this `$background_color` and they only work in Sass files. They are like "compile-time variable" and will be gone after we build the project into result CSS.

Spectre.css only has one color theme, and doesn't have built in multi-theme support. As a result it only uses Sass variables all over the project and theres no way to switch Sass variable with `data-theme`. So some sort of heavy refactoring is needed, to say the least.

##### How about just use CSS variables?

What if we replace all the Sass variables with CSS variables? A full-dir search and replace should do it.

**No**. Spectre uses Sass variables throughout the projects and there're derivatives (one Sass variable's value computed from another one) and some functions that doesn't work with native CSS variables (like `darken` and `lighten`).

The use of Sass variables basically shuts off the possibility to control that from the "source" of all colors (`_variables.scss`), and we have to work on the result side. This inevitably complicates the procedure of producing the wanted results (e.g. needs two `gulp build` not one) but that seems to be the only reasonable way now.

##### Git diff and Python script

It was pretty late into the night when I arrive here. For the very few brain cells I have left, this is the most feasible plan:

- Given that I already have "dark mode" theme configured in my [forked repo](https://github.com/KevinXuxuxu/spectre), go to the main branch of the original Spectre.css repo (which is "light mode") and overwrite (back) the `_variables.scss` and `_codes.scss` file. (I just use [this commit](https://github.com/KevinXuxuxu/spectre/commit/b4271cca15646230cc8fa719c8a76a1e2aa84b47#diff-0f46db35f1104d0c9d2ba6728b66154a55bca36a01869b5263d2b2eb695bdeab))
- `gulp build` to generate result CSS for light mode.
- `git diff dist/spectre.css > tmp.diff` to get the diff between light and dark mode in the results, and store in `tmp.diff` file.
- Write a script to read the diff file and the current result file (`dist/spectre.css`), produce a "merged version" so that everywhere there's a color difference, we split the parent section into light and dark version.

[The script](https://github.com/KevinXuxuxu/spectre/blob/master/merge_css.py) is available in my forked repo and is fairly straight forward.

The first step is to read the diff file and get all the contiguous diff information. The script reads line by line in the diff file, using regex match for lines starting with `@@` to align line number from original file. for a segment of diff file like this:
```diff
...
@@ -286,8 +286,8 @@ html {
 }
 
 body {
-  background: #24272b;
-  color: #d5d5d5;
+  background: #fff;
+  color: #3b4351;
   font-family: -apple-system, system-ui, "Segoe UI";
   font-size: .8rem;
   overflow-x: hidden;
@@ -295,25 +295,25 @@ body {
 }
...
```
It should produce an item in the result dictionary:
```python
{
    '289': (
        ['289', '290'],  # skip
        ['  background: #24272b;', '  color: #d5d5d5;']  # rep
    )
}
```
The key is the first line number of this contiguous diff in the current file version (light mode), the value consists of 2 parts
- All the line numbers of this contiguous diff in the current file version (light mode), parsed from lines starting with `+`
- All the line contents of this contiguous diff in the old file version (dark mode), parsed from lines starting with `-`

Note that we're only recording the line numbers instead of contents for light mode, because the content already presents in the current file we will be reading.

Second step is to read the current file (`dist/spectre.css`), identify CSS sections with diff (from result dict of previous step) and produce 2 versions, with and without `[data-theme="dark"]`. Since the CSS file has very fixed format, I can easily identify section ends with matching `}` lines.

For each parsed section, we use the following state machine[^1] to process and produce result:
![state_machine](/static/image/state_machine.png "Simple State Machine to Generate Alternate Section (for dark mode);;70")

Finally if the alternate buffer is the same as the original section, meaning that state machine stayed in `NORMAL` all the time and there's no diff, we'll just output the original section; otherwise, we append `[data-theme="dark"]` to the alternate buffer and output that as well.

[^1]: The notion of state machine is actually very profound and powerful in solving many complex computer system problems. The first step is actually also able to be represented as a state machine, just that it's simple enough to be handled without explicit definition. Once I was being interviewed for system design, and it was about using state machine to concurrently parse huge JSON files. Very interesting problem for a separate post :)

#### The Blink Issue

Previously I thought that the blink when refreshing page in dark mode is purely caused by switching between 2 CSS files instead of using `data-theme`. But after I got the result from previous script, it still blinks. Apparently the issue is caused by the time I actually start to use the correct theme.

Previously I make the theme selection with `window.onload` which is obviously too late. It gets very bad with my [previous post](/blog/post/cosmo:-3D-Graphics-Engine-in-Terminal/) which contains an 11Mb GIF. It's not a blink but full light mode before all resources are loaded.

As a result, I made a bunch of changes on the [color_theme.js](https://github.com/KevinXuxuxu/blog/blob/main/static/script/color_theme.js) script, including switching theme with
```javascript
document.documentElement.setAttribute('data-theme', color_theme);
```
and doing that early in the header to resolve the blink issue. I also have the switch state and an emoji (🌒/🌖), so I isolated that logic, and bind with the loading of these elements (more accurately their parent `label` element):
```javascript
document.addEventListener("DOMContentLoaded", function() {
    const element = document.getElementById("color-switch");
    if (element) {
        init_color_switch();
    }
});
```
And now it's working perfectly, yay.

#### (Maybe) Future Work

Since it now in a pretty decent state, it's not likely that I will spend more time on this recently. But for something to be improved, there's probably a smart way to create a "function" of some sort in Sass so that it automatically generate 2 versions of a section when color theme support is needed. That will save me from all that procedure, and bring the logic back to the source.

Hope you enjoyed my poor writing and until next time :)
