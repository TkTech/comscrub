from pathlib import Path



def read_bytes(p: Path) -> bytes:
    return p.read_bytes()


def test_library_scrub_file(tmp_path: Path):
    from comscrub.core import scrub_file

    src = Path(__file__).parent.parent / "data" / "sample.c"
    # copy to tmp so we don't mutate repo data
    test_file = tmp_path / "sample.c"
    test_file.write_bytes(src.read_bytes())

    out = scrub_file(str(test_file))
    # Ensure line comments are gone and strings preserved
    assert b"//" not in out
    # The string literal containing comment-like text must remain
    assert b"/* not a comment */" in out
    # Specific block comments from the source should be removed
    assert b"/* include is fine */" not in out
    assert b"block" not in out  # from the multi-line block comment
    assert b"trailing */" not in out
    # Ensure tokens separated when comment was between identifiers
    assert b"x y" in out or b"x  y" in out or b"x\ty" in out or b"x\ny" in out


def test_cli_stdout(tmp_path: Path, monkeypatch):
    from comscrub.cli import main

    src = Path(__file__).parent.parent / "data" / "sample.c"
    test_file = tmp_path / "sample.c"
    test_file.write_bytes(src.read_bytes())

    # Capture stdout buffer
    out_chunks = []

    class StdoutBuf:
        def write(self, b):
            out_chunks.append(b)

        def flush(self):
            pass

    class Stdout:
        buffer = StdoutBuf()

    monkeypatch.setattr("sys.stdout", Stdout())
    rc = main([str(test_file)])
    assert rc == 0
    out = b"".join(out_chunks)
    assert b"//" not in out
    assert b"/* not a comment */" in out
    assert b"/* include is fine */" not in out


def test_cli_inplace(tmp_path: Path):
    from comscrub.cli import main

    src = Path(__file__).parent.parent / "data" / "sample.c"
    test_file = tmp_path / "sample.c"
    test_file.write_bytes(src.read_bytes())

    rc = main(["--inplace", str(test_file)])
    assert rc == 0
    new_bytes = test_file.read_bytes()
    assert b"//" not in new_bytes
    assert b"/* not a comment */" in new_bytes
    assert b"/* include is fine */" not in new_bytes


def test_library_scrub_file_cpp(tmp_path: Path):
    from comscrub.core import scrub_file

    src = Path(__file__).parent.parent / "data" / "sample.cpp"
    test_file = tmp_path / "sample.cpp"
    test_file.write_bytes(src.read_bytes())

    out = scrub_file(str(test_file))
    assert b"//" not in out
    assert b"/* not a comment */" in out
    assert b"/* header block */" not in out
    assert b"block comment in cpp" not in out
    assert b"x y" in out or b"x  y" in out or b"x\ty" in out or b"x\ny" in out


def test_cli_stdout_cpp(tmp_path: Path, monkeypatch):
    from comscrub.cli import main

    src = Path(__file__).parent.parent / "data" / "sample.cpp"
    test_file = tmp_path / "sample.cpp"
    test_file.write_bytes(src.read_bytes())

    out_chunks = []

    class StdoutBuf:
        def write(self, b):
            out_chunks.append(b)

        def flush(self):
            pass

    class Stdout:
        buffer = StdoutBuf()

    monkeypatch.setattr("sys.stdout", Stdout())
    rc = main([str(test_file)])
    assert rc == 0
    out = b"".join(out_chunks)
    assert b"//" not in out
    assert b"/* not a comment */" in out
    assert b"/* header block */" not in out


def test_cli_inplace_cpp(tmp_path: Path):
    from comscrub.cli import main

    src = Path(__file__).parent.parent / "data" / "sample.cpp"
    test_file = tmp_path / "sample.cpp"
    test_file.write_bytes(src.read_bytes())

    rc = main(["--inplace", str(test_file)])
    assert rc == 0
    new_bytes = test_file.read_bytes()
    assert b"//" not in new_bytes
    assert b"/* not a comment */" in new_bytes
    assert b"/* header block */" not in new_bytes


def test_library_scrub_file_objc(tmp_path: Path):
    from comscrub.core import scrub_file

    src = Path(__file__).parent.parent / "data" / "sample.m"
    test_file = tmp_path / "sample.m"
    test_file.write_bytes(src.read_bytes())

    out = scrub_file(str(test_file))
    assert b"//" not in out
    assert b"/* not a comment */" in out
    assert b"/* objc header */" not in out
    assert b"objc block comment" not in out
    assert b"a b" in out or b"a  b" in out or b"a\tb" in out or b"a\nb" in out


