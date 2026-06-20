import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.graph.state import InterviewState
from app.graph.graph import build_graph

router = APIRouter(prefix="/api/interview", tags=["interview"])

# 内存会话存储（生产环境应替换为 Redis / DB）
sessions: dict[str, InterviewState] = {}
_graph = build_graph()


class CreateSessionRequest(BaseModel):
    position: str
    tech_stack: str = ""


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


class CreateSessionResponse(BaseModel):
    session_id: str
    question: str
    question_index: int


class AnswerResponse(BaseModel):
    question: str
    question_index: int
    evaluation: dict
    is_finished: bool
    report: dict | None = None


@router.post("/create", response_model=CreateSessionResponse)
def create_session(req: CreateSessionRequest):
    """创建面试会话，返回第一道题"""
    session_id = uuid.uuid4().hex[:12]

    state: InterviewState = {
        "session_id": session_id,
        "position": req.position,
        "tech_stack": req.tech_stack,
        "questions": [],
        "current_question_index": 0,
        "current_question": "",
        "user_answer": "",
        "evaluation": None,
        "evaluations": [],
        "report": None,
        "status": "idle",
    }

    result = _graph.invoke(state)
    sessions[session_id] = result

    return CreateSessionResponse(
        session_id=session_id,
        question=result["current_question"],
        question_index=1,
    )


@router.post("/answer", response_model=AnswerResponse)
def submit_answer(req: AnswerRequest):
    """提交回答，触发评估并返回下一题或报告"""
    state = sessions.get(req.session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="面试会话不存在")

    state["user_answer"] = req.answer
    state["status"] = "evaluating"

    result = _graph.invoke(state)

    sessions[req.session_id] = result
    is_finished = result["status"] == "completed"

    return AnswerResponse(
        question=result.get("current_question", ""),
        question_index=result["current_question_index"] + 1,
        evaluation=result.get("evaluation") or {},
        is_finished=is_finished,
        report=result.get("report") if is_finished else None,
    )


@router.get("/state/{session_id}")
def get_state(session_id: str):
    """获取会话当前状态"""
    state = sessions.get(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    return {
        "session_id": state["session_id"],
        "position": state["position"],
        "tech_stack": state["tech_stack"],
        "current_question": state.get("current_question", ""),
        "current_question_index": state["current_question_index"],
        "total_questions": len(state.get("questions", [])),
        "evaluations": state.get("evaluations", []),
        "report": state.get("report"),
        "status": state["status"],
    }
