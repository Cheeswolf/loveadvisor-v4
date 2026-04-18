import csv
import json
import os
import sys
import time
from typing import Any, Dict, List, Tuple

import requests


# =========================
# 配置区
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "test_cases.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
RESULT_JSON_PATH = os.path.join(OUTPUT_DIR, "test_results.json")
RESULT_CSV_PATH = os.path.join(OUTPUT_DIR, "test_results.csv")
METRICS_JSON_PATH = os.path.join(OUTPUT_DIR, "metrics_report.json")

API_URL = "http://127.0.0.1:8000/api/v1/analyze"
REQUEST_TIMEOUT = 120
RETRY_TIMES = 2
RETRY_SLEEP_SECONDS = 1.5
PROVIDER_NAME = "deepseek"  # 使用真实 DeepSeek provider，不再默认 mock


# =========================
# 通用工具
# =========================
def ensure_output_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def safe_get(d: Any, *keys: str, default=None):
    cur = d
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def safe_str(v: Any, default: str = "") -> str:
    if v is None:
        return default
    if isinstance(v, str):
        return v.strip()
    return str(v).strip()


def safe_list(v: Any) -> List[Any]:
    if isinstance(v, list):
        return v
    return []


def load_test_cases(path: str) -> List[Dict[str, Any]]:
    # 检测文件编码并确保UTF-8
    try:
        # 首先尝试用UTF-8读取
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # 尝试解析JSON以验证编码正确
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except UnicodeDecodeError:
        # 如果UTF-8失败，尝试GBK（常见中文编码）
        print(f"[WARN] 文件 {path} 不是UTF-8编码，尝试GBK编码...")
        try:
            with open(path, "r", encoding="gbk") as f:
                content = f.read()
            # 将内容转换为UTF-8并写回文件
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[INFO] 已将 {path} 转换为UTF-8编码")
            # 重新用UTF-8读取
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"无法读取或转换文件编码: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON解析错误: {e}")

    if not isinstance(data, list):
        raise ValueError("test_cases.json 顶层必须是 list")
    return data


# =========================
# 请求 /analyze
# =========================
def call_analyze_api(input_text: str, debug: bool = False) -> Tuple[bool, Dict[str, Any], str, float]:
    # V3 API 期望 chat_text 和 user_question 字段
    payload = {"chat_text": input_text, "user_question": "", "provider_name": PROVIDER_NAME, "debug": debug}
    # 添加debug字段以获取后端调试信息

    last_error = ""
    start = time.time()

    for attempt in range(RETRY_TIMES + 1):
        try:
            resp = requests.post(API_URL, json=payload, timeout=REQUEST_TIMEOUT)
            elapsed = time.time() - start
            resp.raise_for_status()
            data = resp.json()
            return True, data, "", elapsed
        except Exception as e:
            last_error = str(e)
            if attempt < RETRY_TIMES:
                time.sleep(RETRY_SLEEP_SECONDS)
            else:
                elapsed = time.time() - start
                return False, {}, last_error, elapsed

    return False, {}, last_error, time.time() - start