def test_cli_stdout_objc(tmp_path: Path, monkeypatch):
    from comscrub.cli import main

    src = Path(__file__).parent.parent / "data" / "sample.m"
    test_file = tmp_path / "sample.m"
    test_file.write_bytes(src.read_bytes())

    out_chunks = []

    class StdoutBuf:
        def write(self, b):
            out_chunks.append(b)

        def flush(self):
            pass

    class Stdout:
        buffer = StdoutBuf()

    monkeypatch.setattr("sys.stdout", Stdout())
    rc = main([str(test_file)])
    assert rc == 0
    out = b"".join(out_chunks)
    assert b"//" not in out
    assert b"/* not a comment */" in out
    assert b"/* objc header */" not in out


def test_cli_inplace_objc(tmp_path: Path):
    from comscrub.cli import main

    src = Path(__file__).parent.parent / "data" / "sample.m"
    test_file = tmp_path / "sample.m"
    test_file.write_bytes(src.read_bytes())

    rc = main(["--inplace", str(test_file)])
    assert rc == 0
    new_bytes = test_file.read_bytes()
    assert b"//" not in new_bytes
    assert b"/* not a comment */" in new_bytes
    assert b"/* objc header */" not in new_bytes


def test_library_scrub_file_objcpp(tmp_path: Path):
    from comscrub.core import scrub_file

    src = Path(__file__).parent.parent / "data" / "sample.mm"
    test_file = tmp_path / "sample.mm"
    test_file.write_bytes(src.read_bytes())

    out = scrub_file(str(test_file))
    assert b"//" not in out
    assert b"/* not a comment */" in out
    assert b"/* objc++ header */" not in out
    assert b"objc++ block comment" not in out
    assert b"m n" in out or b"m  n" in out or b"m\tn" in out or b"m\nn" in out


def test_cli_stdout_objcpp(tmp_path: Path, monkeypatch):
    from comscrub.cli import main

    src = Path(__file__).parent.parent / "data" / "sample.mm"
    test_file = tmp_path / "sample.mm"
    test_file.write_bytes(src.read_bytes())

    out_chunks = []

    class StdoutBuf:
        def write(self, b):
            out_chunks.append(b)

        def flush(self):
            pass

    class Stdout:
        buffer = StdoutBuf()

    monkeypatch.setattr("sys.stdout", Stdout())
    rc = main([str(test_file)])
    assert rc == 0
    out = b"".join(out_chunks)
    assert b"//" not in out
    assert b"/* not a comment */" in out
    assert b"/* objc++ header */" not in out


def test_cli_inplace_objcpp(tmp_path: Path):
    from comscrub.cli import main

    src = Path(__file__).parent.parent / "data" / "sample.mm"
    test_file = tmp_path / "sample.mm"
    test_file.write_bytes(src.read_bytes())

    rc = main(["--inplace", str(test_file)])
    assert rc == 0
    new_bytes = test_file.read_bytes()
    assert b"//" not in new_bytes
    assert b"/* not a comment */" in new_bytes
    assert b"/* objc++ header */" not in new_bytes


def test_line_comments_only_keeps_block_comments(tmp_path: Path):
    from comscrub.core import scrub_file

    src = Path(__file__).parent.parent / "data" / "sample.c"
    test_file = tmp_path / "sample.c"
    test_file.write_bytes(src.read_bytes())

    out = scrub_file(str(test_file), only_line_comments=True)
    # Line comments removed
    assert b"//" not in out
    # Block comments remain
    assert b"/* include is fine */" in out
    assert b"block" in out
    assert b"trailing */" in out
    # String literal preserved
    assert b"/* not a comment */" in out
    # Adjacency preserved since block comment remains
    assert b"x/**/y" in out


def test_line_comments_only_keeps_block_comments_cpp(tmp_path: Path):
    from comscrub.core import scrub_file

    src = Path(__file__).parent.parent / "data" / "sample.cpp"
    test_file = tmp_path / "sample.cpp"
    test_file.write_bytes(src.read_bytes())

    out = scrub_file(str(test_file), only_line_comments=True)
    # Line comments removed
    assert b"//" not in out
    # Block comments remain
    assert b"/* header block */" in out
    assert b"block comment in cpp" in out
    assert b"trailing */" in out
    # String literal preserved
    assert b"/* not a comment */" in out
    # Adjacency preserved since block comment remains
    assert b"x/**/y" in out
