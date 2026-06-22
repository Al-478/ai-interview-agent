import json
from app.services.llm import chat


def evaluate_answer(question: str, answer: str, position: str, api_key: str = None) -> dict:
    """评估面试回答，返回多维评价"""
    prompt = f"""你是一名资深面试官，请评估以下面试回答：

岗位：{position}
面试题：{question}
候选人回答：{answer}

请从以下维度评分（1-10分）并给出简短评语：
1. 技术准确性
2. 表达清晰度
3. 深度与细节
4. 综合表现

最后给出总分（满分10分）和一句改进建议。

请只输出 JSON 格式，不要其他文字：
{{
    "technical_accuracy": <分数>,
    "clarity": <分数>,
    "depth": <分数>,
    "overall": <分数>,
    "total_score": <平均分>,
    "feedback": "<简短评语>",
    "suggestion": "<改进建议>"
}}"""

    raw = chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        api_key=api_key,
    )

    try:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            if raw.endswith("```"):
                raw = raw[:-3]
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "technical_accuracy": 6,
            "clarity": 6,
            "depth": 6,
            "overall": 6,
            "total_score": 6.0,
            "feedback": "评估解析异常，请重试",
            "suggestion": "请重新回答",
        }
