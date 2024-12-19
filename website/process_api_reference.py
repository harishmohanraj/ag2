# Copyright (c) 2023 - 2024, Owners of https://github.com/ag2ai
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT
#!/usr/bin/env python

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, List, Optional


def run_pydoc_markdown(config_file: Path) -> None:
    """Run pydoc-markdown with the specified config file.

    Args:
        config_file (Path): Path to the pydoc-markdown config file
    """
    try:
        subprocess.run(["pydoc-markdown"], check=True, capture_output=True, text=True)
        print(f"Successfully ran pydoc-markdown with config: {config_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error running pydoc-markdown: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("pydoc-markdown not found. Please install it with: pip install pydoc-markdown")
        sys.exit(1)


def escape_html_tags(content: str) -> str:
    """Escape all angle brackets < > in the content.

    Args:
        content (str): Input text content

    Returns:
        str: Content with all angle brackets escaped
    """
    return content.replace("<", r"\<").replace("{", r"\{")


def read_file_content(file_path: str) -> str:
    """Read content from a file.

    Args:
        file_path (str): Path to the file

    Returns:
        str: Content of the file
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file_content(file_path: str, content: str) -> None:
    """Write content to a file.

    Args:
        file_path (str): Path to the file
        content (str): Content to write
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def add_code_fences(content: str) -> str:
    """Add Python code fence markers to content starting with 'import'.

    Args:
        content: Content to process
    Returns:
        Content with Python code blocks properly fenced
    """
    return content
    lines = content.split("\n")
    output = []
    i = 0

    while i < len(lines):
        if lines[i].strip().startswith("import"):
            block = []
            # Collect lines until next markdown marker
            while i < len(lines) and not lines[i].strip().startswith(("---", "#", "-", "`")):
                block.append(lines[i])
                i += 1
            if block:
                output.extend(["```python", *block, "```"])
        else:
            output.append(lines[i])
            i += 1

    return "\n".join(output)


def convert_md_to_mdx(input_dir: Path) -> None:
    """Convert all .md files in directory to .mdx while preserving structure.

    Args:
        input_dir (Path): Directory containing .md files to convert
    """
    if not input_dir.exists():
        print(f"Directory not found: {input_dir}")
        sys.exit(1)

    for md_file in input_dir.rglob("*.md"):
        mdx_file = md_file.with_suffix(".mdx")

        # Read content from .md file
        content = md_file.read_text(encoding="utf-8")

        # Escape HTML tags
        processed_content = escape_html_tags(content)

        # Add code fences
        processed_content = add_code_fences(processed_content)

        # Update sidenav title
        processed_content = processed_content.replace("sidebar_label: ", "sidebarTitle: ")

        # Write content to .mdx file
        mdx_file.write_text(processed_content, encoding="utf-8")

        # Remove original .md file
        md_file.unlink()
        print(f"Converted: {md_file} -> {mdx_file}")


def get_mdx_files(directory: Path) -> List[str]:
    """Get all MDX files in directory and subdirectories."""
    return [f"{str(p.relative_to(directory).with_suffix(''))}".replace("\\", "/") for p in directory.rglob("*.mdx")]


def add_prefix(path: str, parent_groups: List[str] = None) -> str:
    """Create full path with prefix and parent groups."""
    groups = parent_groups or []
    return f"docs/reference/{'/'.join(groups + [path])}"


def create_nav_structure(paths: List[str], parent_groups: List[str] = None) -> List[Any]:
    """Convert list of file paths into nested navigation structure."""
    groups = {}
    pages = []
    parent_groups = parent_groups or []

    for path in paths:
        parts = path.split("/")
        if len(parts) == 1:
            pages.append(add_prefix(path, parent_groups))
        else:
            group = parts[0]
            subpath = "/".join(parts[1:])
            groups.setdefault(group, []).append(subpath)

    # Sort directories and create their structures
    sorted_groups = [
        {
            "group": ".".join(parent_groups + [group]) if parent_groups else group,
            "pages": create_nav_structure(subpaths, parent_groups + [group]),
        }
        for group, subpaths in sorted(groups.items())
    ]

    # Sort pages
    sorted_pages = sorted(pages)

    # Return directories first, then files
    return sorted_groups + sorted_pages


def update_nav(mint_json_path: Path, new_nav_pages: List[Any]) -> None:
    """
    Update the 'API Reference' section in mint.json navigation with new pages.

    Args:
        mint_json_path: Path to mint.json file
        new_nav_pages: New navigation structure to replace in API Reference pages
    """
    try:
        # Read the current mint.json
        with open(mint_json_path, "r") as f:
            mint_config = json.load(f)

        # Find and update the API Reference section
        for section in mint_config["navigation"]:
            if section.get("group") == "API Reference":
                section["pages"] = new_nav_pages
                break

        # Write back to mint.json with proper formatting
        with open(mint_json_path, "w") as f:
            json.dump(mint_config, f, indent=2)
            f.write("\n")

    except json.JSONDecodeError:
        print(f"Error: {mint_json_path} is not valid JSON")
    except Exception as e:
        print(f"Error updating mint.json: {e}")


def update_mint_json_with_api_nav(script_dir: Path, api_dir: Path) -> None:
    """Update mint.json with MDX files in the API directory."""
    mint_json_path = script_dir / "mint.json"
    if not mint_json_path.exists():
        print(f"File not found: {mint_json_path}")
        sys.exit(1)

    # Get all MDX files in the API directory
    mdx_files = get_mdx_files(api_dir)

    # Create navigation structure
    nav_structure = create_nav_structure(mdx_files)

    # Update mint.json with new navigation
    update_nav(mint_json_path, nav_structure)


def main() -> None:
    script_dir = Path(__file__).parent.absolute()

    parser = argparse.ArgumentParser(description="Process API reference documentation")
    parser.add_argument("--config", type=Path, help="Path to pydoc-markdown config file", default=script_dir)
    parser.add_argument(
        "--api-dir",
        type=Path,
        help="Directory containing API documentation to process",
        default=script_dir / "docs" / "reference",
    )

    args = parser.parse_args()

    # Run pydoc-markdown
    print("Running pydoc-markdown...")
    run_pydoc_markdown(args.config)

    # Convert MD to MDX
    print("Converting MD files to MDX...")
    convert_md_to_mdx(args.api_dir)

    # Update mint.json
    update_mint_json_with_api_nav(script_dir, args.api_dir)

    print("API reference processing complete!")


if __name__ == "__main__":
    main()