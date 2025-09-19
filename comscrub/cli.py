from __future__ import annotations

import argparse
import sys
from typing import List, Sequence

from .core import scrub_file, _detect_language_from_extension


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="comscrub",
        description="Strip comments from C-family source files using libclang.",
    )
    parser.add_argument("files", nargs="+", help="Input files to process")
    parser.add_argument(
        "-i",
        "--inplace",
        action="store_true",
        help="Rewrite files in place (default prints to stdout)",
    )
    parser.add_argument(
        "-x",
        "--language",
        choices=["c", "c++", "objective-c", "objective-c++", "cuda"],
        help="Explicit language to parse with clang (-x)",
    )
    parser.add_argument(
        "--clang-arg",
        dest="clang_args",
        action="append",
        default=[],
        help="Additional argument to forward to clang (repeatable)",
    )
    parser.add_argument(
        "--line-comments-only",
        action="store_true",
        help="Remove only // line comments; keep /* block comments */",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    ns = parse_args(sys.argv[1:] if argv is None else argv)

    combined_stdout: List[bytes] = []
    for path in ns.files:
        lang = ns.language or _detect_language_from_extension(path)
        try:
            out = scrub_file(
                path,
                language=lang,
                extra_clang_args=ns.clang_args,
                only_line_comments=ns.line_comments_only,
            )
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            return 2

        if ns.inplace:
            with open(path, "wb") as f:
                f.write(out)
        else:
            combined_stdout.append(out)

    if not ns.inplace:
        # Print content for all files in order, concatenated
        sys.stdout.buffer.write(b"".join(combined_stdout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
