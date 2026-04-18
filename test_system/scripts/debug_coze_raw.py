# test_system/scripts/debug_coze_raw.py
# -*- coding: utf-8 -*-

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.coze_client import run_workflow
from configs.settings import EXTRACT_WORKFLOW_ID, S5_WORKFLOW_ID


TEST_TEXT = """A：你最近是不是对我冷了
B：哪有
A：感觉你没以前那么主动了
B：可能忙吧
A：那你会想我吗
B：会啊
"""


def pretty_print(title: str, data):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    if isinstance(data, (dict, list)):
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(data)


def main():
    pretty_print("PROJECT_ROOT", str(PROJECT_ROOT))
    pretty_print("EXTRACT_WORKFLOW_ID", EXTRACT_WORKFLOW_ID)
    pretty_print("S5_WORKFLOW_ID", S5_WORKFLOW_ID)
    pretty_print("TEST_TEXT", TEST_TEXT)

    # 1) 先测前半段
    try:
        extract_payload = {
            "chat_text": TEST_TEXT
        }
        pretty_print("EXTRACT PAYLOAD", extract_payload)

        extract_result = run_workflow(EXTRACT_WORKFLOW_ID, extract_payload)
        pretty_print("EXTRACT RESULT", extract_result)

    except Exception as e:
        pretty_print("EXTRACT EXCEPTION", repr(e))
        extract_result = None

    # 2) 再测 S5
    try:
        s5_payload = {
            "S2_output": json.dumps({
                "emotional_tone": "温",
                "initiative": "A 更主动",
                "interaction_reciprocity": "正向承接",
                "key_signals": [
                    "A 多次主动发起话题并表达感受",
                    "B 对 A 的话题进行了回应"
                ],
                "response_length": "短",
                "topic_depth": "中"
            }, ensure_ascii=False),
            "S3_output": json.dumps({
                "has_intimacy_signal": False,
                "has_relationship_probe": True,
                "has_positive_reciprocity": True,
                "has_rejection_signal": False,
                "has_push_pull_pattern": False,
                "has_sustained_coldness": False,
                "signal_summary": [
                    "A 多次主动发起话题并表达感受",
                    "B 对 A 的话题进行了简短但正面回应"
                ]
            }, ensure_ascii=False),
            "R1_output": json.dumps({
                "relationship_stage": "暧昧期",
                "interest_level": "中",
                "next_step_action": "light_probe"
            }, ensure_ascii=False),
            "user_question": ""
        }

        pretty_print("S5 PAYLOAD", s5_payload)

        s5_result = run_workflow(S5_WORKFLOW_ID, s5_payload)
        pretty_print("S5 RESULT", s5_result)

    except Exception as e:
        pretty_print("S5 EXCEPTION", repr(e))


if __name__ == "__main__":
    main()