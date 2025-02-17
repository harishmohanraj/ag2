# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

import shutil
import subprocess
from pathlib import Path


def get_git_tracked_files_in_directory(directory: Path) -> set[Path]:
    """Get all files in the directory that are tracked by git."""
    proc = subprocess.run(["git", "-C", str(directory), "ls-files"], capture_output=True, text=True, check=True)
    return {directory / p for p in proc.stdout.splitlines()}


def copy_only_git_tracked_files(src_dir: Path, dst_dir: Path) -> None:
    """Copy only the files that are tracked by git from src_dir to dst_dir."""
    git_tracked_files_in_website_dir = get_git_tracked_files_in_directory(src_dir)
    for src in git_tracked_files_in_website_dir:
        if src.is_file():
            dst = dst_dir / src.relative_to(src_dir)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
