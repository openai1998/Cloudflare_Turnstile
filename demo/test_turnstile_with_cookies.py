import turnstile_bypass
import time
import json

def main():
    # 创建一个带有补丁的浏览器实例
    browser = turnstile_bypass.get_patched_browser(headless=False)
    tab = browser.get_tab()
    
    try:
        # 访问测试网站
        print("正在访问测试网站...")
        # tab.get("https://turnstile.zeroclover.io/")
        tab.get("https://grok.com/?referrer=website")
        
        # 等待并点击 Turnstile 复选框
        print("\n尝试绕过 Turnstile 验证...")
        result = turnstile_bypass.click_turnstile_checkbox(tab)
        print(f"\n验证结果: {'成功' if result else '失败'}")
        
        if result:
            # 获取验证后的 cookie
            cookies = tab.get_cookies()
            print("\n获取到的 cookies:")
            for cookie in cookies:
                print(f"  {cookie['name']}: {cookie['value']}")
            
            # 获取 cf-turnstile-response 值
            turnstile_token = tab.ele("@name=cf-turnstile-response").attr("value")
            print(f"\nTurnstile Token: {turnstile_token}")
            
            # 点击提交按钮
            print("\n点击提交按钮...")
            time.sleep(2)  # 等待验证完成
            tab.ele("@type=submit").click()
            
            # 检查最终结果
            time.sleep(1)
            if tab.ele("Captcha success!"):
                print("\n最终结果: 验证成功！")
                
                # 导出验证后的 headers 信息，可用于后续请求
                headers = {
                    "User-Agent": tab.run_js("return navigator.userAgent"),
                    "Cookie": '; '.join([f"{c['name']}={c['value']}" for c in cookies]),
                    "cf-turnstile-response": turnstile_token
                }
                
                # 将 headers 保存到文件，方便后续使用
                with open("turnstile_headers.json", "w", encoding="utf-8") as f:
                    json.dump(headers, f, indent=4, ensure_ascii=False)
                print("\n验证后的 headers 已保存到 turnstile_headers.json")
                
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