# AI 简历解析 CLI Demo

一个可直接运行的 Python 命令行工具：读取 PDF 简历、通过 DeepSeek 提取结构化信息，并根据 JD 生成 0–100 的匹配评分。项目内置 `--mock` 模式，没有 API Key 也能完整演示。

## 功能

- `parse`：提取本地 PDF 的文本
- `extract`：输出基础信息、职业概况、个人优势、工作经历、项目经历、教育、技能、证书和语言能力 JSON
- `score`：输出综合、技能、经验、教育评分及面试问题 JSON
- Pydantic 严格校验 AI 结构化输出与评分范围
- 针对文件不存在、非 PDF、损坏/加密 PDF、空文本、空 JD 等情况给出中文错误
- 支持 `--output` 保存结果、`--verbose` 日志和离线 `--mock` 演示

## 环境要求

- Python 3.10+
- pip

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
resume-cli --help
```

真实 AI 模式使用 `.env` 配置文件。先复制示例并填入 DeepSeek API Key：

```bash
cp .env.example .env
```

```dotenv
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_MODEL=deepseek-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

默认读取当前目录的 `.env`。如需使用其他配置文件，可传入 `--config /path/to/custom.env`。

## 示例命令

解析 PDF 文本：

```bash
resume-cli parse ./resume.pdf
resume-cli parse ./resume.pdf --output resume.txt
```

结构化提取：

```bash
# 真实 DeepSeek API
resume-cli extract ./resume.pdf
resume-cli extract ./resume.pdf --config ./.env

# 无 API Key 演示
resume-cli extract ./resume.pdf --mock
```

JD 匹配评分：

```bash
resume-cli score ./resume.pdf --jd ./examples/jd.txt
resume-cli score ./resume.pdf --jd ./examples/jd.txt --config ./.env
resume-cli score ./resume.pdf --jd ./examples/jd.txt --mock --output result.json
```

`--mock` 使用简单的正则与关键词规则，目的是离线演示 CLI 流程，不代表真实 AI 评分质量。

`extract` 会将工作经历与项目经历分开，区分职责和成果，并保留简历中的量化指标。职业概况和个人优势只允许依据简历事实生成，不采集或推断性别、年龄、婚育等与岗位能力无关的信息。

## 输出示例

```json
{
  "overall_score": 82,
  "skill_score": 88,
  "experience_score": 80,
  "education_score": 75,
  "comment": "候选人的后端与前端技能覆盖岗位主要要求，但大模型项目经验需要进一步核实。",
  "interview_questions": [
    "请介绍一个你主导过的全栈项目。",
    "你是否有调用大模型 API 的实际经验？"
  ]
}
```

## 测试

```bash
python -m pytest
# 或
make test
```

测试会动态生成 PDF，覆盖真实 PDF 文本提取、Mock JSON 输出及文件错误处理，不会调用 DeepSeek API。

## 项目结构

```text
.
├── src/resume_cli/
│   ├── cli.py      # Typer 命令入口
│   ├── config.py   # .env 配置读取与校验
│   ├── deepseek.py # DeepSeek 结构化输出
│   ├── files.py    # JD 与输出文件处理
│   ├── mock.py     # 离线演示逻辑
│   ├── models.py   # Pydantic 数据模型
│   └── pdf.py      # PDF 校验与文本提取
├── tests/
├── examples/jd.txt
├── .env.example
├── Dockerfile
├── Makefile
├── requirements.txt
└── pyproject.toml
```

## 设计说明与边界

- AI 调用采用 DeepSeek Responses API 的 JSON Schema 结构化输出；DeepSeek 官方推荐使用 OpenAI-compatible Python SDK，因此项目保留 `openai` 客户端依赖，但请求地址、密钥和模型均为 DeepSeek。返回结果会再经过 Pydantic 本地校验。
- Prompt 明确要求只依据原文，不得补全未知信息，并要求评分理由可追溯到简历与 JD。
- DeepSeek 的密钥、模型和 API 地址从 `.env` 读取；该文件已被 `.gitignore` 忽略，仓库只提交无真实密钥的 `.env.example`。
- 简历通常包含个人敏感信息；真实模式会把提取出的文本发送给所配置的 AI 服务，使用前请确认已获得授权并符合组织的数据处理要求。
- 当前仅解析带文本层的 PDF。扫描件会提示文本为空，生产版本可进一步接入 OCR。
- 输入文本会分别截取前 50,000 个字符，避免异常大文件造成不可控的 API 请求。
