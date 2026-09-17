"""跨数据集查重：找两个目录之间 dHash 重复的图，可选删除 A 目录侧的重复。"""
import os
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from idt.image import iter_images
from idt.dhash import compute_batch, cross_pairs


def main():
    ap = argparse.ArgumentParser(description="两个目录之间 dHash 查重")
    ap.add_argument("dir_a", help="目录 A")
    ap.add_argument("dir_b", help="目录 B")
    ap.add_argument("--threshold", type=int, default=8, help="汉明距离阈值（默认 8）")
    ap.add_argument("--hash-size", type=int, default=16, help="dHash 位数参数（默认 16）")
    ap.add_argument("--workers", type=int, default=16, help="并发线程数（默认 16）")
    ap.add_argument("--delete-a", action="store_true", help="删除 A 目录侧的重复图")
    ap.add_argument("--out", default=None, help="输出清单到文件")
    args = ap.parse_args()

    files_a = iter_images(args.dir_a)
    files_b = iter_images(args.dir_b)
    print(f"A: {len(files_a)} 张, B: {len(files_b)} 张", flush=True)

    print("计算 dHash...", flush=True)
    bits_a, names_a = compute_batch(files_a, hash_size=args.hash_size, workers=args.workers)
    bits_b, names_b = compute_batch(files_b, hash_size=args.hash_size, workers=args.workers)

    t0 = time.time()
    pairs = cross_pairs(bits_a, names_a, bits_b, names_b, threshold=args.threshold)
    print(f"跨数据集重复: {len(pairs)} 对", flush=True)
    print(f"匹配耗时 {time.time()-t0:.0f}s", flush=True)

    # 各距离分布
    from collections import Counter
    print("距离分布:", dict(sorted(Counter(d for d, _, _ in pairs).items())))

    # 输出清单
    lines = [f"{d}\t{a}\t{b}" for d, a, b in pairs]
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write("distance\tA\tB\n" + "\n".join(lines) + "\n")
        print(f"清单已写 {args.out}")

    # 展示前 30 对
    print("\n前 30 对:")
    for d, a, b in pairs[:30]:
        print(f"  d={d}  A:{a}  <->  B:{b}")

    # 可选删除 A 侧
    if args.delete_a:
        a_uniq = sorted(set(a for _, a, _ in pairs))
        removed = 0
        for name in a_uniq:
            p = os.path.join(args.dir_a, name)
            if os.path.exists(p):
                os.remove(p)
                removed += 1
        print(f"\n删除 A 侧 {removed} 张重复图")


if __name__ == "__main__":
    main()
