"""
text-annotation-tool

A lightweight text annotation tool for annotating spans of text with custom tags and attributes.

Author: Toni Golian
License: MIT
"""

import argparse

from utils.app_builder import AppBuilder


def parse_args() -> argparse.Namespace:
    """
    Parses command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Start the text annotation tool."
    )

    frontend_group = parser.add_mutually_exclusive_group()

    frontend_group.add_argument(
        "-tkinter",
        "--tkinter",
        action="store_const",
        const="tkinter",
        dest="frontend",
        help="Start the Tkinter frontend.",
    )

    frontend_group.add_argument(
        "-pyside",
        "--pyside",
        action="store_const",
        const="pyside",
        dest="frontend",
        help="Start the PySide6 frontend.",
    )

    parser.set_defaults(frontend="pyside")

    return parser.parse_args()


def main() -> None:
    """
    Application entrypoint.
    """
    args = parse_args()
    app_builder = AppBuilder()

    if args.frontend == "tkinter":
        app_builder.run_tkinter_app()
        return

    if args.frontend == "pyside":
        app_builder.run_pyside_app()
        return

    raise ValueError(f"Unsupported frontend: {args.frontend}")


if __name__ == "__main__":
    main()