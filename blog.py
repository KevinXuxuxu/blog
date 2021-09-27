import base64
import requests
import mistune

from flask import Flask, render_template_string

GITHUB_REPO_CONTENT_API = 'https://api.github.com/repos/{repo}/contents/{path}'

def get_github_content(repo: str, path: str) -> str:
    resp = requests.get(GITHUB_REPO_CONTENT_API.format(repo=repo, path=path))
    encoded_content = resp.json()['content']
    return base64.b64decode(encoded_content).decode()

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<link rel="stylesheet" href="https://unpkg.com/spectre.css/dist/spectre.min.css">
</head>
<body>
<main class="content columns">
<div class="column col-sm-12 col-md-10 col-8">
{}
</div>
</main>
</body>
'''


app = Flask(__name__)

@app.route("/")
def hello_world():
    md = get_github_content('KevinXuxuxu/NN', 'README.md')
    md_factory = mistune.create_markdown()
    html = md_factory(md)
    return render_template_string(HTML_TEMPLATE.format(html))
