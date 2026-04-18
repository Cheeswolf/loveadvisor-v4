from typing import Any, Dict, Optional

from app.utils.helpers import safe_list, safe_str
from app.rules.rules import map_next_step_action_to_text


def assemble_output(
    s2: Dict[str, Any],
    s3: Dict[str, Any],
    r1: Dict[str, Any],
    s5: Dict[str, Any]
) -> Dict[str, Any]:
    next_step_action = safe_str(r1.get("next_step_action"), "observe")

    return {
        "relationship_stage": safe_str(r1.get("relationship_stage")),
        "interest_level": safe_str(r1.get("interest_level")),
        "key_signals": safe_list(s2.get("key_signals")),
        "signal_summary": safe_list(s3.get("signal_summary")),
        "psychological_analysis": safe_str(
            s5.get("psychological_analysis"),
            "输入内容不足，当前无法形成有效判断。"
        ),
        "risk_points": safe_list(s5.get("risk_points")),
        "suggestions": safe_list(s5.get("suggestions")),
        "next_step": map_next_step_action_to_text(next_step_action),
    }


def default_output(
    psychological_analysis: str,
    suggestions: Optional[list] = None,
    next_step: str = "无法判断"
) -> Dict[str, Any]:
    return {
        "relationship_stage": "无法判断",
        "interest_level": "无法判断",
        "key_signals": [],
        "signal_summary": [],
        "psychological_analysis": psychological_analysis,
        "risk_points": [],
        "suggestions": suggestions if isinstance(suggestions, list) else [],
        "next_step": next_step,
    }