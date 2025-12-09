#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器状态检查工具
检查指定URL的响应状态，如果超时则通过Server酱发送推送通知
"""

import requests
import time
import argparse
from datetime import datetime
from typing import Dict, Any

from config import (
    SERVER_CHAN_URL,
    URLS_TO_CHECK,
    DEFAULT_TIMEOUT,
    CHECK_INTERVAL,
    VERBOSE
)


def log(message: str, verbose_only: bool = False) -> None:
    """打印日志"""
    if verbose_only and not VERBOSE:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def send_server_chan_notification(title: str, content: str = "", channel: str = "") -> Dict[str, Any]:
    """
    通过Server酱发送推送通知

    Args:
        title: 消息标题，必填，最大长度32
        content: 消息内容，选填，支持Markdown，最大长度32KB
        channel: 消息通道，选填

    Returns:
        API响应的JSON数据
    """
    data = {
        "title": title[:32],  # 限制标题长度
        "desp": content,
        "noip": 1,  # 隐藏调用IP
    }

    if channel:
        data["channel"] = channel

    try:
        response = requests.post(
            SERVER_CHAN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        result = response.json()

        if result.get("code") == 0:
            log(f"✅ 推送成功: {title}")
        else:
            log(f"❌ 推送失败: {result.get('message', '未知错误')}")

        return result
    except Exception as e:
        log(f"❌ 推送异常: {str(e)}")
        return {"code": -1, "message": str(e)}


def check_url(url: str, timeout: int = DEFAULT_TIMEOUT, name: str = "") -> Dict[str, Any]:
    """
    检查URL的响应状态

    Args:
        url: 要检查的URL
        timeout: 超时时间（秒）
        name: 服务名称（用于日志）

    Returns:
        检查结果字典
    """
    display_name = name or url
    result = {
        "url": url,
        "name": display_name,
        "success": False,
        "status_code": None,
        "response_time": None,
        "error": None
    }

    log(f"🔍 正在检查: {display_name}", verbose_only=True)

    start_time = time.time()

    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        elapsed_time = time.time() - start_time

        result["status_code"] = response.status_code
        result["response_time"] = round(elapsed_time, 2)
        result["success"] = True
        log(f"✅ {display_name} - 状态码: {response.status_code}, 响应时间: {elapsed_time:.2f}秒")

    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        result["error"] = f"请求超时 (>{timeout}秒)"
        result["response_time"] = round(elapsed_time, 2)
        log(f"❌ {display_name} - 请求超时")

    except requests.exceptions.ConnectionError as e:
        result["error"] = f"连接错误: {str(e)}"
        log(f"❌ {display_name} - 连接错误")

    except requests.exceptions.RequestException as e:
        result["error"] = f"请求异常: {str(e)}"
        log(f"❌ {display_name} - 请求异常: {str(e)}")

    return result


def check_all_urls(urls: list = None) -> list:
    """
    检查所有配置的URL

    Args:
        urls: URL配置列表，为None则使用配置文件中的列表

    Returns:
        所有检查结果的列表
    """
    if urls is None:
        urls = URLS_TO_CHECK

    results = []
    failed_services = []

    for url_config in urls:
        if isinstance(url_config, str):
            # 兼容简单的URL字符串格式
            result = check_url(url_config)
        else:
            # 字典格式配置
            result = check_url(
                url=url_config.get("url"),
                timeout=url_config.get("timeout", DEFAULT_TIMEOUT),
                name=url_config.get("name", "")
            )

        results.append(result)

        if not result["success"]:
            failed_services.append(result)

    # 如果有失败的服务，发送推送通知
    if failed_services:
        send_failure_notification(failed_services)

    return results


def send_failure_notification(failed_services: list) -> None:
    """
    发送服务故障通知

    Args:
        failed_services: 失败的服务列表
    """
    title = f"⚠️ 服务异常告警 ({len(failed_services)}个)"

    # 构建Markdown格式的消息内容
    content_lines = [
        f"## 检测时间",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 异常服务列表",
        ""
    ]

    for service in failed_services:
        content_lines.append(f"### {service['name']}")
        content_lines.append(f"- **URL**: {service['url']}")
        content_lines.append(f"- **错误**: {service['error']}")
        if service['response_time']:
            content_lines.append(f"- **响应时间**: {service['response_time']}秒")
        content_lines.append("")

    content = "\n".join(content_lines)

    send_server_chan_notification(title, content)


def run_once(urls: list = None) -> None:
    """执行一次检查"""
    log("=" * 50)
    log("开始服务器状态检查")
    log("=" * 50)

    results = check_all_urls(urls)

    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count

    log("=" * 50)
    log(f"检查完成: 成功 {success_count} 个, 失败 {fail_count} 个")
    log("=" * 50)


def run_daemon(urls: list = None, interval: int = CHECK_INTERVAL) -> None:
    """
    守护进程模式，定时检查

    Args:
        urls: URL配置列表
        interval: 检查间隔（秒）
    """
    log(f"🚀 启动守护进程模式，检查间隔: {interval}秒")

    while True:
        try:
            run_once(urls)
            log(f"💤 等待 {interval} 秒后进行下一次检查...")
            time.sleep(interval)
        except KeyboardInterrupt:
            log("👋 收到退出信号，停止检查")
            break


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="服务器状态检查工具 - 检查URL响应并通过Server酱推送告警"
    )

    parser.add_argument(
        "-u", "--url",
        type=str,
        help="要检查的单个URL（不使用配置文件中的URL列表）"
    )

    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"超时时间（秒），默认: {DEFAULT_TIMEOUT}"
    )

    parser.add_argument(
        "-d", "--daemon",
        action="store_true",
        help="守护进程模式，定时检查"
    )

    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=CHECK_INTERVAL,
        help=f"守护进程模式下的检查间隔（秒），默认: {CHECK_INTERVAL}"
    )

    parser.add_argument(
        "--test-push",
        action="store_true",
        help="测试Server酱推送功能"
    )

    args = parser.parse_args()

    # 测试推送
    if args.test_push:
        log("📤 发送测试推送...")
        result = send_server_chan_notification(
            title="🔔 测试推送",
            content="## 测试消息\n\n这是一条来自服务器状态检查工具的测试推送。\n\n如果您收到此消息，说明推送功能正常工作。"
        )
        return

    # 构建URL列表
    urls = None
    if args.url:
        urls = [{"name": args.url, "url": args.url, "timeout": args.timeout}]

    # 执行检查
    if args.daemon:
        run_daemon(urls, args.interval)
    else:
        run_once(urls)


if __name__ == "__main__":
    main()

