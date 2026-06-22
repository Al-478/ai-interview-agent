import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI 面试官",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 AI 智能面试官")
st.caption("模拟真实面试场景，AI 出题 + 实时评估反馈")

# ==== 初始化 session_state ====
defaults = {
    "server_url": API_BASE,
    "position": "",
    "tech_stack": "",
    "api_key": "",
    "messages": [],
    "evaluations": [],
    "is_finished": False,
    "session_id": None,
    "waiting_for_answer": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ==== 侧边栏：配置 ====
with st.sidebar:
    st.header("⚙️ 面试配置")

    # ====== API Key 输入 ======
    st.subheader("🔑 DeepSeek API Key")
    api_key = st.text_input(
        "输入你的 API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-xxxxxxxxxxxxxxxx",
        help="在 platform.deepseek.com 注册免费获取",
    )
    st.session_state.api_key = api_key

    if not api_key:
        st.warning("⚠️ 请先输入 DeepSeek API Key")
    else:
        st.success("✅ API Key 已设置")

    st.divider()

    # ====== 面试岗位配置 ======
    st.subheader("📋 面试设置")

    server = st.text_input("后端地址", value=st.session_state.server_url)
    st.session_state.server_url = server

    position = st.text_input(
        "面试岗位",
        value=st.session_state.position,
        placeholder="例如：资深 Python 后端工程师",
    )
    tech_stack = st.text_input(
        "技术栈",
        value=st.session_state.tech_stack,
        placeholder="例如：FastAPI, MySQL, Redis, Docker",
    )

    if st.button("🚀 开始面试", type="primary", use_container_width=True):
        if not st.session_state.api_key:
            st.error("请先在侧边栏输入 DeepSeek API Key！")
        elif not position:
            st.warning("请填写面试岗位")
        else:
            st.session_state.position = position
            st.session_state.tech_stack = tech_stack
            st.session_state.messages = []
            st.session_state.evaluations = []
            st.session_state.is_finished = False
            st.session_state.waiting_for_answer = False

            with st.spinner("AI 正在出题..."):
                try:
                    r = requests.post(
                        f"{server}/api/interview/create",
                        json={
                            "position": position,
                            "tech_stack": tech_stack,
                            "api_key": st.session_state.api_key,
                        },
                        timeout=60,
                    )
                    if r.ok:
                        data = r.json()
                        st.session_state.session_id = data["session_id"]
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"📝 **第 1 题**：{data['question']}",
                        })
                        st.session_state.waiting_for_answer = True
                        st.rerun()
                    else:
                        st.error(f"服务异常: {r.text}")
                except requests.ConnectionError:
                    st.error("无法连接后端，请确认 uvicorn 已启动")

# ==== 主体：对话区 ====
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==== 报告区域 ====
if st.session_state.is_finished and st.session_state.get("report"):
    report = st.session_state.report
    with st.container():
        st.divider()
        st.header("📊 面试报告")

        col1, col2, col3 = st.columns(3)
        score = report.get("total_score", 0)
        col1.metric("综合评分", f"{score:.1f} / 10")
        count = len(st.session_state.evaluations)
        col2.metric("答题数", f"{count} 题")
        avg = (
            sum(e.get("total_score", 0) for e in st.session_state.evaluations) / count
            if count else 0
        )
        col3.metric("均分", f"{avg:.1f}")

        st.markdown(f"**总结**：{report.get('summary', '')}")

        if report.get("strengths"):
            st.success("**优势**\n\n" + "\n".join(f"- {s}" for s in report["strengths"]))
        if report.get("weaknesses"):
            st.error("**需改进**\n\n" + "\n".join(f"- {w}" for w in report["weaknesses"]))
        if report.get("suggestions"):
            st.info("**学习建议**\n\n" + "\n".join(f"- {s}" for s in report["suggestions"]))

# ==== 输入 ====
if st.session_state.waiting_for_answer and not st.session_state.is_finished:
    user_input = st.chat_input("输入你的回答...")

    if user_input:
        # 记录用户回答
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("AI 评估中..."):
            try:
                r = requests.post(
                    f"{server}/api/interview/answer",
                    json={
                        "session_id": st.session_state.session_id,
                        "answer": user_input,
                    },
                    timeout=60,
                )
                if r.ok:
                    data = r.json()
                    ev = data.get("evaluation", {})
                    st.session_state.evaluations.append(ev)

                    # 构建评估结果消息
                    eval_msg = (
                        f"📋 **评估结果**\n\n"
                        f"| 维度 | 评分 |\n"
                        f"|------|------|\n"
                        f"| 技术准确性 | {ev.get('technical_accuracy', '-')}/10 |\n"
                        f"| 表达清晰度 | {ev.get('clarity', '-')}/10 |\n"
                        f"| 深度与细节 | {ev.get('depth', '-')}/10 |\n"
                        f"| 综合表现 | {ev.get('overall', '-')}/10 |\n\n"
                        f"💬 {ev.get('feedback', '')}\n\n"
                        f"💡 {ev.get('suggestion', '')}"
                    )
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": eval_msg,
                    })

                    if data["is_finished"]:
                        # 面试结束，保存报告
                        st.session_state.is_finished = True
                        st.session_state.report = data.get("report")
                        st.session_state.waiting_for_answer = False
                    else:
                        # 追加下一题到对话
                        next_q = data.get("question", "")
                        next_idx = data.get("question_index", 1)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"📝 **第 {next_idx} 题**：{next_q}",
                        })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ 评估失败: {r.text}",
                    })
            except requests.ConnectionError:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "❌ 无法连接后端",
                })

        st.rerun()

elif not st.session_state.session_id:
    st.info("👈 在侧边栏输入 API Key 和面试信息，点击「开始面试」启动")

# ==== 快捷提示 ====
with st.sidebar:
    st.divider()
    st.caption("🔑 获取 Key: platform.deepseek.com → 注册 → API Keys")
    st.caption("⌨️ 快捷键：Enter 发送 | Shift+Enter 换行")
