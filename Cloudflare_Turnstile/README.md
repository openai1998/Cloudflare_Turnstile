# Cloudflare Turnstile 绕过解决方案

## 项目简介

本项目提供了一套完整的 Cloudflare Turnstile 验证码自动化绕过解决方案。通过修补浏览器中的 MouseEvent.screenX 和 MouseEvent.screenY 属性，成功绕过 Cloudflare 的鼠标轨迹检测机制，实现自动化验证并获取验证后的请求头信息。

## 项目结构

```
├── CloudflareTurnstileBypass/       # 主要实现方案
│   ├── cf_turnstile_bypass.py       # 核心实现代码
│   ├── example.py                   # 使用示例
│   ├── requirements.txt             # 依赖包列表
│   └── 说明文档.md                  # 详细说明文档
│
├── CDP-bug-MouseEvent-.screenX-.screenY-patcher/  # 浏览器补丁实现
│   ├── turnstilePatch/              # 浏览器扩展文件
│   ├── DrissionPage_example.py      # DrissionPage示例
│   ├── puppeteer-real-browser_example.js  # Puppeteer示例
│   ├── Dockerfile                   # Docker配置文件
│   └── 说明文档.md                  # 技术原理说明
│
├── demo/                            # 演示代码
│   ├── turnstile_bypass.py          # 简化版实现
│   ├── test.py                      # 基础测试代码
│   ├── test_turnstile.py            # 标准测试代码
│   ├── test_turnstile_with_cookies.py  # 完整功能测试
│   └── 技术说明.md                  # 技术实现说明
│
└── .gitignore                       # Git忽略文件配置
```

## 核心功能

- **浏览器自动化**：使用 DrissionPage 控制 Chrome 浏览器访问目标网站
- **鼠标事件修补**：通过自定义浏览器扩展修补 MouseEvent.screenX 和 MouseEvent.screenY 属性
- **验证码识别**：自动识别并点击 Turnstile 验证按钮
- **验证状态监控**：监控验证过程并等待验证完成
- **Cookie 提取**：从验证成功的会话中提取必要的 Cookie 和 Headers

## 环境要求

- Python 3.6+
- Chrome 浏览器
- DrissionPage
- loguru
- aiohttp
- attrs

## 快速开始

### 安装依赖

```bash
pip install -r CloudflareTurnstileBypass/requirements.txt
```

### 基本使用

```python
import asyncio
import aiohttp
from CloudflareTurnstileBypass.cf_turnstile_bypass import TurnstileSolver, TurnstileConfig
from loguru import logger

async def main():
    config = TurnstileConfig(
        chrome_path='C:\Program Files\Google\Chrome\Application\chrome.exe',
        max_attempts=5,
        initial_wait_time=0.6,
        proxy="http://127.0.0.1:10808",  # 可选
    )

    solver = TurnstileSolver(logger, config)

    try:
        headers = await solver.solve(
            url="https://example.com",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        print("验证成功，获取到的headers:", headers)

        # 使用验证后的headers访问目标网站
        async with aiohttp.ClientSession() as session:
            async with session.get("https://example.com", headers=headers) as response:
                print(f"访问状态码: {response.status}")

    except Exception as e:
        print(f"验证失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 高级功能

- **验证结果缓存**：自动缓存成功的验证结果，减少重复验证
- **并发控制**：支持控制最大并发任务数
- **调试功能**：支持保存验证过程的截图和录屏
- **错误重试**：内置错误处理和重试机制

## 技术原理

本项目解决了 Chrome DevTools Protocol (CDP) 中的一个已知问题：当使用 CDP 命令 `Input.dispatchMouseEvent` 时，创建的 MouseEvent/PointerEvent 对象会有"假"的 .screenX 和 .screenY 属性值（它们与 .x 和 .y 属性值相同）。Cloudflare Turnstile 能够检测到这一点并将用户标记为机器人。

我们通过浏览器扩展修补了这些属性，使其行为更接近真实用户操作，从而成功绕过 Turnstile 的检测机制。

## 注意事项

1. 本项目仅供学习和研究使用
2. 请遵守网站的使用条款和服务条款
3. 不要过度频繁地使用此工具，以免IP被封禁
4. 建议配合代理服务使用，轮换IP地址

## 参考资料

- [Cloudflare Turnstile 官方文档](https://developers.cloudflare.com/turnstile/)
- [Chrome DevTools Protocol 文档](https://chromedevtools.github.io/devtools-protocol/)
- [DrissionPage 官方文档](https://github.com/g1879/DrissionPage)
