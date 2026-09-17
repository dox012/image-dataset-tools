"""缩略图：把目录下图片缩放到最长边，保持宽高比。"""
import os
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from idt.image import iter_images, resize_file
from idt.parallel import parallel_map


def main():
    ap = argparse.ArgumentParser(description="缩略图：缩放到最长边，保持宽高比")
    ap.add_argument("src", help="源图片目录")
    ap.add_argument("dst", help="输出目录")
    ap.add_argument("--max-edge", type=int, default=1024, help="最长边（默认 1024）")
    ap.add_argument("--quality", type=int, default=90, help="JPG 质量（默认 90）")
    ap.add_argument("--workers", type=int, default=16, help="并发线程数（默认 16）")
    ap.add_argument("--overwrite", action="store_true", help="覆盖输出目录（默认跳过已存在）")
    args = ap.parse_args()

    os.makedirs(args.dst, exist_ok=True)
    files = iter_images(args.src)
    print(f"待处理 {len(files)} 张", flush=True)

    def process(f):
        name = os.path.basename(f)
        out = os.path.join(args.dst, name)
        if not args.overwrite and os.path.exists(out):
            return "skip"
        return "ok" if resize_file(f, out, args.max_edge, args.quality) else "err"

    t0 = time.time()
    results = parallel_map(process, files, workers=args.workers)
    ok = results.count("ok")
    skip = results.count("skip")
    err = results.count("err")
    dt = time.time() - t0
    print(f"完成: 成功 {ok}, 跳过 {skip}, 失败 {err}")
    print(f"耗时 {dt:.0f}s, 速度 {len(files)/dt:.0f} 张/s")
    print(f"输出: {args.dst}")


if __name__ == "__main__":
    main()
