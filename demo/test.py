# 导入turnstile验证码绕过模块
import turnstile_bypass
# 导入时间模块，用于添加延时
import time

def main():
    # 初始化浏览器，设置headless=False以显示浏览器界面
    browser = turnstile_bypass.get_patched_browser(headless=True)
    # 获取浏览器标签页
    tab = browser.get_tab()

    # 访问目标验证页面
    tab.get("https://turnstile.zeroclover.io/")
    # 尝试点击并通过Turnstile验证，获取验证结果
    result = turnstile_bypass.click_turnstile_checkbox(tab)
    # 打印验证结果
    print(f"验证结果: {result}")

    time.sleep(2)  # 添加延时，观察验证过程

    # 点击提交按钮
    tab.ele("@type=submit").click()
    # 检查验证是否成功
    if tab.ele("Captcha success!"):
        print("Captcha success!")
    # 检查验证是否失败
    elif tab.ele("Captcha failed!"):
        print("Captcha failed!")

    # 关闭浏览器，释放资源
    browser.quit()

# 程序入口点
if __name__ == "__main__":
    main()
