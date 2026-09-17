"""dHash 感知哈希：计算、跨数据集匹配、内部重复检测、聚组。

用法示例：
    from idt.dhash import compute_batch, cross_pairs, internal_pairs, cluster_pairs
"""
import os
import numpy as np
import imagehash
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


def compute_one(path, hash_size=16):
    """计算单张图的 dHash。"""
    return imagehash.dhash(Image.open(path).convert("L"), hash_size=hash_size)


def compute_batch(paths, hash_size=16, workers=16):
    """批量计算 dHash。

    返回 (bits, names)：
      bits:  shape (N, hash_size*hash_size) 的 uint8 0/1 矩阵
      names: 每张图的文件名（basename）
    """
    with ThreadPoolExecutor(max_workers=workers) as ex:
        hashes = list(ex.map(lambda p: compute_one(p, hash_size), paths))
    bits = np.stack([h.hash.flatten().astype(np.uint8) for h in hashes])
    names = [os.path.basename(p) for p in paths]
    return bits, names


def _pack(bits):
    """把 0/1 位矩阵打包成 uint8（每 8 位一字节），用于 bitwise_count 加速。"""
    return np.packbits(bits, axis=1)


def cross_pairs(bits_a, names_a, bits_b, names_b, threshold=8):
    """跨数据集找汉明距离 <= threshold 的对。

    返回 [(distance, name_a, name_b), ...]，按距离升序。
    """
    a = _pack(bits_a)
    b = _pack(bits_b)
    pairs = []
    for i in range(len(a)):
        dists = np.bitwise_count(b ^ a[i][None, :]).sum(axis=1)
        for j in np.where(dists <= threshold)[0]:
            pairs.append((int(dists[j]), names_a[i], names_b[j]))
    pairs.sort(key=lambda x: x[0])
    return pairs


def internal_pairs(bits, names, threshold=8, chunk=300):
    """数据集内部找汉明距离 <= threshold 的对（只算上三角，避免重复）。

    返回 [(idx_a, idx_b, distance), ...]。
    """
    packed = _pack(bits)
    n = len(names)
    pairs = []
    for i in range(0, n, chunk):
        block = packed[i:i + chunk]
        rest = packed[i:]
        xor = block[:, None, :] ^ rest[None, :, :]
        dists = np.bitwise_count(xor).sum(axis=2)
        mask = np.triu(np.ones_like(dists, dtype=bool), k=1)
        cand = (dists <= threshold) & mask
        ii, jj = np.where(cand)
        for a, b in zip(ii, jj):
            pairs.append((i + a, i + b, int(dists[a, b])))
    return pairs


class DSU:
    """并查集。"""
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def cluster_pairs(pairs, n):
    """把 (idx_a, idx_b, ...) 的对聚成连通组。

    返回 [[idx, ...], ...]，只保留大小 >= 2 的组。
    """
    dsu = DSU(n)
    for a, b, *_ in pairs:
        dsu.union(a, b)
    groups = {}
    for i in range(n):
        groups.setdefault(dsu.find(i), []).append(i)
    return [g for g in groups.values() if len(g) >= 2]
