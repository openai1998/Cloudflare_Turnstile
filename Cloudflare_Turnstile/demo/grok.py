# 导入turnstile验证码绕过模块
import turnstile_bypass
# 导入时间模块，用于添加延时
import time

def find_and_click_turnstile(tab):
    """查找并点击Turnstile复选框"""
    # 检查是否存在turnstile元素
    if tab.ele("@name=cf-turnstile-response", timeout=3):
        print("找到Turnstile验证码")
        return turnstile_bypass.click_turnstile_checkbox(tab)

    # 尝试通过iframe直接查找
    iframes = tab.eles("tag:iframe")
    for iframe in iframes:
        try:
            src = iframe.attr("src")
            if src and ("cloudflare" in src or "turnstile" in src):
                print(f"找到Cloudflare iframe: {src}")
                # 切换到iframe
                tab.to_frame(iframe)
                # 尝试点击复选框
                checkbox = tab.ele("@type=checkbox", timeout=2)
                if checkbox:
                    checkbox.click(by_js=True)
                    print("已点击复选框")
                    # 返回主框架
                    tab.to_main_frame()
                    return True
                # 返回主框架
                tab.to_main_frame()
        except Exception as e:
            print(f"处理iframe时出错: {e}")
            # 确保返回主框架
            tab.to_main_frame()

    return False

def setup_dom_monitor(tab):
    """设置DOM监听器，监控验证码和页面刷新"""
    try:
        tab.run_js("""
            window.__turnstileDetected = false;
            window.__pageRefreshed = false;

            // 监控DOM变化，检测验证码
            if (!window.__turnstileObserver) {
                window.__turnstileObserver = new MutationObserver(function(mutations) {
                    window.__turnstileDetected = document.querySelector('iframe[src*="challenges.cloudflare.com"]') != null;
                });
                window.__turnstileObserver.observe(document.body, {childList: true, subtree: true});
            }

            // 监控页面刷新
            window.addEventListener('beforeunload', function() {
                window.__pageRefreshed = true;
            });

            // 记录当前URL，用于检测页面变化
            window.__currentUrl = window.location.href;
        """)
        print("已设置DOM监听器")
        return True
    except Exception as e:
        print(f"设置DOM监听器失败: {e}")
        return False

def check_page_refresh(tab):
    """检查页面是否刷新"""
    try:
        # 检查URL是否变化
        current_url = tab.url
        old_url = tab.run_js("return window.__currentUrl || ''")

        if current_url != old_url and old_url:
            print(f"检测到页面URL变化: {old_url} -> {current_url}")
            # 更新记录的URL
            tab.run_js(f"window.__currentUrl = '{current_url}'")
            return True

        # 检查页面刷新标志
        refreshed = tab.run_js("var r = window.__pageRefreshed || false; window.__pageRefreshed = false; return r;")
        if refreshed:
            print("检测到页面刷新")
            return True

        return False
    except Exception as e:
        print(f"检查页面刷新时出错: {e}")
        # 如果出错，假设页面已刷新
        return True

def main():
    # 初始化浏览器，设置headless=False以显示浏览器界面
    browser = turnstile_bypass.get_patched_browser(headless=False)
    # 获取浏览器标签页
    tab = browser.get_tab()

    # 开始监听网络请求
    tab.listen.start()

    # 访问目标验证页面
    tab.get("https://accounts.x.ai/sign-up?redirect=grok-com")

    # 设置初始DOM监听器
    setup_dom_monitor(tab)

    # 首次尝试处理验证码
    result = find_and_click_turnstile(tab)
    print(f"初始验证结果: {result}")

    # 检查验证码和提交按钮，有限次数
    for i in range(20):  # 增加检查次数
        print(f"第 {i+1} 次检查")

        # 检查页面是否刷新
        if check_page_refresh(tab):
            print("页面已刷新，重新设置监听器")
            setup_dom_monitor(tab)
            # 页面刷新后立即检查验证码
            find_and_click_turnstile(tab)

        # 检查是否检测到验证码
        try:
            detected = tab.run_js("return window.__turnstileDetected || false")
            if detected:
                print("检测到新的验证码")
                find_and_click_turnstile(tab)
                tab.run_js("window.__turnstileDetected = false")  # 重置检测标志
        except Exception as e:
            print(f"检查验证码时出错: {e}")
            # 如果出错，可能是页面刷新，重新设置监听器
            setup_dom_monitor(tab)

        # 尝试查找并点击提交按钮
        try:
            submit_button = tab.ele("@type=submit", timeout=1)
            if submit_button:
                print(f"找到提交按钮: {submit_button.text}")
                submit_button.click(by_js=True)
                print("已点击提交按钮")
                time.sleep(3)  # 等待提交后的响应
        except Exception as e:
            print(f"处理提交按钮时出错: {e}")

        # 检查网络请求 - 修正属性名
        try:
            # 正确的属性是 all_requests 而不是 requests
            all_requests = tab.listen.all_requests
            for req in all_requests:
                if "cloudflare" in req.url and "turnstile" in req.url:
                    print(f"检测到Turnstile请求: {req.url}")
        except Exception as e:
            print(f"检查网络请求时出错: {e}")

        time.sleep(2)  # 每2秒检查一次

    # 等待页面加载完成
    try:
        tab.wait.page_loaded()  # 正确的方法名
    except Exception as e:
        print(f"等待页面加载时出错: {e}")

    # 打印最终页面内容
    try:
        page_text = tab.ele("tag:body").text
        print(f"最终页面文本: {page_text[:100]}...")
    except Exception as e:
        print(f"获取页面文本时出错: {e}")

    # 关闭浏览器，释放资源
    browser.quit()

# 程序入口点
if __name__ == "__main__":
    main()
