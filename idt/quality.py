"""质量检查：损坏文件检测 + 近纯色（占位符）检测。"""
import os
import numpy as np
from PIL import Image


def check_file(path, solid_std_threshold=5.0):
    """检查单张图。返回 (status, detail)：
      status: "ok" / "corrupt" / "near_solid"
      detail: 说明文字（ok 时为空）
    """
    try:
        if os.path.getsize(path) == 0:
            return ("corrupt", "空文件")
        im = Image.open(path).convert("RGB")
        im.load()  # 完整解码，能发现截断/损坏的 JPEG
        im.thumbnail((64, 64), Image.LANCZOS)
        arr = np.asarray(im)
        std = float(arr.std())
        if std < solid_std_threshold:
            return ("near_solid", f"std={std:.2f} mean={arr.mean():.1f}")
        return ("ok", "")
    except Exception as e:
        return ("corrupt", f"{type(e).__name__}: {str(e)[:60]}")


def scan_dir(directory, workers=16, solid_std_threshold=5.0, paths=None):
    """扫描目录下所有图片。返回 (corrupt, near_solid)，每项为 [(path, detail), ...]。"""
    from .image import iter_images
    from .parallel import parallel_map
    if paths is None:
        paths = iter_images(directory)
    results = parallel_map(
        lambda p: check_file(p, solid_std_threshold), paths, workers=workers
    )
    corrupt = [(p, d) for p, (s, d) in zip(paths, results) if s == "corrupt"]
    near_solid = [(p, d) for p, (s, d) in zip(paths, results) if s == "near_solid"]
    return corrupt, near_solid
