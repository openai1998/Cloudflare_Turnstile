import os
import tempfile
import json
import shutil
import subprocess
from sys import platform
import time

try:
    from DrissionPage import Chromium, ChromiumOptions
except ImportError:
    subprocess.check_call(['pip', 'install', 'DrissionPage'])

MANIFEST_CONTENT = {
    "manifest_version": 3,
    "name": "Turnstile Patcher",
    "version": "0.1",
    "content_scripts": [{
        "js": ["./script.js"],
        "matches": ["<all_urls>"],
        "run_at": "document_start",
        "all_frames": True,
        "world": "MAIN"
    }]
}

SCRIPT_CONTENT = """
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
let screenX = getRandomInt(800, 1200);
let screenY = getRandomInt(400, 600);
Object.defineProperty(MouseEvent.prototype, 'screenX', { value: screenX });
Object.defineProperty(MouseEvent.prototype, 'screenY', { value: screenY });
"""

def _create_extension() -> str:
    """创建临时扩展文件"""
    temp_dir = tempfile.mkdtemp(prefix='turnstile_extension_')

    try:
        manifest_path = os.path.join(temp_dir, 'manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(MANIFEST_CONTENT, f, indent=4)

        script_path = os.path.join(temp_dir, 'script.js')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(SCRIPT_CONTENT.strip())

        return temp_dir

    except Exception as e:
        _cleanup_extension(temp_dir)
        raise Exception(f"创建扩展失败: {e}")

def _cleanup_extension(path: str):
    """清理临时扩展文件"""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"清理临时文件失败: {e}")

# 在文件顶部添加正确的导入语句
from DrissionPage import ChromiumOptions, Chromium

def get_patched_browser(options: ChromiumOptions = None, headless = False) -> Chromium:
    """
    创建一个带有 Turnstile 绕过功能的浏览器实例

    Args:
        options: ChromiumOptions 对象，如果为 None 则创建默认配置

    Returns:
        Chromium: 返回配置好的浏览器实例
    """
    platform_id = "Windows NT 10.0; Win64; x64"
    if platform == "linux" or platform == "linux2":
        platform_id = "X11; Linux x86_64"
    elif platform == "darwin":
        platform_id = "Macintosh; Intel Mac OS X 10_15_7"
    user_agent =f"Mozilla/5.0 ({platform_id}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.99 Safari/537.36"

    if options is None:
        options = ChromiumOptions().auto_port()

    if headless is True:
        options.headless(True)
        options.set_user_agent(user_agent)

    options.set_argument("--no-sandbox")

    if "--blink-settings=imagesEnabled=false" in options._arguments:
        raise RuntimeError("To bypass Turnstile, imagesEnabled must be True")
    if "--incognito" in options._arguments:
        raise RuntimeError("Cannot bypass Turnstile in incognito mode. Please run in normal browser mode.")

    try:
        extension_path = _create_extension()
        options.add_extension(extension_path)
        browser = Chromium(options)
        shutil.rmtree(extension_path)
        return browser

    except Exception as e:
        if 'extension_path' in locals() and os.path.exists(extension_path):
            shutil.rmtree(extension_path)
        raise e

