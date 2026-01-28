# AI News Daily Digest

每天自动收集 AI 领域新闻，生成摘要邮件并发送到指定邮箱。

## 功能

- 从多个 RSS 源和中文 AI 媒体采集新闻
- 自动去重和分类（技术进展、产品发布、大公司动向、投融资）
- 生成响应式 HTML 邮件
- 通过 GitHub Actions 每天北京时间 8:00 自动运行

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写：

```bash
cp .env.example .env
```

需要配置：
- `SMTP_SERVER` - SMTP 服务器（如 `smtp.qq.com`）
- `SMTP_PORT` - 端口（SSL 用 `465`，TLS 用 `587`）
- `SMTP_USER` - 发件人邮箱
- `SMTP_PASSWORD` - SMTP 授权码
- `RECEIVER_EMAIL` - 收件人邮箱

### 3. 本地运行

```bash
python main.py
```

### 4. GitHub Actions 部署

1. Fork 本仓库
2. 在仓库 Settings → Secrets and variables → Actions 中添加上述环境变量
3. Actions 会每天 UTC 00:00（北京时间 08:00）自动运行
4. 也可在 Actions 页面手动触发

## 自定义新闻源

编辑 `config.yaml` 添加或修改 RSS 源和网页爬取目标。

## 项目结构

```
├── config.yaml              # 新闻源配置
├── main.py                  # 入口脚本
├── news_collector.py        # 新闻采集（RSS + 网页爬取）
├── email_sender.py          # 邮件发送（SMTP）
├── email_template.html      # 邮件 HTML 模板
├── requirements.txt         # Python 依赖
├── .github/workflows/       # GitHub Actions
├── .env.example             # 环境变量示例
└── README.md                # 使用说明
```
