# -*- coding: utf-8 -*-
"""
LoveAdvisor V2.5 - metrics_report.py

作用：
1. 读取 batch_test.py 产出的 test_results.json
2. 自动计算核心指标
3. 自动做基础错误分类
4. 输出 metrics_report.json
5. 可选输出 metrics_report.csv（按 group 统计）

建议目录：
test_system/
├── output/
│   ├── test_results.json
│   ├── metrics_report.json
│   └── metrics_report.csv
└── scripts/
    └── metrics_report.py
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# =========================
# 路径配置
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "output"

DEFAULT_RESULTS_PATH = OUTPUT_DIR / "test_results.json"
DEFAULT_METRICS_JSON_PATH = OUTPUT_DIR / "metrics_report.json"
DEFAULT_METRICS_CSV_PATH = OUTPUT_DIR / "metrics_report.csv"

# =========================
# 常量配置
# =========================
INTEREST_ORDER = {
    "无法判断": -1,
    "低": 0,
    "中": 1,
    "高": 2,
}

VALID_GROUPS = ["A", "B", "C", "D", "E"]


# =========================
# 工具函数
# =========================
def safe_load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_dump_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if value in {"true", "1", "yes", "y", "是"}:
            return True
        if value in {"false", "0", "no", "n", "否"}:
            return False
    return default


def interest_rank(value: Optional[str]) -> int:
    if value is None:
        return -999
    return INTEREST_ORDER.get(str(value).strip(), -999)


def calc_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def normalize_case(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    兼容不同 test_results.json 字段写法。
    你后续如果 batch_test.py 字段稍有变化，这里改一次即可。
    """
    expected_stage = case.get("expected_stage") or case.get("expected_relationship_stage") or ""
    actual_stage = case.get("actual_stage") or case.get("relationship_stage") or ""

    expected_interest = case.get("expected_interest") or case.get("expected_interest_level") or ""
    actual_interest = case.get("actual_interest") or case.get("interest_level") or ""

    # 优先使用现成字段，没有再自动计算
    stage_correct = case.get("stage_correct")
    if stage_correct is None:
        stage_correct = (expected_stage == actual_stage)

    interest_correct = case.get("interest_correct")
    if interest_correct is None:
        interest_correct = (expected_interest == actual_interest)

    r1_correct = case.get("r1_correct")
    if r1_correct is None:
        r1_correct = bool(stage_correct and interest_correct)

    suggestion_aligned = case.get("suggestion_aligned", False)
    next_step_conservative = (
        case.get("next_step_conservative")
        if "next_step_conservative" in case
        else case.get("next_step_ok", False)
    )
    full_chain_pass = case.get("full_chain_pass")
    if full_chain_pass is None:
        full_chain_pass = bool(r1_correct and suggestion_aligned and next_step_conservative)

    normalized = {
        "sample_id": str(case.get("sample_id", "")).strip(),
        "group": str(case.get("group", "")).strip().upper(),
        "expected_stage": str(expected_stage).strip(),
        "actual_stage": str(actual_stage).strip(),
        "expected_interest": str(expected_interest).strip(),
        "actual_interest": str(actual_interest).strip(),
        "stage_correct": safe_bool(stage_correct),
        "interest_correct": safe_bool(interest_correct),
        "r1_correct": safe_bool(r1_correct),
        "suggestion_aligned": safe_bool(suggestion_aligned),
        "next_step_conservative": safe_bool(next_step_conservative),
        "full_chain_pass": safe_bool(full_chain_pass),
        "issue_type": case.get("issue_type"),
        "notes": case.get("notes", ""),
        "raw_output": case.get("raw_output"),
    }
    return normalized


# =========================
# 错误分类
# =========================
def classify_issue(case: Dict[str, Any]) -> str:
    """
    基础错误分类逻辑。
    当前优先支持：
    - 边界失守
    - 误判初识
    - interest_level低估
    - interest_level高估
    - suggestion漂移
    - next_step不克制
    - pass
    """

    expected_stage = case["expected_stage"]
    actual_stage = case["actual_stage"]
    expected_interest = case["expected_interest"]
    actual_interest = case["actual_interest"]

    # 1. 先抓最关键边界问题：无法判断被吸入其他阶段
    if expected_stage == "无法判断" and actual_stage != "无法判断":
        if actual_stage == "初识期":
            return "误判初识"
        return "边界失守"

    # 2. R1 错误中的 interest_level 漂移
    if case["stage_correct"] and not case["interest_correct"]:
        actual_rank = interest_rank(actual_interest)
        expected_rank = interest_rank(expected_interest)

        if actual_rank < expected_rank:
            return "interest_level低估"
        if actual_rank > expected_rank:
            return "interest_level高估"

    # 3. stage误判：阶段本身错了，但又不是 E 类边界失守
    if not case["stage_correct"]:
        return "stage误判"

    # 4. suggestion漂移：规则不对齐
    if not case["suggestion_aligned"]:
        return "suggestion漂移"

    # 5. 最后一步不克制
    if not case["next_step_conservative"]:
        return "next_step不克制"

    return "pass"


