# AzToolkit 重构与优化建议

## 优化目标与顺序

建议按以下优先级推进：

1. **P0：修复已确认的错误结果和不可运行入口**——配置路径、相机投影、启动器漏导入、文件移动、7D 框读取。
2. **P1：明确数据契约并防止静默错配**——时间戳匹配策略、传感器配对结构、原子输出和失败汇总。
3. **P1：建立可复现安装环境**——统一项目元数据，区分核心依赖与 ROS/Open3D/Torch 可选依赖。
4. **P2：清理脚本副作用和旧目录耦合**——去除导入打印、`chdir`、硬编码路径、通配符导入和旧 `toolkit.*` 引用。
5. **P2：补齐单元、集成和样例数据测试**——将本次最小复现全部固化为回归测试。

## 1. 修复默认路径与统一配置模型

### 原代码

位置：`az_toolkit/config.py:3-11`

```python
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
GLOBAL_CONFIG = {
    "simple_path": os.path.join(PACKAGE_ROOT, "..", "..", "test_data"),
}
```

该路径从包目录向上两级，实际落到仓库外；同时使用可变全局字典，任意模块都能改变进程级配置。

### 优化后

```python
from dataclasses import dataclass, replace
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent

@dataclass(frozen=True)
class ToolkitConfig:
    version: str = "0.1.0"
    author: str = "HuangWei"
    debug: bool = False
    sample_path: Path = PROJECT_ROOT / "test_data"

CONFIG = ToolkitConfig()

def with_config(config: ToolkitConfig = CONFIG, **changes) -> ToolkitConfig:
    return replace(config, **changes)
```

库函数应把路径作为显式参数；默认样例路径只服务 demo/test，不应成为生产流程的隐式输入。版本号只从项目元数据读取，不在 README、setup 和运行配置中分别维护。

## 2. 修复包内导入与数据集启动器

### 原代码

位置：`dataset/com_dataset_launcher.py:8-20` 及多个子包文件头

```python
import az_toolkit.dataset.data_stamp_rename
import az_toolkit.dataset.read_timstamp
import az_toolkit.dataset.timestamp_match

az_toolkit.dataset.select_nearest.main(...)
```

```python
try:
    from .common.misc import *
except ImportError:
    from az_toolkit.common.misc import *
```

启动器未导入 `select_nearest`。在 `dataset/` 内，`.common` 实际指向不存在的 `az_toolkit.dataset.common`；宽泛回退会掩盖真正的依赖错误。

### 优化后

```python
from pathlib import Path

from az_toolkit.dataset import (
    data_stamp_rename,
    read_timstamp,
    select_nearest,
    timestamp_match,
)


def build_common_dataset(root: str | Path, limit: int = 100) -> None:
    root = Path(root)
    if not root.is_dir():
        raise FileNotFoundError(root)

    read_timstamp.main(root, fixedTsFile=False)
    timestamp_match.main(root, limit_num=limit)
    select_nearest.main(root, root)
    data_stamp_rename.main(root)
```

其他文件统一使用真实相对层级，例如：

```python
from ..common.misc import load_timestamp, mkdir_folder
from ..extract.extract_timestamp import write_timestamp_fixed
from ..config import CONFIG
```

不要使用 `import *`。如需支持 `python file.py` 直接运行，推荐改用正式 CLI 入口，而不是靠捕获 `ImportError` 判断运行方式。

## 3. 统一点到图像投影的返回契约

### 原代码

位置：`pointcloud/pointcloud_to_image.py:24-49`

```python
pts_2d = np.dot(p_matrix, np.transpose(pts_3d_extend)).T
pts_2d = pts_2d[:, :2] / pts_2d[:, 2:3]
return pts_2d

pts_2d = project_to_uv(lidar, calib_p)
z = pts_2d[:, 2]
```

调用方需要深度，但被调用方只返回 UV；`mode` 参数除 1 外没有实现。

### 优化后

```python
import numpy as np


def project_to_uv_depth(points_xyz: np.ndarray,
                        projection: np.ndarray,
                        eps: float = 1e-8):
    points = np.asarray(points_xyz, dtype=np.float64)
    matrix = np.asarray(projection, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points_xyz must have shape (N, 3)")
    if matrix.shape != (3, 4):
        raise ValueError("projection must have shape (3, 4)")

    homogeneous = np.c_[points, np.ones(len(points))]
    projected = homogeneous @ matrix.T
    depth = projected[:, 2]
    valid = np.isfinite(projected).all(axis=1) & (depth > eps)

    uv = np.full((len(points), 2), np.nan, dtype=np.float64)
    uv[valid] = projected[valid, :2] / depth[valid, None]
    return uv, depth, valid


def project_to_depth(image, lidar, projection):
    uv, depth, valid = project_to_uv_depth(lidar, projection)
    pixels = np.full((len(uv), 2), -1, dtype=np.int64)
    finite_uv = np.isfinite(uv).all(axis=1)
    pixels[finite_uv] = np.floor(uv[finite_uv]).astype(np.int64)
    valid &= finite_uv & (
        (pixels[:, 0] >= 0) & (pixels[:, 0] < image.shape[1]) &
        (pixels[:, 1] >= 0) & (pixels[:, 1] < image.shape[0])
    )
    return valid, pixels[valid], depth[valid]
```

