## 使用示例

### 1. 下载小说

支持的站点列表详见: [站点支持文档](./6-supported-sites.md)

#### 1.1 显式指定配置文件 (优先级最高)

```bash
# 使用自定义配置文件, 下载起点小说 '123456' 和 '654321'
novel-cli --config "/path/to/custom.toml" download 123456 654321
```

#### 1.2 使用当前目录下的 `settings.toml`

```bash
# 在包含 ./settings.toml 的目录中运行 CLI 即可
cd novel-folder
novel-cli download 123456 654321
```

#### 1.3 使用已注册的全局配置

```bash
# 如果当前目录下没有 settings.toml, CLI 会尝试使用已注册的全局配置
# 注册命令示例:
# novel-cli settings set-config ./path/to/settings.toml
novel-cli download 123456 654321
```

> **登录提示说明**
> 若针对当前下载站点的配置中 `mode: browser` 且启用了 `login_required: true`, 程序将自动弹出浏览器窗口引导登录,
> 请根据提示完成操作, 以便访问受限章节内容。
>
> 如果是其他模式 (如 `session`) 并启用了 `login_required: true`, CLI 将检测当前是否已登录;
> 若未登录, 将提示你在命令行中手动输入当前站点的有效 Cookie 信息

---

### 2. 全局选项

```text
novel-cli [OPTIONS] COMMAND [ARGS]...

Options:
  --config FILE   配置文件路径
  --help      显示此帮助信息并退出
```

---

### 3. 子命令一览

```text
Commands:
  download     下载小说
  interactive  小说下载与预览的交互式模式
  settings     配置下载器设置
  clean        清理本地缓存和配置文件
```

---

### 4. download 子命令

按书籍 ID 下载完整小说, 支持从命令行或配置文件读取 ID:

```bash
novel-cli download [OPTIONS] [BOOK_IDS]...
```

**参数说明**:

* `BOOK_IDS`: 要下载的书籍 ID (可选, 省略时将从配置文件读取)
* `--site [qidian|biquge|...]`: 站点名称缩写, 默认 `qidian`
* `--help`: 显示帮助信息

**示例**:

```bash
# 下载指定书籍 (默认 起点)
novel-cli download 1234567890

# 指定站点 (如 biquge)
novel-cli download --site biquge 8_8187

# 从配置文件中读取 ID
novel-cli download
```

查看完整支持站点列表: [`supported-sites.md`](./6-supported-sites.md)

---

### 5. settings 子命令

用于初始化和管理下载器设置, 包括切换语言、设置 Cookie、更新规则等:

```bash
novel-cli settings [OPTIONS] COMMAND [ARGS]...
```

**参数说明**:

* `set-lang LANG`: 在中文 (zh) 和英文 (en) 之间切换界面语言
* `set-config PATH`: 设置并保存自定义 YAML 配置文件
* `update-rules PATH`: 从 TOML/YAML/JSON 文件更新站点解析规则
* `set-cookies [SITE] [COOKIES]`: 为指定站点设置 Cookie, 可省略参数交互输入
* `init [--force]`: 在当前目录初始化默认配置文件

**示例:**

```bash
# 切换界面语言为英文
novel-cli settings set-lang en

# 使用新的 settings.toml
novel-cli settings set-config ./settings.toml

# 更新站点解析规则
novel-cli settings update-rules ./rules.toml

# 为起点设置 Cookie (方式 1: 一行输入)
novel-cli settings set-cookies qidian '{"token": "abc123"}'

# 为起点设置 Cookie (方式 2: 交互输入)
novel-cli settings set-cookies

# 初始化默认配置到当前目录
novel-cli settings init

# 强制覆盖已存在的配置文件
novel-cli settings init --force
```

---

### 6. clean 子命令

清理下载器生成的本地缓存和全局配置文件:

```bash
novel-cli clean [OPTIONS]
```

**参数说明**:

* `--logs`: 清理日志目录 (`logs/`)
* `--cache`: 清理脚本缓存与浏览器数据 (`js_script/`、`browser_data/`)
* `--state`: 清理状态文件与 cookies (`state.json`)
* `--all`: 清除所有配置、缓存、状态 (包括设置文件)
* `--yes`: 跳过确认提示
* `--help`: 显示帮助信息并退出

**示例:**

```bash
# 清理缓存目录和浏览器数据
novel-cli clean --cache

# 清理日志和状态文件
novel-cli clean --logs --state

# 交互确认后清理所有数据 (包括配置文件)
novel-cli clean --all

# 无需确认直接清理所有数据
novel-cli clean --all --yes
```

> **注意**: `--all` 会删除包括设置文件在内的所有本地数据, 请慎重使用！

---

> **提示**
>
> * 所有子命令均支持 `--help` 查看本地化帮助文本
> * 切换语言后, 帮助文本与运行时提示会同步更新为中、英文对应
