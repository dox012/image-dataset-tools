# image-dataset-tools

图像数据集预处理工具集：缩略图、抽样、dHash 去重、质量检查、分辨率统计。

## 安装

```bash
pip install -r requirements.txt
```

## 用法

所有命令通过 `python cli/xxx.py` 调用，参数用 `--help` 查看。

### 1. 缩略图

把目录图片缩放到最长边（保持宽高比），输出到新目录：

```bash
python cli/resize.py E:\openimages E:\openimages_1k --max-edge 1024 --quality 90 --workers 16
```

- `--max-edge 1024`：最长边（小于该值的图原样保留）
- `--quality 90`：JPG 质量
- `--workers 16`：并发线程数（I/O + cv2 场景 16 是实测甜点）

### 2. 抽样

随机抽 N 张复制到新目录：

```bash
python cli/sample.py E:\openimages_1k E:\openimages_1w --count 10000 --seed 42
```

### 3. 目录内去重

找目录内 dHash 重复（汉明距离 ≤ 阈值），可选删除：

```bash
# 只报告，不删除
python cli/dedup.py E:\pexels_1k --threshold 8

# 删除重复（每组保留文件名最小的一张）
python cli/dedup.py E:\pexels_1k --threshold 8 --delete
```

### 4. 跨数据集查重

找两个目录之间重复的图：

```bash
# 只报告
python cli/cross_dedup.py E:\openimages_1k E:\pexels_1k --threshold 8

# 输出清单 + 删除 A 目录侧重复
python cli/cross_dedup.py E:\openimages_1k E:\pexels_1k --threshold 8 --delete-a --out dup.txt
```

### 5. 质量检查

检测损坏图片和近纯色占位符：

```bash
python cli/quality_check.py E:\openimages --workers 16 --solid-std 5
```

### 6. 统计

分辨率 / 宽高比 / 面积 / 文件大小分布：

```bash
python cli/stats.py E:\pexels_1k --workers 16
```

## 核心库

也可以作为库 import 复用：

```python
from idt.dhash import compute_batch, cross_pairs, internal_pairs, cluster_pairs
from idt.image import iter_images, resize_file
from idt.quality import scan_dir
```

## 设计要点（踩坑记录）

- **dHash 用 `hash_size=16`**（256 位），不要用默认 8（64 位）——低纹理图（天空/纯色）在 64 位下会哈希碰撞。
- **汉明距离阈值默认 8**：实测距离 ≤ 8 是「同一张图的不同压缩/缩放版本」的边界，距离 9+ 开始混入「相似但不同」的图。
- **缩放用 cv2 + INTER_AREA**，比 PIL + LANCZOS 快 ~1.7 倍。
- **并发用线程而非进程**（cv2/PIL 解码释放 GIL），16 线程是甜点，32 线程反而因磁盘寻道竞争变慢。
- **不要用 MD5 查重**：不同压缩/缩放的同一张图字节不同，MD5 匹配不到，要用感知哈希。

## 目录结构

```
image-dataset-tools/
├── idt/                    # 核心库
│   ├── dhash.py            # dHash 计算/匹配/聚组
│   ├── image.py            # 缩放/图片遍历
│   ├── quality.py          # 损坏/占位符检测
│   └── parallel.py         # 多线程工具
├── cli/                    # 命令行入口
│   ├── resize.py
│   ├── sample.py
│   ├── dedup.py
│   ├── cross_dedup.py
│   ├── quality_check.py
│   └── stats.py
├── requirements.txt
└── README.md
```
