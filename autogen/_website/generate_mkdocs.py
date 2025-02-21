# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0


from pathlib import Path

from .utils import copy_files, get_git_tracked_and_untracked_files_in_directory


def filter_excluded_files(files: list[Path], exclusion_list: list[str], website_dir: Path) -> list[Path]:
    return [
        file
        for file in files
        if not any(str(file.relative_to(website_dir)).startswith(excl) for excl in exclusion_list)
    ]


def main() -> None:
    root_dir = Path(__file__).resolve().parents[2]
    website_dir = root_dir / "website"

    mint_inpur_dir = website_dir / "docs"
    mkdocs_output_dir = website_dir / "mkdocs" / "docs" / "docs"

    exclusion_list = ["docs/_blogs", "docs/home", "docs/.gitignore"]

    files_to_copy = get_git_tracked_and_untracked_files_in_directory(mint_inpur_dir)
    filtered_files = filter_excluded_files(files_to_copy, exclusion_list, website_dir)

    copy_files(mint_inpur_dir, mkdocs_output_dir, filtered_files)
