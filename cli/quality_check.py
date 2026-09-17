"""质量检查：检测目录内损坏图片和近纯色（占位符）图片。"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from idt.quality import scan_dir


def main():
    ap = argparse.ArgumentParser(description="检测损坏图片和近纯色占位符")
    ap.add_argument("dir", help="图片目录")
    ap.add_argument("--workers", type=int, default=16, help="并发线程数（默认 16）")
    ap.add_argument("--solid-std", type=float, default=5.0, help="近纯色阈值（std，默认 5）")
    ap.add_argument("--out", default=None, help="输出清单到文件")
    args = ap.parse_args()

    corrupt, near_solid = scan_dir(args.dir, workers=args.workers, solid_std_threshold=args.solid_std)
    print(f"损坏: {len(corrupt)} 张")
    for p, d in corrupt:
        print(f"  [损坏] {os.path.basename(p)}: {d}")
    print(f"\n近纯色(std<{args.solid_std}): {len(near_solid)} 张")
    for p, d in near_solid:
        print(f"  [纯色] {os.path.basename(p)}: {d}")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            for p, d in corrupt:
                f.write(f"corrupt\t{os.path.basename(p)}\t{d}\n")
            for p, d in near_solid:
                f.write(f"solid\t{os.path.basename(p)}\t{d}\n")
        print(f"\n清单已写 {args.out}")


if __name__ == "__main__":
    main()