删除未实现的 `mode`，或用明确的枚举实现所有分支。测试至少覆盖零深度、负深度、边界像素、NaN、空输入和非法 shape。

## 4. 明确时间戳匹配是一对一还是多对一

### 原代码

位置：`dataset/timestamp_match.py:27-68`、`extract/extract_timestamp.py:71-108`

```python
j = 0
for base_ts in base_timestamp_list:
    # 找到 nearest_catch
    matched_timestamp_list.append(nearest_catch)
    # j 没有移动到命中项之后
```

当前同一个候选时间戳可被重复使用，与“每个值只会被匹配一次”的注释冲突。

### 优化后

先在 API 上明确策略：

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class TimestampPair:
    base: int
    matched: int
    delta: int
```

若业务要求一对一且输入已排序，可使用单调双指针，并在命中后消费候选：

```python
def match_one_to_one(base, candidates, threshold, *, past_only=False):
    base = sorted(map(int, base))
    candidates = sorted(map(int, candidates))
    pairs, unmatched = [], []
    j = 0

    for base_ts in base:
        while j < len(candidates) and candidates[j] < base_ts - threshold:
            j += 1

        best_index = None
        best_delta = None
        for k in range(j, len(candidates)):
            delta = candidates[k] - base_ts
            if past_only and delta > 0:
                break
            if not past_only and delta > threshold:
                break
            if abs(delta) <= threshold and (
                best_delta is None or abs(delta) < abs(best_delta)
            ):
                best_index, best_delta = k, delta

        if best_index is None:
            unmatched.append(base_ts)
            continue

        matched = candidates[best_index]
        pairs.append(TimestampPair(base_ts, matched, best_delta))
        j = best_index + 1

    return pairs, unmatched
```

如果业务确实允许多对一，应将函数命名为 `match_nearest_reusable()`，删除“一次使用”的注释，并测试重复行为。不要再靠两个独立列表和删除列表表达匹配关系；后续复制步骤直接消费 `TimestampPair`。

## 5. 修复文件操作并默认使用原子输出

### 原代码

位置：`common/misc.py:65-72`

```python
mkdir_folder(dst_path)
shutil.move(src_file, dst_path + f_name)
```

### 优化后

```python
from pathlib import Path
import shutil


def move_file(src_file, dst_dir):
    src = Path(src_file)
    dst = Path(dst_dir)
    if not src.is_file():
        raise FileNotFoundError(src)
    dst.mkdir(parents=True, exist_ok=True)
    target = dst / src.name
    return Path(shutil.move(str(src), str(target)))
