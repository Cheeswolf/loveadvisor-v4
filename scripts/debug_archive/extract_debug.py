import json
import requests
import sys

API_URL = "http://127.0.0.1:8000/api/v1/analyze"
PROVIDER_NAME = "deepseek"

def analyze_with_debug(input_text, sample_id):
    payload = {
        "chat_text": input_text,
        "user_question": "",
        "provider_name": PROVIDER_NAME,
        "debug": True
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception as e:
        print(f"Error for {sample_id}: {e}")
        return None

def main():
    # Load test cases
    with open("test_system/data/test_cases.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    target_samples = ["A2", "A3", "B1", "C2"]
    target_cases = [c for c in cases if c["sample_id"] in target_samples]

    results = []
    for case in target_cases:
        sample_id = case["sample_id"]
        input_text = case["input_text"]
        expected_stage = case["expected_relationship_stage"]
        expected_interest = case["expected_interest_level"]

        print(f"Processing {sample_id}...")
        data = analyze_with_debug(input_text, sample_id)
        if data is None:
            continue

        # Extract result
        result = data.get("result", {})
        actual_stage = result.get("relationship_stage")
        actual_interest = result.get("interest_level")

        # Extract debug info
        debug = result.get("debug")
        if debug:
            s2 = debug.get("s2")
            s3 = debug.get("s3")
            r1_output = debug.get("r1_output", {})
            r1_interest_reason = r1_output.get("r1_interest_reason")
        else:
            s2 = None
            s3 = None
            r1_interest_reason = None

        results.append({
            "sample_id": sample_id,
            "expected_interest": expected_interest,
            "actual_interest": actual_interest,
            "s2": s2,
            "s3": s3,
            "r1_interest_reason": r1_interest_reason
        })

    # Print summary
    print("\n=== Interest Debug Summary ===")
    for r in results:
        print(f"\n{r['sample_id']}:")
        print(f"  expected_interest: {r['expected_interest']}")
        print(f"  actual_interest: {r['actual_interest']}")
        print(f"  r1_interest_reason: {r['r1_interest_reason']}")
        if r['s2']:
            print(f"  s2: {json.dumps(r['s2'], ensure_ascii=False, indent=2)}")
        if r['s3']:
            print(f"  s3: {json.dumps(r['s3'], ensure_ascii=False, indent=2)}")

    # Save to file
    with open("interest_debug_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\nSaved to interest_debug_summary.json")

if __name__ == "__main__":
    main()
