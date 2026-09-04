import os
import sys


def main():
    workdir = sys.argv[1]
    in_path = os.path.join(workdir, "numbers.txt")
    with open(in_path) as f:
        values = [int(line.strip()) for line in f if line.strip()]

    count = 0
    total = 0
    for n in values:
        div3 = (n % 3 == 0)
        div5 = (n % 5 == 0)
        if div3 != div5:
            count += 1
            total += n

    out_path = os.path.join(workdir, "modular_result.txt")
    with open(out_path, "w") as f:
        f.write(f"count={count}\n")
        f.write(f"sum={total}")


if __name__ == "__main__":
    main()
