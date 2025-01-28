import pytest
from unittest.mock import mock_open, patch, MagicMock, call
from datetime import datetime
import os
import time
from flask import Flask

import utils
from utils import ParsedPost, HighlightRenderer
from app import app


@pytest.fixture
def valid_metadata():
    return """---
title: Test Post
date: 2024-01-01 12:00:00
tags: ["python", "testing"]
category: tech
---
Test content here
"""


@pytest.fixture
def minimal_metadata():
    return """---
title: Minimal Post
date: 2024-01-01 12:00:00
tags: []
category: default
---
Content
"""


@pytest.fixture
def mock_posts_dir():
    return [
        "post1.md",
        "post2.md",
        ".DS_Store",  # Should be ignored
        "invalid.txt",  # Should be ignored
    ]


# Test ParsedPost creation and metadata parsing
def test_parse_post_metadata_complete(valid_metadata):
    result = utils.parse_post_metadata("test-post", valid_metadata)
    assert isinstance(result, ParsedPost)
    assert result.title == "Test Post"
    assert result.path_title == "test-post"
    assert result.date == "2024-01-01 12:00:00"
    assert result.tags == ["python", "testing"]
    assert result.category == "tech"
    assert result.content == "Test content here\n"
    assert result.enable_cosmo is False


def test_parse_post_metadata_minimal(minimal_metadata):
    result = utils.parse_post_metadata("minimal-post", minimal_metadata)
    assert result.title == "Minimal Post"
    assert result.tags == []
    assert result.category == "default"
    assert result.enable_cosmo is False


def test_parse_post_metadata_invalid():
    invalid_metadata = "No metadata section"
    with pytest.raises(IndexError):
        utils.parse_post_metadata("invalid", invalid_metadata)


# Test HighlightRenderer
def test_block_code_with_language():
    renderer = HighlightRenderer()
    code = 'print("Hello, World!")'
    result = renderer.block_code(code, "python")
    assert '<div class="highlight">' in result
    assert '<pre class="code" data-lang="python">' in result
    assert "Hello, World!" in result


def test_block_code_without_language():
    renderer = HighlightRenderer()
    code = 'print("Hello")'
    result = renderer.block_code(code, None)
    assert "<pre><code>" in result
    # Check for HTML-escaped version
    assert "print(&quot;Hello&quot;)" in result


def test_heading_with_anchor():
    renderer = HighlightRenderer()
    result = renderer.heading("Test Heading", 2)
    assert '<h2 id="test_heading">' in result
    assert 'href="#test_heading"' in result
    assert "Test Heading" in result


def test_image_with_caption():
    renderer = HighlightRenderer()
    result = renderer.image("alt text", "image.jpg", "Caption;;50")
    assert "width: 50%" in result
    assert 'class="text-gray">Caption</em>' in result
    assert 'src="image.jpg"' in result


def test_image_without_caption():
    renderer = HighlightRenderer()
    result = renderer.image("alt text", "image.jpg")
    assert "width: 100%" in result
    assert "text-gray" not in result


# Test post management functions
def test_get_all_posts_with_metadata(mock_posts_dir):
    mock_data = """---
title: Test
date: 2024-01-01 12:00:00
tags: []
category: default
---
content"""

    with (
        patch("os.listdir", return_value=mock_posts_dir),
        patch("builtins.open", mock_open(read_data=mock_data)),
    ):
        posts = utils.get_all_posts_with_metadata()
        assert len(posts) == 2  # Only .md files
        assert all(isinstance(p, ParsedPost) for p in posts)


def test_get_all_posts_caching(mock_posts_dir):
    mock_data = """---
title: Test
date: 2024-01-01 12:00:00
tags: []
category: default
---
content"""

    with (
        patch("os.listdir") as mock_listdir,
        patch("builtins.open", mock_open(read_data=mock_data)),
    ):
        mock_listdir.return_value = mock_posts_dir
        # Clear cache
        utils._all_post_metadata_cache = None
        # First call
        posts1 = utils.get_all_posts_with_metadata()
        # Second call should use cache
        posts2 = utils.get_all_posts_with_metadata()

        # Verify listdir was only called once (caching worked)
        assert mock_listdir.call_count == 1


# Test tag handling
def test_get_all_tags():
    posts = [
        ParsedPost("Post1", "", "", ["tag1", "tag2"], "", "", False),
        ParsedPost("Post2", "", "", ["tag2", "tag3"], "", "", False),
    ]
    tags = utils.get_all_tags(posts)
    assert sorted(tags) == ["tag1", "tag2", "tag3"]


def test_get_top_k_tags():
    posts = [
        ParsedPost("Post1", "", "", ["tag1", "tag2"], "", "", False),
        ParsedPost("Post2", "", "", ["tag2", "tag3"], "", "", False),
        ParsedPost("Post3", "", "", ["tag2"], "", "", False),
    ]
    tags = utils.get_top_k_tags(posts, 2)
    # Only check the most frequent tag since order of equal-frequency tags may vary
    assert tags[0] == "tag2"  # tag2 has highest frequency
    assert len(tags) == 2


# Test new post generation
def test_gen_new_post():
    mock_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    with (
        patch("builtins.open", mock_open()) as mock_file,
        patch("time.strftime", return_value=mock_time),
    ):
        utils.gen_new_post("Test Title")

        # Verify file was created with correct name
        mock_file.assert_called_once_with("posts/Test-Title.md", "w")

        # Verify content
        written_content = mock_file().write.call_args[0][0]
        assert "title: Test Title" in written_content
        assert mock_time in written_content


# Test URL generation
def test_gen_post_md():
    with app.test_request_context():
        result = utils.gen_post_md("test-post")
        assert "[test-post]" in result
        assert "(/blog/post/test-post/)" in result


# Test attribute parsing
def test_parse_attribute():
    key, value = utils.parse_attribute("title: Hello: World")
    assert key == "title"
    assert value == "Hello: World"


def test_parse_attribute_with_multiple_colons():
    key, value = utils.parse_attribute("time: 12:30:45")
    assert key == "time"
    assert value == "12:30:45"
