import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.rules.rules import infer_r1_with_debug, _initial_medium_signal, _norm_s2, _norm_s3

debug_file = PROJECT_ROOT / "test_system" / "output" / "a2_a3_debug_output.json"
with open(debug_file, 'r', encoding='utf-8') as f:
    debug_data = json.load(f)

for sample_id in ["A2", "A3"]:
    print(f"\n=== {sample_id} ===")
    data = debug_data[sample_id]
    # 使用 r1_input 中的 s2, s3
    r1_input = data["debug"]["r1_input"]
    s2 = r1_input["s2"]
    s3 = r1_input["s3"]
    print("s2:", json.dumps(s2, ensure_ascii=False, indent=2))
    print("s3:", json.dumps(s3, ensure_ascii=False, indent=2))

    # 规范化
    s2n = _norm_s2(s2)
    s3n = _norm_s3(s3)
    print("normalized s2:", json.dumps(s2n, ensure_ascii=False, indent=2))
    print("normalized s3:", json.dumps(s3n, ensure_ascii=False, indent=2))

    # 直接调用 _initial_medium_signal
    medium = _initial_medium_signal(s2n, s3n)
    print(f"_initial_medium_signal result: {medium}")

    # 调用 infer_r1_with_debug
    r1 = infer_r1_with_debug(s2, s3)
    print("infer_r1_with_debug result:", json.dumps(r1, ensure_ascii=False, indent=2))

    # 比较
    expected = data["debug"]["r1_output"]
    print("expected r1_output:", json.dumps(expected, ensure_ascii=False, indent=2))

    if r1["interest_level"] != expected["interest_level"]:
        print(f"*** MISMATCH: got {r1['interest_level']}, expected {expected['interest_level']}")
        print(f"   interest_reason: {r1['r1_interest_reason']}")
        print(f"   expected interest_reason: {expected['r1_interest_reason']}")