def click_turnstile_checkbox(tab) -> bool:
    """
    等待 Turnstile 加载完成并点击

    Args:
        tab: 由 get_patched_browser() 得到的 Chromium 的标签页对象

    Returns:
        bool: 是否通过 turnstile 验证
    """
    try:
        if tab.wait.eles_loaded("@name=cf-turnstile-response", timeout=5):
            response_ele = tab.ele("@name=cf-turnstile-response")

            # 添加响应值检查
            print(f"初始响应值: {response_ele.attr('value')}")

            if response_ele.attr("value"):
                print("验证码已自动通过，无需点击")
                return True

            # 尝试查找并点击验证码
            wrapper = response_ele.parent()

            # 打印更多调试信息
            print(f"找到验证码容器: {wrapper.tag}")

            try:
                iframe = wrapper.shadow_root.ele("tag:iframe")
                print(f"找到iframe: {iframe.tag}")
                print(f"iframe URL: {iframe.attr('src')}")  # 添加iframe URL信息

                # 尝试不同的方式查找checkbox
                iframe_body = iframe.ele("tag:body").shadow_root

                # 尝试多种选择器
                checkbox = None
                selectors = ["tag:input", "@type=checkbox", "@role=checkbox", "tag:div @role=checkbox"]

                for selector in selectors:
                    try:
                        print(f"尝试选择器: {selector}")
                        checkbox = iframe_body.ele(selector, timeout=5)
                        if checkbox:
                            print(f"找到复选框: {checkbox.tag}")
                            break
                    except Exception as e:
                        print(f"选择器 {selector} 失败: {e}")

                if checkbox:
                    checkbox.click()
                    print("已点击复选框")

                    # 检查是否成功
                    try:
                        if iframe_body.ele("@id=success", timeout=2):
                            return True
                    except:
                        pass

                    # 检查响应值是否已设置
                    if tab.ele("@name=cf-turnstile-response").attr("value"):
                        return True

                # 在返回False之前再次检查响应值
                final_value = tab.ele("@name=cf-turnstile-response").attr("value")
                print(f"最终响应值: {final_value}")
                if final_value:
                    print("验证码已自动通过")
                    return True

                return False

            except Exception as e:
                print(f"处理iframe失败: {e}")
                # 如果无法通过常规方式点击，尝试直接执行JavaScript
                js_result = tab.run_js('''
                    const iframe = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
                    if (iframe) {
                        try {
                            const checkbox = iframe.contentDocument.querySelector('input[type="checkbox"]');
                            if (checkbox) {
                                checkbox.click();
                                return true;
                            }
                        } catch (e) {}
                    }
                    return false;
                ''')
                print(f"JavaScript点击结果: {js_result}")
                return js_result
        else:
            print("未检测到 cloudflare turnstile 组件")
            return False

    except Exception as e:
        print(f"Turnstile 处理失败: {e}")
        return False

def monitor_and_solve_turnstile(tab, max_attempts=5, check_interval=2, total_timeout=60):
    """
    持续监控并处理页面上出现的所有 Turnstile 验证码

    Args:
        tab: 浏览器标签页对象
        max_attempts: 最大尝试次数
        check_interval: 检查间隔(秒)
        total_timeout: 总超时时间(秒)

    Returns:
        bool: 是否成功处理所有验证码
    """
    start_time = time.time()
    attempt = 0
    solved_count = 0

    # 多种可能的 Turnstile 验证码选择器
    turnstile_selectors = [
        "@name=cf-turnstile-response",
        "iframe[src*='challenges.cloudflare.com']",
        "iframe[src*='turnstile']",
        "div[class*='turnstile']",
        "div[data-sitekey]"
    ]

    while time.time() - start_time < total_timeout and attempt < max_attempts:
        attempt += 1
        print(f"检查验证码 - 第 {attempt} 次尝试")

        # 检查页面是否有验证码
        found_turnstile = False
        for selector in turnstile_selectors:
            try:
                if tab.ele(selector, timeout=1):
                    found_turnstile = True
                    print(f"发现验证码元素: {selector}")
                    result = click_turnstile_checkbox(tab)
                    if result:
                        solved_count += 1
                        print(f"成功处理验证码 #{solved_count}")
                    break
            except Exception as e:
                print(f"检查选择器 {selector} 时出错: {e}")

        if not found_turnstile:
            print("当前页面未检测到验证码")

        # 等待一段时间后再次检查
        time.sleep(check_interval)

        # 检查页面是否有变化
        try:
            # 获取当前URL，如果页面重定向会发生变化
            current_url = tab.url
            print(f"当前URL: {current_url}")

            # 可以添加其他页面变化检测逻辑
        except Exception as e:
            print(f"检查页面变化时出错: {e}")

    print(f"验证码监控结束: 共处理 {solved_count} 个验证码")
    return solved_count > 0
