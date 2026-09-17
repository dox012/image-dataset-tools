"""图片处理：缩放（保持宽高比到最长边）、图片文件遍历。"""
import os
import glob
import cv2


IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")


def iter_images(directory, recursive=False):
    """列出目录下所有图片文件路径。"""
    pattern = os.path.join(directory, "**" if recursive else "", "*")
    files = glob.glob(pattern, recursive=recursive)
    return sorted(f for f in files if f.lower().endswith(IMAGE_EXTS))


def resize_to_max_edge(img, max_edge, interpolation=cv2.INTER_AREA):
    """把图片缩放到最长边 <= max_edge，保持宽高比（小于 max_edge 的原样返回）。"""
    h, w = img.shape[:2]
    if max(w, h) > max_edge:
        s = max_edge / max(w, h)
        img = cv2.resize(
            img,
            (max(1, round(w * s)), max(1, round(h * s))),
            interpolation=interpolation,
        )
    return img


def resize_file(src, dst, max_edge=1024, quality=90, interpolation=cv2.INTER_AREA):
    """缩放单个图片文件。返回 True 成功 / False 失败（无法解码等）。"""
    img = cv2.imread(src, cv2.IMREAD_COLOR)
    if img is None:
        return False
    img = resize_to_max_edge(img, max_edge, interpolation)
    cv2.imwrite(dst, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return True
