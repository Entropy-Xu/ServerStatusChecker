# 服务器状态检查配置文件
import os
import json

# Server酱 SendKey（从环境变量读取）
SENDKEY = os.environ.get("SENDKEY", "")

# Server酱 API 地址
SERVER_CHAN_URL = f"https://sctapi.ftqq.com/{SENDKEY}.send" if SENDKEY else ""

# 要检查的URL列表（从环境变量读取，JSON格式）
# 格式: [{"name": "服务名称", "url": "检查地址", "timeout": 超时秒数}]
# 环境变量示例: CHECK_URLS='[{"name":"我的网站","url":"https://example.com","timeout":10}]'
def get_urls_from_env():
    urls_json = os.environ.get("CHECK_URLS", "")
    if urls_json:
        try:
            return json.loads(urls_json)
        except json.JSONDecodeError:
            print("警告: CHECK_URLS 环境变量格式错误，使用默认配置")
    # 默认配置（本地开发时使用）
    return [
        {"name": "示例服务", "url": "https://www.example.com", "timeout": 10},
    ]

URLS_TO_CHECK = get_urls_from_env()

# 默认超时时间（秒）
DEFAULT_TIMEOUT = int(os.environ.get("DEFAULT_TIMEOUT", "10"))

# 检查间隔（秒），用于定时检查模式
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "300"))  # 5分钟

# 是否启用详细日志
VERBOSE = os.environ.get("VERBOSE", "true").lower() == "true"
