#!/usr/bin/env python3
"""Read an IPA's app metadata without extracting or executing its contents."""
import argparse
import os
import plistlib
import re
import sys
import zipfile


def inspect(path):
    with zipfile.ZipFile(path) as archive:
        candidates = [name for name in archive.namelist()
                      if re.fullmatch(r"Payload/[^/]+\.app/Info\.plist", name)]
        if len(candidates) != 1:
            raise ValueError("IPA must contain exactly one top-level app Info.plist")
        info = plistlib.loads(archive.read(candidates[0]))
        if info.get("CFBundleIdentifier") != "com.google.ios.youtube":
            raise ValueError("Expected an original YouTube IPA (com.google.ios.youtube)")
        version = info.get("CFBundleShortVersionString") or info.get("CFBundleVersion")
        if not isinstance(version, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", version):
            raise ValueError("YouTube version is missing or invalid")
        executable = info.get("CFBundleExecutable")
        if not executable or candidates[0].rsplit("/", 1)[0] + "/" + executable not in archive.namelist():
            raise ValueError("App executable is missing")
        return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ipa")
    args = parser.parse_args()
    try:
        version = inspect(args.ipa)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, plistlib.InvalidFileException) as error:
        print(f"Invalid IPA: {error}", file=sys.stderr)
        return 1
    print(f"YouTube version: {version}")
    if os.environ.get("GITHUB_ENV"):
        with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as output:
            output.write(f"YT_VERSION={version}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
