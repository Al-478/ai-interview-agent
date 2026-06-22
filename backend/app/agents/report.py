from app.services.llm import chat


def generate_report(position: str, tech_stack: str, evaluations: list[dict], api_key: str = None) -> dict:
    """根据所有评估记录生成面试综合报告"""
    if not evaluations:
        return {
            "summary": "无面试记录",
            "total_score": 0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
        }

    eval_text = "\n".join(
        [
            f"第{i+1}题 -> 综合: {e.get('total_score', 'N/A')}, 评语: {e.get('feedback', '')}"
            for i, e in enumerate(evaluations)
        ]
    )

    scores = [e.get("total_score", 0) for e in evaluations]
    avg_score = sum(scores) / len(scores) if scores else 0

    prompt = f"""请根据以下面试记录，生成一份简洁的综合面试报告。

岗位：{position} | 技术栈：{tech_stack}
共 {len(evaluations)} 题，平均分 {avg_score:.1f}

逐题记录：
{eval_text}

请输出 JSON（不要其他文字）：
{{
    "summary": "<一段话的面试总结>",
    "total_score": {avg_score},
    "strengths": ["<优势1>", "<优势2>"],
    "weaknesses": ["<需要改进1>", "<需要改进2>"],
    "suggestions": ["<建议1>", "<建议2>"]
}}"""

    raw = chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        api_key=api_key,
    )

    import json
    try:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            if raw.endswith("```"):
                raw = raw[:-3]
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "summary": f"面试完成，共 {len(evaluations)} 题，平均分 {avg_score:.1f}",
            "total_score": avg_score,
            "strengths": [],
            "weaknesses": [],
            "suggestions": ["建议加强基础知识和项目经验的表达"],
        }
