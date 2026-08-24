from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def register(registry: Any, *, working_dir: str | Path) -> None:
    root = Path(working_dir).expanduser().resolve()

    def resolve(path: object) -> Path | str:
        candidate = (root / str(path)).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            return f"error: path '{path}' escapes the working directory"
        return candidate

    def error(message: object) -> str:
        return f"error: {message}"

    registry.tool("pwd", description="Return the working directory — the root that all file paths are relative to.", parameters={}, block=lambda: str(root))

    def list_directory(path: str = ".") -> str:
        target = resolve(path)
        if isinstance(target, str):
            return target
        if not target.is_dir():
            return error(f"'{path}' is not a directory")
        entries = sorted(
            f"{item.name}/" if item.is_dir() else item.name
            for item in target.iterdir()
        )
        return "(empty)" if not entries else "\n".join(entries)

    registry.tool("list_directory", description="List files and subdirectories at a path relative to the working directory. Defaults to the working directory itself.", parameters={"path": {"type": "string", "description": "Relative path to list (default '.')"}}, block=list_directory)

    def read_file(path: str) -> str:
        target = resolve(path)
        if isinstance(target, str):
            return target
        if not target.is_file():
            return error(f"'{path}' is not a file")
        try:
            return target.read_text()
        except Exception as exc:
            return error(exc)

    registry.tool("read_file", description="Read and return the full contents of a file. Path is relative to the working directory.", parameters={"path": {"type": "string", "description": "Relative path to the file"}}, block=read_file)

    def write_file(path: str, content: str) -> str:
        target = resolve(path)
        if isinstance(target, str):
            return target
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
            relative = target.relative_to(root)
            return f"ok: wrote {len(content.encode())} bytes to {relative}"
        except Exception as exc:
            return error(exc)

    registry.tool("write_file", description="Write content to a file, creating parents if needed and overwriting existing content.", parameters={"path": {"type": "string", "description": "Relative path to the file"}, "content": {"type": "string", "description": "Text content to write"}}, block=write_file)

    def delete_file(path: str) -> str:
        target = resolve(path)
        if isinstance(target, str):
            return target
        if not target.is_file():
            return error(f"'{path}' is not a file")
        try:
            target.unlink()
            return f"ok: deleted {path}"
        except Exception as exc:
            return error(exc)

    registry.tool("delete_file", description="Delete a file. Directories are not deleted. Path is relative to the working directory.", parameters={"path": {"type": "string", "description": "Relative path to the file to delete"}}, block=delete_file)

    def search_files(pattern: str, path: str = ".", glob: str = "*") -> str:
        target = resolve(path)
        if isinstance(target, str):
            return target
        if target.is_file():
            files = [target]
        elif target.is_dir():
            files = sorted(target.glob(f"**/{glob}"))
        else:
            return error(f"'{path}' is not a file or directory")
        try:
            regex = re.compile(pattern)
        except re.error as exc:
            return error(f"invalid pattern: {exc}")
        matches: list[str] = []
        for file in files:
            if not file.is_file():
                continue
            relative = file.relative_to(root)
            try:
                for line_number, line in enumerate(file.read_text().splitlines(), 1):
                    if regex.search(line):
                        matches.append(f"{relative}:{line_number}:{line}")
            except Exception as exc:
                matches.append(f"{relative}: error reading file: {exc}")
        return "no matches" if not matches else "\n".join(matches)

    registry.tool("search_files", description="Search for a text pattern across files in the working directory tree.", parameters={"pattern": {"type": "string", "description": "The text or regex pattern"}, "path": {"type": "string", "description": "Subdirectory or file (default '.')"}, "glob": {"type": "string", "description": "File glob (default '*')"}}, block=search_files)