```

进一步建议：

- 时间戳文件统一通过已有 `atomic_write_lines()` 写入；
- 输出数据先写到临时目录，全部成功后 rename 为最终目录；
- `data_stamp_rename` 返回成功、缺失、失败文件清单，不要只打印计数；
- 默认不覆盖已有目标，覆盖必须显式 `overwrite=True`；
- 对复制后的文件数量和时间戳数量做一致性校验。

## 6. 修复 7D/24D 框格式和逆变换

### 原代码

位置：`utils/load_box3d.py:37-52`

```python
a = np.stack(tmp.split(',')).astype(np.float32)
a = box3d_convert_7d_to_24d(a)
result.append(a)
```

函数名是 `read_box3d_result_7d`，却返回 25 元素数组。

### 优化后

```python
def read_box3d_result_7d(filename):
    result = []
    with open(filename, encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            line = line.strip()
            if not line:
                continue
            values = np.fromstring(line, sep=",", dtype=np.float32)
            if values.size != 8:
                raise ValueError(f"line {line_no}: expected 8 values")

            corners = box3d_convert_7d_to_24d(values)
            if abs(corners[1]) <= Cfg.ObjDis and abs(corners[2]) <= Cfg.ObjDis:
                result.append(values)
    return np.asarray(result, dtype=np.float32)
```

如果调用方需要 24D，提供独立的 `read_box3d_result_24d()` 或显式参数 `output_format="corners"`。

`box3d_convert_24d_to_7d()` 不应通过世界坐标轴 AABB 恢复旋转框尺寸。应使用约定顶点之间的边长度恢复 `dx/dy/dz`，heading 使用对应长边向量 `atan2(edge_y, edge_x)`；同时用 7D→24D→7D 往返测试验证中心、尺寸和角度误差。

## 7. 让 LaserScan 的文件格式声明与实现一致

### 原代码

位置：`pointcloud/laser_scan.py:8,70-94`

```python
EXTENSIONS_SCAN = ['.bin', '.txt', '.pcd']
scan = np.fromfile(filename, dtype=np.float32).reshape((-1, 4))
```

### 优化后

```python
def open_scan(self, filename):
    path = Path(filename)
    suffix = path.suffix.lower()

    if suffix == ".bin":
        raw = np.fromfile(path, dtype=np.float32)
        if raw.size % 4:
            raise ValueError(f"{path}: float count is not divisible by 4")
        points_xyzi = raw.reshape(-1, 4)
    elif suffix == ".txt":
        points_xyzi = np.loadtxt(path, dtype=np.float32, ndmin=2)
    elif suffix == ".pcd":
        points_xyzi = load_pcd_xyzi(path)  # Open3D/PCL 或自有明确解析器
    else:
        raise ValueError(f"unsupported scan format: {suffix}")

    if points_xyzi.shape[1] < 3:
        raise ValueError("scan must contain at least x, y, z")
    remission = (points_xyzi[:, 3] if points_xyzi.shape[1] > 3
                  else np.zeros(len(points_xyzi), dtype=np.float32))
    self.set_points(points_xyzi[:, :3], remission)
```

球面投影还应：

- 验证 `height/width > 0`、`fov_up > fov_down`；
- 过滤零距离、NaN/Inf 和垂直视场外的点，而不是全部夹到边缘；
- 明确边界 yaw 的环绕策略；
- 保持 `proj_x/proj_y/unproj_range` 与原始点索引对齐，并为被过滤点使用 `-1`；
- 增加同像素近点覆盖、视场外过滤和空点云测试。

## 8. 重构数据集抽取流程

### 当前问题

`Extractor.run()` 用图像时间戳直接拼接所有传感器文件名；`batch_handler()` 接受“路径列表”，入口却传入字符串；CLI 的时间间隔显式传入后是字符串（`dataset/extract_dataset.py:50-79,103-119`；`tools/batch_handler.py:11-22`）。

### 建议接口

```python
@dataclass(frozen=True)
class SensorFile:
    sensor: str
    timestamp: int
    path: Path

@dataclass(frozen=True)
class FrameGroup:
    anchor_timestamp: int
    files: dict[str, SensorFile]
```

流程应拆分为：

1. 扫描每个传感器目录并解析扩展名、时间戳；
2. 以指定 anchor 传感器生成 `TimestampPair/FrameGroup`；
3. 验证必需传感器是否齐全；
4. 按时间间隔对 `FrameGroup` 采样；
5. 写临时目录、生成 manifest，再原子提交。

CLI 至少应使用：

```python
parser.add_argument("--time-interval", type=int, default=200)
parser.add_argument("--data-root", type=Path, required=True)
parser.add_argument("--target-folder", type=Path, required=True)
```

`batch_handler()` 可接受 `Path | Iterable[Path]`，并显式把单个 Path 包装成列表，避免按字符串字符遍历。

## 9. 建立可复现的打包与可选依赖

### 原代码

`setup.py` 的 `install_requires=[]`，根和包内各有一份内容不同的 requirements；版本也不一致。

### 优化后

建议迁移到 `pyproject.toml`：

```toml
[build-system]
requires = ["setuptools>=75", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "az-toolkit"
version = "0.1.0"
requires-python = ">=3.10,<3.14"
dependencies = [
  "numpy>=1.26,<3",
  "pillow>=10",
  "scipy>=1.11",
  "tqdm>=4.66",
]

[project.optional-dependencies]
image = ["opencv-python>=4.9", "svglib>=1.5", "reportlab>=4"]
visualization = ["matplotlib>=3.8", "open3d>=0.18"]
torch = ["torch>=2.2"]
dev = ["pytest>=8", "coverage>=7", "mypy>=1.11", "ruff>=0.6"]
```

ROS1/ROS2 依赖通常不适合直接从 PyPI 一次解决，应在文档中按系统发行版说明，并让 ROS 工具延迟导入对应模块。精确版本范围应在目标 Python、CUDA、ROS 和操作系统组合上验证后再锁定。

同时：

- 删除包内 `az_toolkit/requirements.txt`，只保留一个依赖来源；
- 使用 extras 区分核心、图片、可视化、Torch 和 ROS 能力；
- CI 至少测试一个最小核心环境和一个完整非 ROS 环境；
- 增加 `python -m pytest`、构建 wheel、安装 wheel 后从临时目录导入的验证。

## 10. 清理导入副作用、硬编码路径和旧代码

### 导入副作用

删除 `az_toolkit/__init__.py:6` 的打印。把 `cal_projection_matrix_error.py:13-16` 的 `chdir/sys.path.append/print` 移到 CLI `main()` 中，内部文件路径以 `Path(__file__).resolve()` 计算，不改变进程工作目录。

### 硬编码路径

`split_dataset.py`、`video_compress.py`、`extract_video_frame.py` 和 `tools/analysis/show_w/` 的 `/home/...`、`/media/...` 全部改成 CLI 参数或配置文件。数据集随机划分接受 `seed`，并在 manifest 中记录划分参数。

### 旧模块

对 `tools/analysis/show_w/` 做二选一处理：

- 如果仍需维护，把 `toolkit.*`、`Object_showme*`、`show3DinRangeImage` 等依赖迁入当前包并增加测试；
- 如果只是历史实验脚本，移到 `examples/legacy/`，明确“不随包安装、不纳入 API 稳定性保证”。

## 性能优化点

- 时间戳匹配保持排序输入和单调指针，避免为每个 base 从头扫描候选；必要时使用 `bisect` 搜索邻居。
- `atomic_write_lines()` 当前先把全部内容拼成一个大字符串；百万级时间戳可改为在临时文件中流式写入，再 `fsync + replace`。
- `bin2pcd_raw()` 逐点 Python 写文本较慢，可用 `np.savetxt` 或二进制 PCD；同时避免先写 `.txt` 再 rename。
- 视频多线程抽帧要限制并发，因为多个 OpenCV 解码器与磁盘写入可能相互争用；基于实测吞吐选择 worker 数。
- 距离图投影的排序是 O(N log N)。若只需每像素最近点，可评估按像素分组最小深度或 `np.minimum.at`，但必须同时保留最近点索引和属性，优化前先建立基准测试。
- 可视化函数避免每帧重复创建大数组和颜色映射；对静态标定、类别颜色和边连接表进行缓存。

## 测试与验收建议

### P0 回归测试

1. `GLOBAL_CONFIG` 默认样例路径指向仓库 `test_data`，且路径归一化后存在。
2. `my_move_file(src, dst)` 的结果必须是 `dst/src.name`。
3. `project_to_uv_depth()` 返回 `(N,2)` UV、`(N,)` depth 和 `(N,)` valid；零/负深度不参与图像索引。
4. `com_dataset_launcher` 四个步骤按固定顺序调用，`select_nearest` 不再 `AttributeError`。
5. `read_box3d_result_7d()` 每行返回 8 个值，24D 读取器每行返回 25 个值。
6. `.txt`、`.bin`、`.pcd` 分别使用正确解析器；错误长度或格式必须抛异常，不能静默返回空点云。

### 时间戳测试

- 空输入、候选耗尽、阈值边界等于/超过 1；
- 一对一模式禁止重复候选，多对一模式明确允许；
- 等距候选的稳定选择规则；
- 未排序输入、重复时间戳、负值和非数字内容；
- 生成 manifest 后逐帧验证传感器文件真实存在。

### 数值与几何测试

- 四元数零范数应抛 `ValueError`；单位四元数、随机旋转矩阵往返误差；
- 7D→24D→7D 的中心、尺寸和 heading 往返；
- 相机投影对已知内外参的人工点；
- 球面投影同像素遮挡、水平环绕、垂直视场外点和 index 0 掩码。

### 集成与工程测试

- 在临时目录构造最小 image/lidar 数据集，跑完整四阶段流水线，验证文件数、文件名和时间戳一一对应；
- 在复制中途注入异常，确认旧输出不被破坏且临时目录被清理；
- 构建 wheel 后切换到仓库外目录安装并导入；
- 核心模块的导入不得打印、修改 cwd 或要求 ROS/Open3D/Torch；
- CI 中执行 `compileall`、pytest、ruff、mypy，并将核心模块覆盖率目标先设为 70%，再逐步提高。

## 低风险快速实施项（建议先做 5 项）

1. 把 `simple_path` 改为 `Path(PACKAGE_ROOT).parent / "test_data"`，并删除包导入打印。
2. 在 `com_dataset_launcher.py` 显式导入 `select_nearest`。
3. 将 `my_move_file()` 的目标改为 `os.path.join(dst_path, f_name)` 或 `Path(dst_path) / f_name`。
4. 修复 `project_to_uv/project_to_depth` 返回契约，并添加最小投影测试。
5. 让 `read_box3d_result_7d()` append 原始 7D 值，而只用 24D 角点做距离筛选。

完成以上项目后，再处理时间戳匹配策略和依赖/打包重构；这两项涉及行为契约和部署环境，建议单独提交并配套迁移说明。
