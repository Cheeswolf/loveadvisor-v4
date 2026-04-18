#!/usr/bin/env python3
"""
输出B类样本的完整debug返回（JSON格式）
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.pipeline_orchestrator import run_analysis

def get_debug_output():
    # B1样本
    chat_text = "A：今天怎么不找我\nB：在想你啊\nA：真的假的\nB：骗你干嘛\nA：那你想我什么\nB：想见你"
    user_question = "他对我有兴趣吗？"

    print("测试B1样本（mock provider）...")
    result = run_analysis(chat_text, user_question, provider_name="mock", debug=True)

    # 提取debug信息
    debug_info = result.get("debug", {})

    # 输出为JSON格式
    output = {
        "sample": "B1",
        "provider": "mock",
        "final_result": {
            "relationship_stage": result.get("relationship_stage"),
            "interest_level": result.get("interest_level"),
            "psychological_analysis": result.get("psychological_analysis"),
            "risk_points": result.get("risk_points"),
            "suggestions": result.get("suggestions"),
            "next_step": result.get("next_step")
        },
        "debug_info": debug_info
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output

if __name__ == "__main__":
    get_debug_output()