import os
from typing import List, Optional, Sequence, Tuple


def _detect_language_from_extension(path: str) -> Optional[str]:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".c"}:
        return "c"
    if ext in {".cc", ".cpp", ".cxx", ".c++", ".hpp", ".hh", ".hxx"}:
        return "c++"
    if ext in {".m"}:
        return "objective-c"
    if ext in {".mm"}:
        return "objective-c++"
    if ext in {".cu"}:
        return "cuda"
    if ext in {".h"}:
        return "c++"
    return None


def _clang_args_for_language(language: Optional[str]) -> List[str]:
    if not language:
        return []
    return ["-x", language]


def _needs_space_between(prev_b: Optional[int], next_b: Optional[int]) -> bool:
    if prev_b is None or next_b is None:
        return False
    # whitespace -> no extra space needed
    if chr(prev_b).isspace() or chr(next_b).isspace():
        return False
    # separators/punctuators where adjacency is unambiguous
    seps = b"()[]{};,:+-*/%&|^~!=<>?."
    if prev_b in seps or next_b in seps:
        return False
    return True


def _collect_comment_spans(
    path: str,
    clang_args: Sequence[str],
    *,
    only_line_comments: bool = False,
) -> List[Tuple[int, int]]:
    try:
        from clang import cindex
    except Exception as e:  # pragma: no cover - import guard
        raise RuntimeError(
            "libclang (clang.cindex) is required. Install `clang` Python bindings and ensure libclang is available."
        ) from e

    index = cindex.Index.create()
    # Parse the file directly so offsets are computed from on-disk bytes.
    tu = index.parse(
        path,
        args=list(clang_args),
        options=cindex.TranslationUnit.PARSE_NONE,
    )

    comment_spans: List[Tuple[int, int]] = []
    for token in tu.get_tokens(extent=tu.cursor.extent):
        if token.kind == cindex.TokenKind.COMMENT:
            # Offsets are half-open [start, end)
            start = token.extent.start
            end = token.extent.end
            if (
                start.file
                and start.file.name
                and os.path.abspath(start.file.name) != os.path.abspath(path)
            ):
                # Skip comments from other files (e.g., headers)
                continue
            if only_line_comments:
                # Keep block comments; remove only // and similar
                try:
                    spelling = token.spelling  # type: ignore[attr-defined]
                except Exception:
                    spelling = None
                if spelling is None:
                    # Fallback: slice file bytes when spelling unavailable
                    with open(path, "rb") as _f:
                        _bytes = _f.read()
                    spelling = _bytes[start.offset : end.offset].decode(
                        "utf-8", errors="ignore"
                    )
                if not str(spelling).startswith("//"):
                    continue
            comment_spans.append((start.offset, end.offset))

    # Normalize order and merge overlapping/adjacent spans
    comment_spans.sort()
    merged: List[Tuple[int, int]] = []
    for s, e in comment_spans:
        if not merged:
            merged.append((s, e))
            continue
        ps, pe = merged[-1]
        if s <= pe:  # overlap or adjacency
            merged[-1] = (ps, max(pe, e))
        else:
            merged.append((s, e))
    return merged


def scrub_file(
    path: str,
    *,
    language: Optional[str] = None,
    extra_clang_args: Optional[Sequence[str]] = None,
    only_line_comments: bool = False,
) -> bytes:
    """
    Strip comments from the file at `path` using libclang tokenization.

    Returns the new content as bytes.
    """
    if extra_clang_args is None:
        extra_clang_args = []

    lang = language or _detect_language_from_extension(path)
    clang_args = [*_clang_args_for_language(lang), *list(extra_clang_args)]

    with open(path, "rb") as f:
        original = f.read()

    spans = _collect_comment_spans(
        path, clang_args, only_line_comments=only_line_comments
    )
    if not spans:
        return original

    out = bytearray()
    pos = 0
    for s, e in spans:
        if s > pos:
            out.extend(original[pos:s])
        prev_b = original[s - 1] if s - 1 >= 0 else None
        next_b = original[e] if e < len(original) else None
        if _needs_space_between(prev_b, next_b):
            out.extend(b" ")
        pos = e
    if pos < len(original):
        out.extend(original[pos:])

    return bytes(out)