# =========================
# 结果提取
# 适配 V3 输出结构，兼容两种常见返回：
# 1) 直接返回最终字段（V3标准输出）
# 2) 返回 O1_output / final_output / result 这类包装层
# V3 输出字段：
# - relationship_stage, interest_level, psychological_analysis
# - risk_points[], suggestions[], next_step
# - key_signals[], signal_summary[]（可能包含）
# =========================
def unwrap_final_output(raw: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        return {}

    # 最常见：后端直接返回最终结果
    if raw.get("relationship_stage") is not None:
        return raw

    # 尝试从常见包装字段中提取
    for key in ["final_output", "O1_output", "result", "data", "output"]:
        obj = raw.get(key)
        if isinstance(obj, dict) and obj.get("relationship_stage") is not None:
            return obj

    return raw


def extract_fields(raw_response: Dict[str, Any]) -> Dict[str, Any]:
    final_output = unwrap_final_output(raw_response)

    relationship_stage = safe_str(final_output.get("relationship_stage"), "无法判断")
    interest_level = safe_str(final_output.get("interest_level"), "无法判断")
    suggestions = safe_list(final_output.get("suggestions"))
    risk_points = safe_list(final_output.get("risk_points"))
    key_signals = safe_list(final_output.get("key_signals"))
    signal_summary = safe_list(final_output.get("signal_summary"))
    next_step = safe_str(final_output.get("next_step"), "无法判断")
    psychological_analysis = safe_str(final_output.get("psychological_analysis"), "")

    return {
        "relationship_stage": relationship_stage,
        "interest_level": interest_level,
        "suggestions": suggestions,
        "risk_points": risk_points,
        "key_signals": key_signals,
        "signal_summary": signal_summary,
        "next_step": next_step,
        "psychological_analysis": psychological_analysis,
    }


# =========================
# 自动评测逻辑
# 说明：
# - suggestion_aligned 和 next_step_conservative 目前是“启发式评测”
# - 先解决机械批测问题，后续再升级语义判断
# =========================
def evaluate_r1_correct(
    expected_stage: str,
    actual_stage: str,
    expected_interest: str,
    actual_interest: str
) -> bool:
    return expected_stage == actual_stage and expected_interest == actual_interest


def evaluate_stage_correct(expected_stage: str, actual_stage: str) -> bool:
    return expected_stage == actual_stage


def evaluate_suggestion_aligned(stage: str, suggestions: List[Any], next_step: str) -> bool:
    """
    启发式判断 S5 是否服从 R1。
    规则尽量保守，只做“明显错位”识别。
    """
    text = " ".join([safe_str(x) for x in suggestions]) + " " + safe_str(next_step)

    if stage == "无法判断":
        aggressive_words = ["表白", "约会", "送礼", "直接问清楚", "摊牌", "升级关系"]
        return not any(w in text for w in aggressive_words)

    if stage == "初识期":
        aggressive_words = ["表白", "摊牌", "确定关系", "强推进", "送礼物", "制造暧昧"]
        return not any(w in text for w in aggressive_words)

    if stage == "暧昧期":
        aggressive_words = ["立刻表白", "马上确定关系", "强势推进", "逼问关系"]
        return not any(w in text for w in aggressive_words)

    if stage == "拉扯期":
        aggressive_words = ["继续追问", "逼对方回应", "摊牌", "要求明确态度"]
        return not any(w in text for w in aggressive_words)

    if stage == "冷淡期":
        aggressive_words = ["继续主动", "持续联系", "频繁找他", "加码投入", "追着聊"]
        return not any(w in text for w in aggressive_words)

    return True


def evaluate_next_step_conservative(stage: str, next_step: str) -> bool:
    """
    启发式判断 next_step 是否克制。
    """
    text = safe_str(next_step)

    if not text:
        return False

    aggressive_words = [
        "表白", "摊牌", "直接问", "立刻约", "马上约", "送礼",
        "频繁联系", "持续主动", "加大投入", "升级关系", "逼问"
    ]

    if stage == "无法判断":
        return not any(w in text for w in aggressive_words) and (
            "观察" in text or "不加码" in text or "先别推进" in text or "暂时观察" in text
        )

    if stage == "初识期":
        return not any(w in text for w in aggressive_words)

    if stage == "暧昧期":
        return not any(w in text for w in ["立刻表白", "马上确定关系", "逼问", "摊牌"])

    if stage == "拉扯期":
        return not any(w in text for w in ["继续追问", "逼问", "摊牌", "强推进"])

    if stage == "冷淡期":
        return not any(w in text for w in ["继续主动", "频繁联系", "加码投入", "追着聊"])

    return True


def classify_issue(
    expected_stage: str,
    actual_stage: str,
    expected_interest: str,
    actual_interest: str,
    suggestion_aligned: bool,
    next_step_conservative: bool
) -> str:
    issues = []
    # 系统兜底输出检测
    if actual_stage == "无法判断" and actual_interest == "无法判断":
        issues.append("系统兜底输出")

    if expected_stage == "无法判断" and actual_stage != "无法判断":
        issues.append("边界失守")
        if actual_stage == "初识期":
            issues.append("误判初识")

    order = {
        "低": 0,
        "中": 1,
        "高": 2
    }

    if expected_interest == "无法判断" or actual_interest == "无法判断":
        pass
    else:
        if actual_interest in order and expected_interest in order:
            if order[actual_interest] < order[expected_interest]:
                issues.append("interest_level低估")
            elif order[actual_interest] > order[expected_interest]:
                issues.append("interest_level高估")

    if not suggestion_aligned:
        issues.append("suggestion漂移")

    if not next_step_conservative:
        issues.append("next_step不克制")

    if not issues and (expected_stage != actual_stage):
        issues.append("stage误判")

    return "；".join(issues) if issues else "-"


# =========================
# 单条样本评测
# =========================
def run_single_case(case: Dict[str, Any]) -> Dict[str, Any]:
    sample_id = safe_str(case.get("sample_id"))
    group = safe_str(case.get("group"))
    input_text = safe_str(case.get("input_text"))
    expected_stage = safe_str(case.get("expected_relationship_stage"), "无法判断")
    expected_interest = safe_str(case.get("expected_interest_level"), "无法判断")
    notes = safe_str(case.get("notes"))

    # 临时调试：A1样本发送前检查
    if sample_id == "A1":
        print(f"[DEBUG] A1 sample_id: {sample_id}")
        print(f"[DEBUG] repr(input_text): {repr(input_text)}")
        # 构造payload用于调试
        debug_payload = {"chat_text": input_text, "user_question": "", "provider_name": PROVIDER_NAME}
        print(f"[DEBUG] repr(payload['chat_text']): {repr(debug_payload['chat_text'])}")

    # 对C1、C3、E2、E3样本启用debug以获取完整调试信息
    debug_samples = {"C1", "C3", "E2", "E3"}
    debug_flag = sample_id in debug_samples
    ok, raw_response, error_msg, elapsed = call_analyze_api(input_text, debug=debug_flag)

    if ok:
        extracted = extract_fields(raw_response)
        actual_stage = extracted["relationship_stage"]
        actual_interest = extracted["interest_level"]
        suggestions = extracted["suggestions"]
        next_step = extracted["next_step"]

        stage_correct = evaluate_stage_correct(expected_stage, actual_stage)
        r1_correct = evaluate_r1_correct(
            expected_stage, actual_stage, expected_interest, actual_interest
        )
        suggestion_aligned = evaluate_suggestion_aligned(actual_stage, suggestions, next_step)
        next_step_conservative = evaluate_next_step_conservative(actual_stage, next_step)
        full_chain_pass = r1_correct and suggestion_aligned and next_step_conservative
        issue_type = classify_issue(
            expected_stage,
            actual_stage,
            expected_interest,
            actual_interest,
            suggestion_aligned,
            next_step_conservative
        )

        return {
            "sample_id": sample_id,
            "group": group,
            "expected_stage": expected_stage,
            "actual_stage": actual_stage,
            "expected_interest": expected_interest,
            "actual_interest": actual_interest,
            "stage_correct": stage_correct,
            "r1_correct": r1_correct,
            "suggestion_aligned": suggestion_aligned,
            "next_step_conservative": next_step_conservative,
            "full_chain_pass": full_chain_pass,
            "issue_type": issue_type,
            "elapsed_seconds": round(elapsed, 3),
            "error": "",
            "notes": notes,
            "raw_output": raw_response
        }

    return {
        "sample_id": sample_id,
        "group": group,
        "expected_stage": expected_stage,
        "actual_stage": "请求失败",
        "expected_interest": expected_interest,
        "actual_interest": "请求失败",
        "stage_correct": False,
        "r1_correct": False,
        "suggestion_aligned": False,
        "next_step_conservative": False,
        "full_chain_pass": False,
        "issue_type": "接口异常",
        "elapsed_seconds": round(elapsed, 3),
        "error": error_msg,
        "notes": notes,
        "raw_output": {}
    }


# =========================
# 指标统计
# =========================
def compute_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    if total == 0:
        return {}

    stage_correct_cnt = sum(1 for x in results if x["stage_correct"])
    r1_correct_cnt = sum(1 for x in results if x["r1_correct"])
    suggestion_aligned_cnt = sum(1 for x in results if x["suggestion_aligned"])
    next_step_conservative_cnt = sum(1 for x in results if x["next_step_conservative"])
    full_chain_pass_cnt = sum(1 for x in results if x["full_chain_pass"])

    issue_counter: Dict[str, int] = {}
    for x in results:
        issue_text = safe_str(x.get("issue_type"), "-")
        if issue_text == "-" or not issue_text:
            continue
        for issue in issue_text.split("；"):
            issue = issue.strip()
            if not issue:
                continue
            issue_counter[issue] = issue_counter.get(issue, 0) + 1

    group_stats: Dict[str, Dict[str, Any]] = {}
    all_groups = sorted(set(safe_str(x["group"]) for x in results if safe_str(x["group"])))
    for group in all_groups:
        group_items = [x for x in results if x["group"] == group]
        n = len(group_items)
        if n == 0:
            continue
        group_stats[group] = {
            "count": n,
            "stage_accuracy": round(sum(1 for x in group_items if x["stage_correct"]) / n, 4),
            "r1_strict_accuracy": round(sum(1 for x in group_items if x["r1_correct"]) / n, 4),
            "suggestion_alignment_rate": round(sum(1 for x in group_items if x["suggestion_aligned"]) / n, 4),
            "next_step_conservative_rate": round(sum(1 for x in group_items if x["next_step_conservative"]) / n, 4),
            "full_chain_pass_rate": round(sum(1 for x in group_items if x["full_chain_pass"]) / n, 4),
        }

    return {
        "total_cases": total,
        "stage_accuracy": round(stage_correct_cnt / total, 4),
        "r1_strict_accuracy": round(r1_correct_cnt / total, 4),
        "suggestion_alignment_rate": round(suggestion_aligned_cnt / total, 4),
        "next_step_conservative_rate": round(next_step_conservative_cnt / total, 4),
        "full_chain_pass_rate": round(full_chain_pass_cnt / total, 4),
        "issue_breakdown": issue_counter,
        "group_stats": group_stats
    }


# =========================
# 文件写出
# =========================
def save_json(path: str, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def save_csv(path: str, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return

    fieldnames = [
        "sample_id",
        "group",
        "expected_stage",
        "actual_stage",
        "expected_interest",
        "actual_interest",
        "stage_correct",
        "r1_correct",
        "suggestion_aligned",
        "next_step_conservative",
        "full_chain_pass",
        "issue_type",
        "elapsed_seconds",
        "error",
        "notes",
        "raw_output",
    ]

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row_copy = dict(row)
            row_copy["raw_output"] = json.dumps(row_copy.get("raw_output", {}), ensure_ascii=False)
            writer.writerow(row_copy)


# =========================
# 主流程
# =========================
def main():
    ensure_output_dir()

    try:
        cases = load_test_cases(DATA_PATH)
    except Exception as e:
        print(f"[ERROR] 读取测试集失败: {e}")
        sys.exit(1)

    print("=== LoveAdvisor V3 Batch Test ===")
    print(f"API_URL    : {API_URL}")
    print(f"CASE_COUNT : {len(cases)}")
    print("")

    results: List[Dict[str, Any]] = []

    for idx, case in enumerate(cases, start=1):
        sample_id = safe_str(case.get("sample_id"))
        print(f"[{idx}/{len(cases)}] Running {sample_id} ...")

        result = run_single_case(case)
        results.append(result)

        print(
            f"  expected = {result['expected_stage']} / {result['expected_interest']}\n"
            f"  actual   = {result['actual_stage']} / {result['actual_interest']}\n"
            f"  r1       = {result['r1_correct']}\n"
            f"  suggest  = {result['suggestion_aligned']}\n"
            f"  nextstep = {result['next_step_conservative']}\n"
            f"  issue    = {result['issue_type']}\n"
        )

    metrics = compute_metrics(results)

    save_json(RESULT_JSON_PATH, results)
    save_csv(RESULT_CSV_PATH, results)
    save_json(METRICS_JSON_PATH, metrics)

    print("=== DONE ===")
    print(f"Saved results : {RESULT_JSON_PATH}")
    print(f"Saved csv     : {RESULT_CSV_PATH}")
    print(f"Saved metrics : {METRICS_JSON_PATH}")
    print("")
    print("=== METRICS ===")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()