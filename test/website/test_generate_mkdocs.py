# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from autogen._website.generate_mkdocs import filter_excluded_files


def test_exclude_files() -> None:
    files = [
        Path("/tmp/ag2/ag2/website/docs/user-guide/advanced-concepts/groupchat/groupchat.mdx"),
        Path("/tmp/ag2/ag2/website/docs/_blogs/2023-04-21-LLM-tuning-math/index.mdx"),
        Path("/tmp/ag2/ag2/website/docs/home/home.mdx"),
        Path("/tmp/ag2/ag2/website/docs/home/quick-start.mdx"),
    ]

    exclusion_list = ["docs/_blogs", "docs/home"]
    website_dir = Path("/tmp/ag2/ag2/website")

    actual = filter_excluded_files(files, exclusion_list, website_dir)
    expected = [files[0]]
    assert actual == expected
