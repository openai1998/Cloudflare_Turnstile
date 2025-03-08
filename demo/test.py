import turnstile_bypass
import time

def main():
    browser = turnstile_bypass.get_patched_browser(headless=False)
    tab = browser.get_tab()
    
    tab.get("https://turnstile.zeroclover.io/")
    result = turnstile_bypass.click_turnstile_checkbox(tab)
    print(f"验证结果: {result}")
    
    time.sleep(2)  # 添加延时，观察验证过程
    
    tab.ele("@type=submit").click()
    if tab.ele("Captcha success!"):
        print("Captcha success!")
    elif tab.ele("Captcha failed!"):
        print("Captcha failed!")

    browser.quit()

if __name__ == "__main__":
    main()