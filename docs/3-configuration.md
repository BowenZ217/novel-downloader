## 配置

### 1. 初始化默认配置

```bash
# 创建一个新的工作目录
mkdir novel-folder

# 进入目录
cd novel-folder

# 在当前目录下生成 settings.yaml 和 rules.toml (已存在则跳过)
novel-cli settings init

# 如果想强制覆盖
novel-cli settings init --force
````

### 2. 编辑生成的 `settings.yaml`

```yaml
sites:
  qidian:
    # 小说 ID 列表
    book_ids:
      - "1234567890"
      - "0987654321"
    # 抓取模式, 可选 "session" 或 "browser"
    mode: "session"
    # 是否要登录后再爬取
    login_required: true
```

具体定义可参考 [settings.yaml 配置说明](./4-settings-schema.md)

### 3. (可选) 注册配置到 CLI

```bash
# 将当前目录下的 settings.yaml 设为默认配置
novel-cli settings set-config ./settings.yaml
```

### 4. (可选) 注册自定义规则到 CLI

```bash
novel-cli settings update-rules ./sample_rules.toml
```

### 内置默认配置

- 如果**未执行** `settings init`, 也**未通过** `--config` 或 `set-config` 指定任何配置, CLI 会使用内置默认的 [`settings.yaml`](./novel_downloader/resources/config/settings.yaml)。

### 配置文件查找顺序

CLI 启动时会按以下优先级依次查找并加载配置 (越靠前优先级越高):

1. 通过 `--config` 参数指定的文件
2. 当前工作目录下的 `./settings.yaml`
3. 已注册 (全局保存) 的配置文件
4. 包内资源目录中的内置默认文件

> 注：使用 `novel-cli settings init` 会在当前目录生成 `settings.yaml` 和 `rules.toml`, 便于作为第 2 步的起始模板。
