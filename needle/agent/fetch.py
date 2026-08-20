import os
import platform
import sys
import zipfile

HF_REPO = "Cactus-Compute/needle2"

ENGINE_VERSION = "2.0.3"

PLATFORMS = ("macos-arm64", "linux-x86_64", "linux-arm64", "linux-armv7",
             "linux-riscv64", "linux-mipsel", "windows-x86_64", "windows-arm64",
             "android-arm64", "android-armv7", "android-riscv64",
             "ios-arm64", "ios-sim-arm64", "tvos-arm64", "watchos-arm64", "wasm")


def _lib_name_for(tag):
    if tag.startswith("macosx"):
        return "libneedle.dylib"
    if tag.startswith("win"):
        return "libneedle.dll"
    return "libneedle.so"


def _lib_name():
    if sys.platform == "darwin":
        return "libneedle.dylib"
    if sys.platform == "win32":
        return "libneedle.dll"
    return "libneedle.so"


def _is_musl():
    if sys.platform != "linux":
        return False
    libc, _ = platform.libc_ver()
    if libc:
        return False
    try:
        with open("/proc/self/maps", "rb") as maps:
            return b"musl" in maps.read()
    except OSError:
        return True


def _platform_tag():
    machine = platform.machine().lower()
    if sys.platform == "darwin":
        arch = "arm64" if machine in ("arm64", "aarch64") else "x86_64"
        return "macosx_11_0_" + arch
    if sys.platform == "win32":
        return "win_arm64" if machine in ("arm64", "aarch64") else "win_amd64"
    arch = "aarch64" if machine in ("aarch64", "arm64") else "x86_64"
    family = "musllinux_1_2_" if _is_musl() else "manylinux2014_"
    return family + arch


def _register_download():
    from huggingface_hub import hf_hub_download

    try:
        hf_hub_download(repo_id=HF_REPO, filename="config.json", repo_type="model",
                        force_download=True)
    except Exception:
        pass


def download_platform(name, out_dir):
    import shutil
    import stat
    from huggingface_hub import hf_hub_download, list_repo_files

    _register_download()
    files = [f for f in list_repo_files(HF_REPO) if f.startswith(name + "/")]
    dest = os.path.join(out_dir, name)
    os.makedirs(dest, exist_ok=True)
    out = []
    for f in files:
        cached = hf_hub_download(repo_id=HF_REPO, filename=f, repo_type="model")
        target = os.path.join(dest, os.path.basename(f))
        shutil.copyfile(cached, target)
        if os.path.basename(target) in ("needle", "needle.exe"):
            os.chmod(target, os.stat(target).st_mode | stat.S_IXUSR
                     | stat.S_IXGRP | stat.S_IXOTH)
        out.append(target)
    return out


def fetch_library(version, dest_dir, tag=None):
    from huggingface_hub import hf_hub_download

    tag = tag or _platform_tag()
    wheel = "cactus_needle-{}-py3-none-{}.whl".format(version, tag)
    _register_download()
    path = hf_hub_download(repo_id=HF_REPO, filename="python/" + wheel, repo_type="model")
    lib = _lib_name_for(tag)
    with zipfile.ZipFile(path) as archive:
        data = archive.read("needle/" + lib)
    out = os.path.join(dest_dir, lib)
    with open(out, "wb") as handle:
        handle.write(data)
    return out