# =========================
# 分组统计
# =========================
def build_group_stats(cases: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for case in cases:
        grouped[case["group"]].append(case)

    group_stats: Dict[str, Dict[str, Any]] = {}

    for group_name in VALID_GROUPS:
        items = grouped.get(group_name, [])
        total = len(items)

        stage_correct_count = sum(1 for x in items if x["stage_correct"])
        r1_correct_count = sum(1 for x in items if x["r1_correct"])
        suggestion_aligned_count = sum(1 for x in items if x["suggestion_aligned"])
        next_step_ok_count = sum(1 for x in items if x["next_step_conservative"])
        full_pass_count = sum(1 for x in items if x["full_chain_pass"])

        group_stats[group_name] = {
            "count": total,
            "stage_accuracy": calc_rate(stage_correct_count, total),
            "r1_strict_accuracy": calc_rate(r1_correct_count, total),
            "suggestion_alignment_rate": calc_rate(suggestion_aligned_count, total),
            "next_step_conservative_rate": calc_rate(next_step_ok_count, total),
            "full_chain_pass_rate": calc_rate(full_pass_count, total),
        }

    return group_stats


# =========================
# 核心统计函数
# =========================
def generate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(results, list):
        raise ValueError("results 必须是 list[dict] 格式。")

    normalized_cases = [normalize_case(case) for case in results]

    # 自动补 issue_type
    for case in normalized_cases:
        if not case.get("issue_type"):
            case["issue_type"] = classify_issue(case)

    total_cases = len(normalized_cases)

    stage_correct_count = sum(1 for x in normalized_cases if x["stage_correct"])
    r1_correct_count = sum(1 for x in normalized_cases if x["r1_correct"])
    suggestion_aligned_count = sum(1 for x in normalized_cases if x["suggestion_aligned"])
    next_step_ok_count = sum(1 for x in normalized_cases if x["next_step_conservative"])
    full_pass_count = sum(1 for x in normalized_cases if x["full_chain_pass"])

    issue_counter = Counter(
        case["issue_type"]
        for case in normalized_cases
        if case["issue_type"] and case["issue_type"] != "pass"
    )

    metrics = {
        "total_cases": total_cases,
        "stage_accuracy": calc_rate(stage_correct_count, total_cases),
        "r1_strict_accuracy": calc_rate(r1_correct_count, total_cases),
        "suggestion_alignment_rate": calc_rate(suggestion_aligned_count, total_cases),
        "next_step_conservative_rate": calc_rate(next_step_ok_count, total_cases),
        "full_chain_pass_rate": calc_rate(full_pass_count, total_cases),
        "issue_breakdown": dict(issue_counter),
        "group_stats": build_group_stats(normalized_cases),
        "cases": normalized_cases,  # 方便你后续直接审查
    }
    return metrics


# =========================
# CSV 输出
# =========================
def write_group_stats_csv(metrics: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "group",
        "count",
        "stage_accuracy",
        "r1_strict_accuracy",
        "suggestion_alignment_rate",
        "next_step_conservative_rate",
        "full_chain_pass_rate",
    ]

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for group_name, stats in metrics.get("group_stats", {}).items():
            row = {"group": group_name, **stats}
            writer.writerow(row)


# =========================
# 主流程
# =========================
def main(
    results_path: Path = DEFAULT_RESULTS_PATH,
    metrics_json_path: Path = DEFAULT_METRICS_JSON_PATH,
    metrics_csv_path: Path = DEFAULT_METRICS_CSV_PATH,
) -> None:
    results = safe_load_json(results_path)
    metrics = generate_metrics(results)

    safe_dump_json(metrics, metrics_json_path)
    write_group_stats_csv(metrics, metrics_csv_path)

    print("✅ metrics_report 生成完成")
    print(f"results_path      : {results_path}")
    print(f"metrics_json_path : {metrics_json_path}")
    print(f"metrics_csv_path  : {metrics_csv_path}")
    print()
    print("=== CORE METRICS ===")
    print(f"total_cases                : {metrics['total_cases']}")
    print(f"stage_accuracy             : {metrics['stage_accuracy']}")
    print(f"r1_strict_accuracy         : {metrics['r1_strict_accuracy']}")
    print(f"suggestion_alignment_rate  : {metrics['suggestion_alignment_rate']}")
    print(f"next_step_conservative_rate: {metrics['next_step_conservative_rate']}")
    print(f"full_chain_pass_rate       : {metrics['full_chain_pass_rate']}")
    print(f"issue_breakdown            : {metrics['issue_breakdown']}")


if __name__ == "__main__":
    main()