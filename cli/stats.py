"""统计：图片分辨率、宽高比、文件大小分布。"""
import os
import sys
import argparse
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from idt.image import iter_images
from idt.parallel import parallel_map
from PIL import Image


def img_size(path):
    try:
        with Image.open(path) as im:
            return im.size, os.path.getsize(path)
    except Exception:
        return None, 0


def main():
    ap = argparse.ArgumentParser(description="统计图片分辨率/宽高比/大小分布")
    ap.add_argument("dir", help="图片目录")
    ap.add_argument("--workers", type=int, default=16, help="并发线程数（默认 16）")
    args = ap.parse_args()

    files = iter_images(args.dir)
    results = parallel_map(img_size, files, workers=args.workers)

    sizes = [r[0] for r in results if r[0] is not None]
    bytes_list = [r[1] for r in results if r[0] is not None]
    n = len(sizes)

    if n == 0:
        print("没有可读的图片")
        return

    ws = [s[0] for s in sizes]
    hs = [s[1] for s in sizes]
    areas = [w * h for w, h in sizes]
    ratios = [round(w / h, 2) for w, h in sizes]

    def q(arr):
        import numpy as np
        ps = np.percentile(arr, [0, 25, 50, 75, 100])
        return f"min={ps[0]:.0f} 中位数={ps[2]:.0f} max={ps[4]:.0f}"

    print(f"图片数: {n}")
    print(f"宽 width : {q(ws)}")
    print(f"高 height: {q(hs)}")
    print(f"像素面积: {q(areas)}")
    print(f"文件大小: {q(bytes_list)}")

    # 面积分桶
    mp = [a / 1e6 for a in areas]
    bins = [0, 0.5, 1, 2, 4, 8, 12, 16, 24, 48, float("inf")]
    labels = ["<0.5MP", "0.5-1", "1-2", "2-4", "4-8", "8-12", "12-16", "16-24", "24-48", ">48"]
    print("\n面积分布(MP):")
    for i in range(len(bins) - 1):
        c = sum(1 for a in mp if bins[i] <= a < bins[i + 1])
        print(f"  {labels[i]:>8}: {c:6d} ({c/n*100:.1f}%)")

    # 方向
    land = sum(1 for r in ratios if r > 1.2)
    port = sum(1 for r in ratios if r < 1 / 1.2)
    sq = n - land - port
    print(f"\n方向: 横向 {land} ({land/n*100:.0f}%) 方形 {sq} ({sq/n*100:.0f}%) 纵向 {port} ({port/n*100:.0f}%)")

    # 常见宽高比
    print("\n常见宽高比:")
    for ratio, c in Counter(ratios).most_common(10):
        print(f"  {ratio:.2f}: {c} ({c/n*100:.1f}%)")


if __name__ == "__main__":
    main()
