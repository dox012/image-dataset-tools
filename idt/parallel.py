"""多线程并行工具。"""
from concurrent.futures import ThreadPoolExecutor


def parallel_map(fn, items, workers=16):
    """多线程 map，保持输入顺序。适合 I/O 密集或释放 GIL 的任务。"""
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))
