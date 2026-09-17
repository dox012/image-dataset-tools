"""内部去重：找目录内 dHash 重复，可选删除（每组保留一张）。"""
import os
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from idt.image import iter_images
from idt.dhash import compute_batch, internal_pairs, cluster_pairs


def main():
    ap = argparse.ArgumentParser(description="目录内 dHash 去重")
    ap.add_argument("dir", help="图片目录")
    ap.add_argument("--threshold", type=int, default=8, help="汉明距离阈值（默认 8）")
    ap.add_argument("--hash-size", type=int, default=16, help="dHash 位数参数（默认 16）")
    ap.add_argument("--workers", type=int, default=16, help="并发线程数（默认 16）")
    ap.add_argument("--delete", action="store_true", help="实际删除重复（每组保留 id 最小的一张）")
    args = ap.parse_args()

    files = iter_images(args.dir)
    print(f"计算 {len(files)} 张的 dHash...", flush=True)
    bits, names = compute_batch(files, hash_size=args.hash_size, workers=args.workers)

    t0 = time.time()
    pairs = internal_pairs(bits, names, threshold=args.threshold)
    groups = cluster_pairs(pairs, len(files))
    n_involved = sum(len(g) for g in groups)
    print(f"重复 {len(pairs)} 对, {len(groups)} 组, 涉及 {n_involved} 张", flush=True)
    print(f"检测耗时 {time.time()-t0:.0f}s", flush=True)

    if not args.delete:
        print("未加 --delete，仅报告。加 --delete 才会删除重复。")
        # 打印每组
        for i, g in enumerate(sorted(groups, key=lambda x: -len(x)), 1):
            print(f"  组 {i} ({len(g)} 张): {', '.join(names[j] for j in g)}")
        return

    # 每组保留文件名最小的，删除其余
    to_delete = []
    for g in groups:
        g_sorted = sorted(g, key=lambda j: names[j])
        to_delete.extend(files[j] for j in g_sorted[1:])

    for f in to_delete:
        if os.path.exists(f):
            os.remove(f)
    print(f"删除 {len(to_delete)} 张, 剩余 {len(files) - len(to_delete)} 张")


if __name__ == "__main__":
    main()
