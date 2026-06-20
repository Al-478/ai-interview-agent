# 🤖 AI Interview Agent — 智能面试官

基于大语言模型（LLM）的全栈 AI 面试系统，支持根据目标岗位和技术栈自动生成面试题，对候选人回答进行多维度评估，并生成结构化面试报告。

> **开发周期**：2026.05 — 2026.06 | **作者**：王铭基

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────┐
│                    Frontend                      │
│              Streamlit Chat UI                   │
│         http://localhost:8501                    │
└────────────────────┬────────────────────────────┘
                     │ REST API (HTTP)
                     ▼
┌─────────────────────────────────────────────────┐
│                FastAPI Backend                   │
│                  Port :8000                       │
│  ┌──────────────────────────────────────────┐   │
│  │         LangGraph State Machine           │   │
│  │                                          │   │
│  │   idle → waiting_answer → evaluating     │   │
│  │            ↑                    ↓         │   │
│  │            └── next_question ←─┘         │   │
│  │                        ↓                  │   │
│  │                    completed              │   │
│  │                        ↓                  │   │
│  │                     report                │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Question │ │Evaluator │ │  Report  │        │
│  │  Agent   │ │  Agent   │ │  Agent   │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘        │
│       └─────────────┼────────────┘              │
│                     ▼                            │
│            ┌────────────────┐                   │
│            │   LLM Service  │                   │
│            │ (DeepSeek API) │                   │
│            └────────────────┘                   │
└─────────────────────────────────────────────────┘
```

---

## 🚀 核心特性

| 特性 | 说明 |
|------|------|
| **AI 出题** | 根据岗位 + 技术栈动态生成递进式面试题，覆盖技术基础、项目经验、系统设计、行为面试 |
| **多维评估** | 四维评分体系——技术准确性 / 表达清晰度 / 知识深度 / 综合表现（1-10 分） |
| **状态机编排** | 基于 LangGraph 的有限状态自动机，面试流程清晰可控、易扩展 |
| **多 Agent 协作** | 题目生成 Agent → 评估 Agent → 报告 Agent，关注点分离，Prompt 独立优化 |
| **结构化报告** | 自动汇总总分、平均分、优势、不足、学习建议 |
| **对话式 UI** | Streamlit 构建的聊天界面，模拟真实面试体验 |
| **Docker 部署** | 一键容器化，跨环境一致运行 |

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **LLM** | DeepSeek Chat API（OpenAI 兼容接口） |
| **编排框架** | LangGraph（状态机 / 工作流） |
| **后端** | FastAPI + Uvicorn + Pydantic |
| **前端** | Streamlit |
| **容器化** | Docker（python:3.11-slim） |

---

## 📁 项目结构

```
ai-interview-agent/
├── backend/
│   ├── Dockerfile                  # 容器化配置
│   ├── requirements.txt            # Python 依赖
│   ├── .env                        # 环境变量（API Key 等）
│   └── app/
│       ├── main.py                 # FastAPI 入口
│       ├── core/
│       │   └── config.py           # 配置管理（从环境变量读取）
│       ├── api/
│       │   └── interview.py        # REST API 端点
│       ├── graph/
│       │   ├── state.py            # 面试状态类型定义
│       │   └── graph.py            # LangGraph 状态机构建
│       ├── agents/
│       │   ├── question.py         # 题目生成 Agent
│       │   ├── evaluator.py        # 答案评估 Agent
│       │   └── report.py           # 报告生成 Agent
│       └── services/
│           └── llm.py              # LLM 调用封装层
└── frontend/
    └── app.py                      # Streamlit 前端界面
```

---

## ⚡ 快速启动

### 1. 配置环境变量

```bash
cd backend
cp .env.example .env   # 编辑 .env 填入你的 DEEPSEEK_API_KEY
```

### 2. Docker 一键启动（推荐）

```bash
cd backend
docker build -t ai-interview .
docker run -p 8000:8000 --env-file .env ai-interview
```

### 3. 本地开发启动

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端（新终端）
cd frontend
pip install streamlit requests
streamlit run app.py
```

### 4. 使用

1. 浏览器打开 `http://localhost:8501`
2. 在侧边栏填写**面试岗位**（如"Python 后端开发"）和**技术栈**（如"FastAPI, MySQL, Redis"）
3. 点击「开始面试」→ AI 自动出第一题
4. 逐题回答 → 实时获取四维评估
5. 完成全部题目 → 查看综合面试报告

---

## 🔌 API 文档

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/interview/create` | 创建面试会话，返回首题 |
| `POST` | `/api/interview/answer` | 提交回答，返回评估 + 下一题/报告 |
| `GET` | `/api/interview/state/{session_id}` | 查询会话状态 |
| `GET` | `/health` | 健康检查 |

### 请求示例

```bash
# 创建面试
curl -X POST http://localhost:8000/api/interview/create \
  -H "Content-Type: application/json" \
  -d '{"position": "Python 后端工程师", "tech_stack": "FastAPI, MySQL, Redis"}'

# 提交回答
curl -X POST http://localhost:8000/api/interview/answer \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123def456", "answer": "FastAPI 是一个现代的 Python Web 框架..."}'
```

---

## 🧠 设计决策

- **LangGraph 状态机**：将面试流程建模为有限状态自动机，相比简单的循环调用，状态流转更清晰，后续可扩展子状态（如追问、超时处理）
- **Agent 拆分**：三个 Agent 各有独立的 Prompt 和 temperature 配置（出题 0.8 → 评估 0.3 → 报告 0.5），关注点分离便于独立调优
- **JSON 容错**：评估和报告 Agent 均有 JSON 解析失败的 fallback 默认值，保证系统不会因 LLM 输出格式异常而崩溃
- **LLM 服务抽象**：通过 `services/llm.py` 封装模型调用，切换模型供应商只需改一处配置

---

## 📝 License

MIT

---

> 💡 如有问题或建议，欢迎提 Issue！
