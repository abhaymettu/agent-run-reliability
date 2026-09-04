import os
import sys

BOUNDARY = "---SPLIT---"


def main():
    workdir = sys.argv[1]
    src = os.path.join(workdir, "archive.txt")
    with open(src, "r") as f:
        text = f.read()
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    chunks = [[]]
    for ln in lines:
        if ln == BOUNDARY:
            chunks.append([])
        else:
            chunks[-1].append(ln)

    chunks_dir = os.path.join(workdir, "chunks")
    os.makedirs(chunks_dir, exist_ok=True)

    index_lines = []
    for i, chunk_lines in enumerate(chunks, start=1):
        fname = f"chunk_{i:03d}.txt"
        path = os.path.join(chunks_dir, fname)
        if chunk_lines:
            content = "\n".join(chunk_lines) + "\n"
        else:
            content = ""
        with open(path, "w") as f:
            f.write(content)
        first_line = chunk_lines[0] if chunk_lines else "EMPTY"
        index_lines.append(f"{fname} {len(chunk_lines)} {first_line}")

    with open(os.path.join(chunks_dir, "index.txt"), "w") as f:
        f.write("\n".join(index_lines) + "\n")


if __name__ == "__main__":
    main()
