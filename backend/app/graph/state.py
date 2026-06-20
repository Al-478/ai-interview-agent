from typing import TypedDict, Optional


class InterviewState(TypedDict):
    """LangGraph 面试对话状态"""

    session_id: str
    position: str
    tech_stack: str

    questions: list[str]
    current_question_index: int
    current_question: str

    user_answer: str
    evaluation: Optional[dict]

    evaluations: list[dict]
    report: Optional[dict]

    status: str
    # status 状态机：
    #   "idle"             — 等待生成题目
    #   "waiting_answer"   — 已出题，等待用户回答
    #   "evaluating"       — 正在评估回答
    #   "next_question"    — 准备下一题
    #   "completed"        — 面试结束
