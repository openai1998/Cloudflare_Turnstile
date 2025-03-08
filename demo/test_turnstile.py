import turnstile_bypass
import time

def main():
    # 创建一个带有补丁的浏览器实例
    browser = turnstile_bypass.get_patched_browser(headless=False)
    tab = browser.get_tab()
    
    try:
        # 访问测试网站
        print("正在访问测试网站...")
        tab.get("https://turnstile.zeroclover.io/")
        
        # 等待并点击 Turnstile 复选框
        print("\n尝试绕过 Turnstile 验证...")
        result = turnstile_bypass.click_turnstile_checkbox(tab)
        print(f"\n验证结果: {'成功' if result else '失败'}")
        
        if result:
            # 如果验证成功，点击提交按钮
            print("\n点击提交按钮...")
            time.sleep(2)  # 等待验证完成
            tab.ele("@type=submit").click()
            
            # 检查最终结果
            time.sleep(1)
            if tab.ele("Captcha success!"):
                print("\n最终结果: 验证成功！")
            elif tab.ele("Captcha failed!"):
                print("\n最终结果: 验证失败！")
        
    except Exception as e:
        print(f"\n测试过程出错: {e}")
    
    finally:
        # 确保浏览器正常关闭
        print("\n正在关闭浏览器...")
        browser.quit()

if __name__ == "__main__":
    main()