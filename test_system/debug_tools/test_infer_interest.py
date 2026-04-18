#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from app.rules.rules import infer_interest_level

# Test A2-like sample
s2_a2 = {
    "initiative": "双方接近",
    "response_length": "中",
    "emotional_tone": "热",
    "topic_depth": "中",
    "interaction_reciprocity": "正向承接",
    "key_signals": ["表达共情", "提出邀约"]
}
s3_a2 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": False,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": ["基础互动"]
}

relationship_stage = "初识期"
print(f"relationship_stage: {relationship_stage}")
interest = infer_interest_level(s2_a2, s3_a2, relationship_stage)
print(f"interest_level: {interest}")
print()

# Also test with positive_reciprocity = True
s3_a2_pos = s3_a2.copy()
s3_a2_pos["has_positive_reciprocity"] = True
interest2 = infer_interest_level(s2_a2, s3_a2_pos, relationship_stage)
print(f"With has_positive_reciprocity=True: {interest2}")