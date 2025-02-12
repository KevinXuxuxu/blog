import os
import sys
import mistune
import time

from collections import namedtuple, Counter
from flask.helpers import url_for
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
from typing import List, Tuple

ParsedPost = namedtuple(
    "ParsedPost",
    [
        "title",
        "path_title",
        "date",
        "tags",
        "category",
        "content",
        "enable_cosmo",
        "thumbnail",
    ],
)
_all_post_metadata_cache = None
_post_metadata_template = """---
title: {title}
date: {time}
tags: []
category: default
---
"""


class HighlightRenderer(mistune.HTMLRenderer):
    def decorated_highlight(self, code: str, lang: str) -> str:
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter(style="solarized-light")
        pygments_highlight = highlight(code, lexer, formatter)
        # get everything between <pre>
        i, j = (
            pygments_highlight.find("<pre>") + len("<pre>"),
            pygments_highlight.find("</pre>"),
        )
        code = pygments_highlight[i:j]
        # add <code> element to correct place
        i = len("<span></span>")
        code = code[:i] + "<code>" + code[i:] + "</code>"
        return f'''<div class="highlight">
    <pre class="code" data-lang="{lang}">{code}</pre>
</div>'''

    def block_code(self, code, info=None) -> str:
        if info:
            return self.decorated_highlight(code, info)
        return f"<pre><code>{mistune.escape(code)}</code></pre>"

    def block_html(self, html) -> str:
        return html

    def heading(self, text, level):
        tag = "h" + str(level)
        tid = text.lower().replace(" ", "_")
        link_icon = '<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 8 8"><path fill="currentColor" d="M5.88.03a1.9 1.9 0 0 0-.53.09c-.27.1-.53.25-.75.47a.5.5 0 1 0 .69.69c.11-.11.24-.17.38-.22c.35-.12.78-.07 1.06.22c.39.39.39 1.04 0 1.44l-1.5 1.5c-.44.44-.8.48-1.06.47c-.26-.01-.41-.13-.41-.13a.5.5 0 1 0-.5.88s.34.22.84.25c.5.03 1.2-.16 1.81-.78l1.5-1.5A1.98 1.98 0 0 0 6.44.07C6.26.03 6.06.03 5.88.04zm-2 2.31c-.5-.02-1.19.15-1.78.75L.6 4.59a1.98 1.98 0 0 0 0 2.81c.56.56 1.36.72 2.06.47c.27-.1.53-.25.75-.47a.5.5 0 1 0-.69-.69c-.11.11-.24.17-.38.22c-.35.12-.78.07-1.06-.22c-.39-.39-.39-1.04 0-1.44l1.5-1.5c.4-.4.75-.45 1.03-.44c.28.01.47.09.47.09a.5.5 0 1 0 .44-.88s-.34-.2-.84-.22z"/></svg>'
        link_anchor = f'<a class="hidden" tabindex="-1" href="#{tid}" style="font-size: .8rem">{link_icon}</a>'
        return f'''<{tag} id="{tid}">{text}&nbsp;{link_anchor}</{tag}>\n'''

    def image(self, alt, url, title=None):
        """
        title is repurposed to contain the following information separated by ;;
            caption, percent_width
        """
        d = {}
        if title:
            d = {i: v for i, v in enumerate(title.split(";;"))}
        caption = d.get(0, None)
        percent_width = d.get(1, 100)
        url = mistune.escape_url(url)
        alt = mistune.escape(alt)
        caption_html = (
            f'<em class="text-gray">{mistune.escape(caption)}</em>' if caption else ""
        )
        return f'<p style="text-align: center"><img class="my-resp-img" src="{url}" alt="{alt}" style="width: {percent_width}%"/><br>{caption_html}</p>'


def get_md_factory() -> "mistune.markdown.Markdown":
    return mistune.create_markdown(
        renderer=HighlightRenderer(), plugins=["strikethrough", "footnotes", "math"]
    )


def get_local_content(folder: str, path_title: str) -> str:
    with open("{}/{}.md".format(folder, path_title), "r") as f:
        return f.read()


def get_all_posts_with_metadata() -> List[ParsedPost]:
    global _all_post_metadata_cache
    if _all_post_metadata_cache is None:
        _all_post_metadata_cache = []
        for path in os.listdir("posts"):
            if not path.endswith(".md"):
                continue
            with open("posts/" + path, "r") as f:
                _all_post_metadata_cache.append(
                    parse_post_metadata(path[:-3], f.read())
                )
    return sorted(_all_post_metadata_cache, key=lambda p: p.date, reverse=True)


def get_all_tags(posts: List[ParsedPost]) -> List[str]:
    rtn = set()
    for p in posts:
        for t in p.tags:
            rtn.add(t)
    return sorted(list(rtn))


def get_top_k_tags(posts: List[ParsedPost], K: int) -> List[str]:
    tags = Counter()
    for p in posts:
        for t in p.tags:
            tags[t] += 1
    sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
    return [tag[0] for tag in sorted_tags[:K]]


def gen_post_md(path_title: str) -> str:
    return "- [{}]({})".format(path_title, url_for("post", path_title=path_title))


def parse_attribute(line: str) -> Tuple[str, str]:
    parts = line.split(": ")
    return parts[0], ": ".join(parts[1:])


def parse_post_metadata(path_title: str, md: str) -> ParsedPost:
    parts = md.split("---\n")
    metadata_str, content = parts[1], "---\n".join(parts[2:])
    metadata = {
        "content": content,
        "path_title": path_title,
        "enable_cosmo": False,
        "thumbnail": None,
    }
    for line in metadata_str.strip().split("\n"):
        key, value = parse_attribute(line)
        if key == "tags":
            metadata["tags"] = eval(value.strip())
        else:
            metadata[key] = value.strip()
    return ParsedPost(**metadata)


def gen_new_post(title: str):
    path_title = title.replace(" ", "-")
    with open(f"posts/{path_title}.md", "w") as f:
        f.write(
            _post_metadata_template.format(
                title=title, time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            )
        )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("supported verbs: new")
    elif sys.argv[1] == "new":
        if len(sys.argv) != 3:
            print("e.g. python3 utils.py new <title>")
        else:
            gen_new_post(sys.argv[2])
