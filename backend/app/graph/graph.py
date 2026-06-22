from langgraph.graph import StateGraph, END
from app.graph.state import InterviewState
from app.agents.question import generate_questions
from app.agents.evaluator import evaluate_answer
from app.agents.report import generate_report


def _router(state: InterviewState) -> InterviewState:
    """透传节点，仅用于条件路由"""
    return state


def _route(state: InterviewState) -> str:
    """入口路由：根据状态决定执行哪个节点"""
    if state["status"] == "idle":
        return "generate_questions"
    if state["status"] == "evaluating":
        return "evaluate"
    return END


def _generate_questions(state: InterviewState) -> InterviewState:
    """节点：根据岗位和技能生成面试题目列表"""
    questions = generate_questions(
        position=state["position"],
        tech_stack=state["tech_stack"],
        max_rounds=5,
        api_key=state.get("api_key"),
    )
    state["questions"] = questions
    state["current_question_index"] = 0
    state["current_question"] = questions[0]
    state["status"] = "waiting_answer"
    return state


def _evaluate(state: InterviewState) -> InterviewState:
    """节点：评估用户回答"""
    evaluation = evaluate_answer(
        question=state["current_question"],
        answer=state["user_answer"],
        position=state["position"],
        api_key=state.get("api_key"),
    )
    state["evaluation"] = evaluation
    state["evaluations"].append(evaluation)
    state["status"] = "next_question"
    return state


def _next_question(state: InterviewState) -> InterviewState:
    """节点：推进到下一题或结束"""
    state["current_question_index"] += 1
    idx = state["current_question_index"]
    if idx >= len(state["questions"]):
        state["status"] = "completed"
    else:
        state["current_question"] = state["questions"][idx]
        state["status"] = "waiting_answer"
    return state


def _generate_report(state: InterviewState) -> InterviewState:
    """节点：生成面试报告"""
    report = generate_report(
        position=state["position"],
        tech_stack=state["tech_stack"],
        evaluations=state["evaluations"],
        api_key=state.get("api_key"),
    )
    state["report"] = report
    return state


def _after_evaluate(state: InterviewState) -> str:
    """评估后的路由：下一题还是生成报告"""
    if state["status"] == "completed":
        return "report"
    return "next"


def build_graph() -> StateGraph:
    builder = StateGraph(InterviewState)

    builder.add_node("router", _router)
    builder.add_node("generate_questions", _generate_questions)
    builder.add_node("evaluate", _evaluate)
    builder.add_node("next_question", _next_question)
    builder.add_node("report", _generate_report)

    builder.set_entry_point("router")

    builder.add_conditional_edges(
        "router",
        _route,
        {
            "generate_questions": "generate_questions",
            "evaluate": "evaluate",
            END: END,
        },
    )

    # 生成题目后直接结束，返回第一题给用户
    builder.add_edge("generate_questions", END)

    # 评估后 → 下一题或报告
    builder.add_conditional_edges(
        "evaluate",
        _after_evaluate,
        {
            "report": "report",
            "next": "next_question",
        },
    )

    builder.add_edge("next_question", END)
    builder.add_edge("report", END)

    return builder.compile()
