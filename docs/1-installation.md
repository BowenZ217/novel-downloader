## 安装

**Python 环境**
为避免包冲突, 建议创建独立环境:
推荐使用 Conda 或 `venv` 创建独立环境, 避免包冲突:
```bash
conda create -n novel-downloader python=3.12 -y
conda activate novel-downloader
```
或
```bash
python -m venv .venv
source .venv/bin/activate
```

### 安装 novel-downloader

1. 从 PyPI 安装:

    ```bash
    pip install novel-downloader
    ```

2. 最新开发版 (从 GitHub 安装)

    ```bash
    # 克隆项目
    git clone https://github.com/BowenZ217/novel-downloader.git
    cd novel-downloader

    # 安装为库并生成 CLI
    pip install .
    ```

安装完成后, 会在系统 `PATH` 中生成 `novel-cli` 可执行命令。

## 可选功能及依赖

### 字体解密 (`decode_font` 参数)

起点一个月内更新的章节可能有字体加密

如果开启尝试解密字体功能 (`decode_font` 参数), 需要安装额外库 (注意: 解密字体准确率大约 99.x%, 并且 cpu 状态下一章约需要一分钟, GPU 状态下一章约需要 1 秒):

```bash
pip install novel-downloader[font-recovery]
```

如果启用 `use_ocr` 参数, 则需安装 [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) 及相关依赖 (请根据 paddlepaddle [文档](https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/develop/install/pip/windows-pip.html) 选择合适版本和 CUDA 支持) :

- CPU 版:
    ```bash
    python -m pip install paddlepaddle==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
    ```

- GPU 版 (请根据 CUDA 版本选用对应 paddlepaddle-gpu):
    ```bash
    python -m pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/
    ```

当配置里选择 `novel_downloader.utils.fontocr.ocr_v1` 时需要安装:

```bash
pip install paddleocr
```

当前使用版本示例:

```bash
paddleocr==2.10.0
paddlepaddle==3.0.0
```

> 提示: 仅在启用 `use_ocr` 时才需要上述依赖。

#### OCR 速度基准 (随机中文图片, 512 张)

> **测试设备**: NVIDIA GeForce RTX 3070 (8GB 显存)
>
> **提示**: 实际使用时, 请根据 GPU/CPU 内存情况调整 `batch_size`, 过大可能会因内存不足导致程序崩溃

| Batch Size | Use GPU | Total Time (s) | Avg Time per Image (ms) |
| ---------- | ------- | -------------- | ----------------------- |
| 1          | Yes     | 5.068          | 9.90                    |
| 1          | No      | 504.857        | 986.05                  |
| 8          | Yes     | 1.278          | 2.50                    |
| 8          | No      | 402.604        | 786.34                  |
| 16         | Yes     | 0.499          | 0.97                    |
| 16         | No      | 115.061        | 224.73                  |
| 32         | Yes     | 0.420          | 0.82                    |
| 32         | No      | 82.648         | 161.42                  |
| 64         | Yes     | 0.597          | 1.17                    |
| 64         | No      | 63.439         | 123.90                  |
| 128        | Yes     | 0.295          | 0.58                    |
| 128        | No      | 50.704         | 99.03                   |
| 256        | Yes     | 0.293          | 0.57                    |
| 256        | No      | 45.108         | 88.10                   |

### 异步抓取模式 (`mode=async`) (测试阶段)

基于 `aiohttp` 的异步抓取模式 (`mode=async`), 用于提升抓取性能, 适用于笔趣阁等无需登录的通用站点。

该模式使用 `asyncio + aiohttp` 进行并发网页抓取, 适合抓取大量章节时提高效率

#### 自定义请求限速策略

可在 `settings.toml` 配置文件中, 通过以下字段灵活控制请求速率, 以平衡性能与目标站点的可承受负载

```toml
request_interval = 0.0   # 默认为请求之间的最小间隔 (秒), 设置为 0 表示不强制等待
max_rps = 4              # 最大请求速率 (requests per second), 如不设置则请注释掉本行
```

* **`request_interval`**: 控制每次请求之间的最小等待时间 (秒), 设置为 `0` 可实现更高的并发性和连续性, 适用于对请求频率容忍度较高的站点。
* **`max_rps`**: 限制全局请求速率, 单位为每秒请求数(requests per second)。例如: 设为 4 则最多每秒发送 4 个请求; 若不希望启用此限制, 请注释掉该字段 (以 `#` 开头) 或将其移除。

#### 示例配置

```toml
# 网络请求层设置
[requests]
retry_times = 3                    # 请求失败重试次数
backoff_factor = 2.0
timeout = 30.0                     # 页面加载超时时间 (秒)
max_connections = 10               # 并发连接的最大数 (async)
max_rps = 4                        # 最大请求速率 (requests per second)

# 全局通用设置
[general]
request_interval = 0.0             # 同一本书各章节请求间隔 (秒)
raw_data_dir = "./raw_data"        # 原始章节 JSON/DB 存放目录
output_dir = "./downloads"         # 最终输出文件存放目录
cache_dir = "./novel_cache"        # 本地缓存目录 (字体 / 图片等)
download_workers = 4               # 并发下载线程数 (async)
parser_workers = 4                 # 并发解析线程数
use_process_pool = false           # 是否使用多进程池来处理任务
skip_existing = true               # 是否跳过已存在章节
storage_backend = "sqlite"         # 章节储存方法: json / sqlite
storage_batch_size = 30            # SQLite 批量提交的章节数量

# 各站点的特定配置
[sites.common]
mode = "async"                     # async / session
login_required = false             # 是否需要登录才能访问
```

上述配置下, Downloader 采用异步模式, 每次请求之间不强制等待 (`request_interval = 0.0`), 但将整体请求速率控制在每秒最多 4 次 (`max_rps = 4`)。

> 注意: 部分站点在面对高频的访问频率时 (例如每秒 10 次), 可能因负载压力而返回 `503 Service Temporarily Unavailable` 错误。
>
> 建议根据具体站点的响应情况, 适当调低请求速率参数, 或稍后重新运行程序继续执行 (工具支持断点续爬, 已完成的数据不会被重复抓取)。
