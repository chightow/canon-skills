"""Project context utilities for resolving the project root path."""

from pathlib import Path


def find_project_root(start_path: Path) -> Path:
    """Find the project root by walking up from *start_path* looking for a `.canon` marker.

    Args:
        start_path: The starting directory path to search from.

    Returns:
        The resolved `Path` of the project root.

    Raises:
        ValueError: If *start_path* is not a valid directory or not within the workspace.
    """
    start_path = Path(start_path).resolve()

    if not start_path.is_dir():
        raise ValueError(f"'{start_path}' is not a valid directory")

    # Walk up directories looking for .canon marker
    current = start_path
    while True:
        canon_marker = current / ".canon"
        if canon_marker.is_file():
            return canon_marker.parent.resolve()
        parent = current.parent
        if parent == current:
            # Reached filesystem root, return best effort (parent of input)
            return start_path.parent.resolve()
        current = parent

    return start_path.resolve()


if __name__ == "__main__":
    import sys

    root = find_project_root(Path("."))
    print(f"Project root: {root}")
