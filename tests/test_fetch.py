def test_lib_path_env_override(tmp_path, monkeypatch):
    import needle

    fake = tmp_path / "libneedle.dylib"
    fake.write_bytes(b"x")
    monkeypatch.setenv("NEEDLE_LIB_PATH", str(fake))
    assert needle._library_path() == str(fake)


def test_weights_spec_parsing():
    from needle.cli import _weights_spec

    assert _weights_spec("acme/tuned/model.cact") == ("acme/tuned", "model.cact")
    assert _weights_spec("acme/tuned") == ("acme/tuned", None)
    assert _weights_spec("acme/tuned/sub/dir/m.cact") == ("acme/tuned", "sub/dir/m.cact")


def test_lib_name_for_tags():
    from needle.agent.fetch import _lib_name_for

    assert _lib_name_for("macosx_11_0_arm64") == "libneedle.dylib"
    assert _lib_name_for("win_amd64") == "libneedle.dll"
    assert _lib_name_for("manylinux2014_aarch64") == "libneedle.so"
    assert _lib_name_for("musllinux_1_2_x86_64") == "libneedle.so"
