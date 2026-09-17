"""抽样：从目录随机抽 N 张复制到新目录。"""
import os
import sys
import random
import shutil
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from idt.image import iter_images
from idt.parallel import parallel_map


def main():
    ap = argparse.ArgumentParser(description="从目录随机抽 N 张复制到新目录")
    ap.add_argument("src", help="源目录")
    ap.add_argument("dst", help="输出目录")
    ap.add_argument("--count", type=int, default=10000, help="抽样数量（默认 10000）")
    ap.add_argument("--seed", type=int, default=42, help="随机种子（默认 42，可复现）")
    ap.add_argument("--workers", type=int, default=16, help="并发线程数（默认 16）")
    args = ap.parse_args()

    os.makedirs(args.dst, exist_ok=True)
    files = iter_images(args.src)
    random.seed(args.seed)
    sample = random.sample(files, min(args.count, len(files)))
    print(f"从 {len(files)} 张中抽 {len(sample)} 张", flush=True)

    def copy(f):
        shutil.copy2(f, os.path.join(args.dst, os.path.basename(f)))

    parallel_map(copy, sample, workers=args.workers)
    print(f"完成，输出 {len(sample)} 张 -> {args.dst}")


if __name__ == "__main__":
    main()
