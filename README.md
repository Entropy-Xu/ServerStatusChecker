# 服务器状态检查工具

一个简单的服务器状态检查工具，可以检测指定URL的响应状态，如果超时或异常则通过 [Server酱](https://sct.ftqq.com/) 发送推送通知到手机。

## 功能特性

- ✅ 检查URL响应状态和响应时间
- ✅ 支持自定义超时时间
- ✅ 支持批量检查多个URL
- ✅ 超时或异常时自动通过Server酱推送告警
- ✅ 支持守护进程模式，定时自动检查
- ✅ 支持Markdown格式的告警消息
- ✅ 支持 GitHub Actions 自动化部署

## 快速开始

### 方式一：GitHub Actions 部署（推荐）

使用 GitHub Actions 可以免费实现定时检查，无需自己的服务器。

#### 1. Fork 本仓库

点击右上角的 Fork 按钮，将仓库 fork 到你的账号下。

#### 2. 配置 Environment 和 Secrets

由于工作流使用了 `environment: Basic`，你需要创建一个名为 `Basic` 的 Environment 并在其中配置 Secrets。

**步骤：**

1. 进入你 fork 的仓库，点击 **Settings**
2. 在左侧菜单中点击 **Environments**
3. 点击 **New environment**
4. 输入名称 `Basic`，点击 **Configure environment**
5. 在 **Environment secrets** 部分，点击 **Add secret** 添加以下 Secrets：

| Secret 名称 | 必填 | 说明 |
|------------|------|------|
| `SENDKEY` | ✅ | Server酱的 SendKey，从 [Server酱官网](https://sct.ftqq.com/) 获取 |
| `CHECK_URLS` | ✅ | 要检查的URL列表，JSON格式（见下方示例） |

> ⚠️ **注意**：Secrets 必须添加到 `Basic` Environment 中，而不是 Repository secrets，否则工作流无法读取到这些变量。

**CHECK_URLS 格式示例：**

```json
[{"name":"我的网站","url":"https://www.example.com","timeout":10},{"name":"API服务","url":"https://api.example.com/health","timeout":5}]
```

> 💡 **提示**：JSON 必须写成一行，不能有换行符。

#### 3. 启用 GitHub Actions

进入仓库的 **Actions** 标签页，点击 "I understand my workflows, go ahead and enable them" 启用工作流。

#### 4. 手动测试

在 Actions 页面，选择 "Server Status Check" 工作流，点击 "Run workflow" 手动触发一次检查。

#### 5. 自动定时检查

工作流默认每 5 分钟自动运行一次。如需修改频率，编辑 `.github/workflows/server-status-check.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '*/5 * * * *'  # 每5分钟
  # - cron: '*/10 * * * *'  # 每10分钟
  # - cron: '0 * * * *'     # 每小时
```

---

### 方式二：本地部署

#### 安装

```bash
# 克隆项目
git clone https://github.com/your-username/ServerStatusChecker.git
cd ServerStatusChecker

# 安装依赖
pip install -r requirements.txt
```

#### 配置环境变量

```bash
# 必需
export SENDKEY="你的Server酱SendKey"
export CHECK_URLS='[{"name":"我的网站","url":"https://example.com","timeout":10}]'

# 可选
export DEFAULT_TIMEOUT=10
export CHECK_INTERVAL=300
export VERBOSE=true
```

#### 运行

```bash
# 执行一次检查
python server_status_checker.py

# 守护进程模式
python server_status_checker.py -d
```

---

## 使用方法

### 1. 检查配置的所有URL

```bash
python server_status_checker.py
```

### 2. 检查单个URL

```bash
python server_status_checker.py -u https://www.example.com
```

### 3. 指定超时时间

```bash
python server_status_checker.py -u https://www.example.com -t 5
```

### 4. 守护进程模式（定时检查）

```bash
# 使用默认间隔（5分钟）
python server_status_checker.py -d

# 指定检查间隔（60秒）
python server_status_checker.py -d -i 60
```

### 5. 测试推送功能

```bash
python server_status_checker.py --test-push
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `-u, --url` | 要检查的单个URL |
| `-t, --timeout` | 超时时间（秒），默认10秒 |
| `-d, --daemon` | 守护进程模式，定时检查 |
| `-i, --interval` | 检查间隔（秒），默认300秒 |
| `--test-push` | 测试Server酱推送功能 |

## 环境变量

| 变量名 | 必填 | 说明 | 默认值 |
|--------|------|------|--------|
| `SENDKEY` | ✅ | Server酱 SendKey | - |
| `CHECK_URLS` | ✅ | URL列表（JSON格式） | - |
| `DEFAULT_TIMEOUT` | ❌ | 默认超时时间（秒），留空则使用默认值 | 10 |
| `CHECK_INTERVAL` | ❌ | 检查间隔（秒），留空则使用默认值 | 300 |
| `VERBOSE` | ❌ | 是否启用详细日志 | true |

> 💡 **提示**：在 GitHub Actions 中，可选的环境变量如果不需要设置，直接不添加对应的 Secret 即可，程序会自动使用默认值。

## 推送效果

当检测到服务异常时，会收到类似这样的推送：

**标题**: ⚠️ 服务异常告警 (1个)

**内容**:
```markdown
## 检测时间
2025-12-09 10:30:00

## 异常服务列表

### 我的网站
- **URL**: https://www.example.com
- **错误**: 请求超时 (>10秒)
- **响应时间**: 10.01秒
```

## 定时任务设置（可选）

如果不想使用守护进程模式或 GitHub Actions，也可以使用系统的定时任务：

### macOS/Linux (crontab)

```bash
# 编辑定时任务
crontab -e

# 每5分钟检查一次
*/5 * * * * SENDKEY=xxx CHECK_URLS='[...]' /usr/bin/python3 /path/to/server_status_checker.py >> /var/log/server_check.log 2>&1
```

## 常见问题

### Q: 工作流运行失败，提示 Secrets 读取为空？

**A**: 请确保 Secrets 是添加到 `Basic` Environment 中的，而不是 Repository secrets。具体步骤：
1. Settings → Environments → 点击 `Basic`（如果没有则新建）
2. 在 Environment secrets 中添加 `SENDKEY` 和 `CHECK_URLS`

### Q: 报错 `ValueError: invalid literal for int()`？

**A**: 这是因为 `DEFAULT_TIMEOUT` 被设置为空字符串。解决方法：
- 如果不需要自定义超时时间，不要添加 `DEFAULT_TIMEOUT` Secret
- 如果要添加，确保值是一个有效的数字（如 `10`）

### Q: CHECK_URLS 格式怎么写？

**A**: 必须是有效的 JSON 格式，且写成一行：
```json
[{"name":"网站名","url":"https://example.com","timeout":10}]
```

多个 URL 用逗号分隔：
```json
[{"name":"网站1","url":"https://example1.com","timeout":10},{"name":"网站2","url":"https://example2.com","timeout":5}]
```

### Q: 如何修改检查频率？

**A**: 编辑 `.github/workflows/server-status-check.yml` 中的 cron 表达式：
```yaml
schedule:
  - cron: '*/5 * * * *'   # 每5分钟（默认）
  - cron: '*/10 * * * *'  # 每10分钟
  - cron: '0 * * * *'     # 每小时
  - cron: '0 */6 * * *'   # 每6小时
```

## License

MIT
