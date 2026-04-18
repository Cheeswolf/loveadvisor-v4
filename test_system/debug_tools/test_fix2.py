#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from app.rules.rules import has_any_advanced_signal, is_low_quality_key_signals

# E2 actual data from test_results.json
s2_e2 = {
    "initiative": "A更主动",
    "response_length": "短",
    "emotional_tone": "无法判断",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接",
    "key_signals": ["A主动发起对话", "B进行简短确认"]
}
s3_e2 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": False,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": ["对话仅为简单的发起与确认，轮数过少，未识别到任何高级关系信号。"]
}

print("E2 check:")
print("  has_any_advanced_signal:", has_any_advanced_signal(s3_e2))
print("  response_length == '短':", s2_e2["response_length"] == "短")
print("  topic_depth == '浅':", s2_e2["topic_depth"] == "浅")
print("  interaction_reciprocity == '弱承接':", s2_e2["interaction_reciprocity"] == "弱承接")
print("  emotional_tone in ['温','无法判断','']:", s2_e2["emotional_tone"] in ["温", "无法判断", ""])
print("  key_signals:", s2_e2["key_signals"])
print("  is_low_quality_key_signals:", is_low_quality_key_signals(s2_e2["key_signals"]))
print()

# Also check is_judgable
from app.rules.rules import is_judgable
debug = {}
print("  is_judgable:", is_judgable(s2_e2, s3_e2, debug))
print("  debug:", debug)