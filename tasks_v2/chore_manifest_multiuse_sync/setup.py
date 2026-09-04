import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import generate  # noqa: E402


def main():
    workdir = sys.argv[1]
    sources, manifest_entries, prebuilt = generate()

    sources_dir = os.path.join(workdir, "sources")
    os.makedirs(sources_dir, exist_ok=True)
    for name, content in sources:
        with open(os.path.join(sources_dir, name), "w") as f:
            f.write(content)

    manifest = [{"target": t, "source": s} for t, s in manifest_entries]
    with open(os.path.join(workdir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    for relpath, content in prebuilt:
        full = os.path.join(workdir, "build", *relpath.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content)


if __name__ == "__main__":
    main()
