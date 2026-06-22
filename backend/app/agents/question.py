from app.services.llm import chat


def generate_questions(position: str, tech_stack: str, max_rounds: int = 5, api_key: str = None) -> list[str]:
    """根据岗位和技术栈生成面试题目"""
    prompt = f"""你是一名资深技术面试官，需为以下岗位生成{max_rounds}道面试题：

岗位：{position}
技术栈：{tech_stack}

要求：
- 题目覆盖技术基础、项目经验、系统设计、行为面试
- 每道题独立，递进式加深难度
- 输出格式：每行一道题，以 "1. " "2. " 等编号开头，不要其他多余文字"""

    raw = chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        api_key=api_key,
    )

    questions = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        parts = line.split(". ", 1)
        if len(parts) == 2 and parts[0].isdigit():
            questions.append(parts[1])
    if not questions:
        questions = [line for line in raw.strip().split("\n") if line.strip()]
    return questions[:max_rounds]


def choose_next_question(state: dict) -> str:
    """返回当前要问的题目"""
    idx = state["current_question_index"]
    if idx < len(state["questions"]):
        return state["questions"][idx]
    return "面试结束"
