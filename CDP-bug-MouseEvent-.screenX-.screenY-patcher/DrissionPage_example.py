# 导入所需的模块
from DrissionPage import Chromium, ChromiumOptions  # 导入DrissionPage的浏览器和配置类
import time  # 导入时间模块用于延时
import os  # 导入os模块用于文件路径操作

# 创建浏览器配置对象
co = ChromiumOptions()  # 实例化ChromiumOptions对象
co.auto_port()  # 自动设置调试端口

co.set_timeouts(base=1)  # 设置基本超时时间为1秒

# change this to the path of the folder containing the extension
EXTENSION_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "turnstilePatch"))  # 获取扩展程序的绝对路径
co.add_extension(EXTENSION_PATH)  # 添加扩展程序
"""
# uncomment this if you want to use headless mode
co.headless()  # 启用无头模式

# 根据操作系统设置平台标识符
from sys import platform
if platform == "linux" or platform == "linux2":
    platformIdentifier = "X11; Linux x86_64"  # Linux系统标识符
elif platform == "darwin":
    platformIdentifier = "Macintosh; Intel Mac OS X 10_15_7"  # MacOS系统标识符
elif platform == "win32":
    platformIdentifier = "Windows NT 10.0; Win64; x64"  # Windows系统标识符

# 设置User-Agent
co.set_user_agent(f"Mozilla/5.0 ({platformIdentifier}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
"""
# 初始化浏览器和页面
browser = Chromium(co)  # 创建浏览器实例
page = browser.get_tabs()[-1]  # 获取最后一个标签页
page.get("https://turnstile.zeroclover.io/")  # 访问目标网址

def getTurnstileToken():
    """获取Turnstile验证token的函数"""
    page.run_js("try { turnstile.reset() } catch(e) { }")  # 重置turnstile验证

    turnstileResponse = None  # 初始化响应变量

    for i in range(0, 15):  # 尝试15次
        try:
            # 尝试获取turnstile响应
            turnstileResponse = page.run_js("try { return turnstile.getResponse() } catch(e) { return null }")
            if turnstileResponse:
                return turnstileResponse
            
            # 定位并操作验证码元素
            challengeSolution = page.ele("@name=cf-turnstile-response")  # 获取验证码响应元素
            challengeWrapper = challengeSolution.parent()  # 获取父元素
            challengeIframe = challengeWrapper.shadow_root.ele("tag:iframe")  # 获取iframe元素
            challengeIframeBody = challengeIframe.ele("tag:body").shadow_root  # 获取iframe中的body元素
            challengeButton = challengeIframeBody.ele("tag:input")  # 获取验证按钮
            challengeButton.click()  # 点击验证按钮
        except:
            pass
        time.sleep(1)  # 等待1秒
    page.refresh()  # 刷新页面
    raise Exception("failed to solve turnstile")  # 抛出异常

# 持续获取token并打印
while True:
    print(getTurnstileToken())