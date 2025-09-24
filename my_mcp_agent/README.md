# 启动运行环境
```bash
source .venv/bin/activate
```
# npx环境配置
## 【nodejs的安装】
下载地址见 : [https://nodejs.org/en/download](https://nodejs.org/en/download) 根据你的电脑环境选择适配的版本（软件LTS版本即可）。


# 以网页形式运行Agent
```bash
uv run adk web
```

# 开发自己的MCP Server
# 调试工具安装准备
## 【nodejs的安装】（同上）
下载地址见 : [https://nodejs.org/en/download](https://nodejs.org/en/download) 根据你的电脑环境选择适配的版本（软件LTS版本即可）。

## 【MCP调试工具-MCP Inspector】
官方文档中使用MCP自带的开发调试工具MCP Inspector，可参考[https://github.com/modelcontextprotocol/inspector。](https://github.com/modelcontextprotocol/inspector%E3%80%82)

```bash
npx @modelcontextprotocol/inspector node build/index.js
```
运行后在命令行点击网址或者自动的弹窗中即可进行调试。

# MCP Server上线部署
## 前言
我们将Server发布往往有多种方式，npx、uvx、docker等等，他们本质上都是把项目从远程拉取下载，从而在本地的一个隔离的运行环境中运行。一个python项目往往可以通过上传到PyPI，以uvx的方式运行；一个Java项目则推荐npx；此外我们还可以使用dockerfile，将server转换成一个容器等等。我们这里关注python的上线方式。

## Python项目上传
## PyPI账号注册与Token获取
1. 前往PyPI官网注册账号（https://pypi.org/account/login/），然后创建 API token，建议把 token 配置保存到本地（如其他API Key一般妥善保管）。

2. 然后执行该命令上传：

```text
python -m twine upload ./dist/*
```

3. 使用uvx启动服务
上传 PyPI 后，可通过执行 `uvx <你在toml中声明的对项目的命名>` 命令进行服务启动和验证。
注：别人此时也可通过该指令使用你的MCP Server。

推荐资源：
PyPI的token获取：https://blog.csdn.net/m0_56161419/article/details/138522039