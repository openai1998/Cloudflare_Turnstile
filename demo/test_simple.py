import turnstile_bypass
import time

def main():
    # 初始化带有补丁的浏览器
    print("初始化浏览器...")
    browser = turnstile_bypass.get_patched_browser(headless=False)
    tab = browser.get_tab()
    
    try:
        # 访问测试网站
        print("访问测试网站...")
        tab.get("https://turnstile.zeroclover.io/")
        
        # 等待页面加载
        time.sleep(2)
        
        # 尝试绕过验证
        print("尝试绕过 Turnstile 验证...")
        result = turnstile_bypass.click_turnstile_checkbox(tab)
        
        # 显示验证结果
        if result:
            print("\n✅ Turnstile 验证成功!")
            
            # 获取验证令牌
            token = tab.ele("@name=cf-turnstile-response").attr("value")
            print(f"验证令牌: {token[:20]}...{token[-20:] if token else ''}")
            
            # 提交表单
            print("\n提交表单...")
            tab.ele("@type=submit").click()
            time.sleep(1)
            
            # 检查最终结果
            if tab.ele("Captcha success!"):
                print("\n🎉 表单提交成功!")
            else:
                print("\n❌ 表单提交失败!")
        else:
            print("\n❌ Turnstile 验证失败!")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    
    finally:
        # 等待几秒查看结果
        time.sleep(3)
        print("\n关闭浏览器...")
        browser.quit()

if __name__ == "__main__":
    main()