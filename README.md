comscrub
=========

Strip comments from C-family source files using libclang’s tokenizer. Unlike
regex-based approaches, this relies on clang’s understanding of the language,
so strings and tricky edge cases are handled correctly.

Usage
-----

- CLI: `comscrub file.c` (or `python -m comscrub file.c`).
- Prints to stdout by default; use `--inplace` to rewrite files.
- Remove only line comments with `--line-comments-only` (keeps `/* ... */`).

Examples:

- `comscrub data/sample.c`
- `comscrub --inplace data/sample.c`
- Remove only line comments: `comscrub --line-comments-only data/sample.cpp`
- Force language (otherwise inferred from extension): `comscrub -x c++ foo.hpp`
- Pass extra clang args (repeatable): `comscrub --clang-arg -std=c11 file.c`


One-liners:

- In‑place across repo (batch files safely):
   - find . -type f \( -name '*.cpp' -o -name '*.hpp' \) -exec uv run comscrub --inplace {} +
- Dry‑run to stdout (one file at a time to keep outputs separate):
   - find . -type f \( -name '*.cpp' -o -name '*.hpp' \) -exec uv run comscrub {} \;
- Only remove line comments:
   - find . -type f \( -name '*.cpp' -o -name '*.hpp' \) -exec uv run comscrub --line-comments-only --inplace {} +
- Handle paths with spaces using null‑sep + xargs:
   - find . -type f \( -name '*.cpp' -o -name '*.hpp' \) -print0 | xargs -0 uv run comscrub --inplace
- Exclude common build/VC dirs:
   - find . -type d \( -name .git -o -name build -o -name dist \) -prune -o -type f \( -name '*.cpp' -o -name '*.hpp' \) -exec uv run comscrub --inplace {} +

