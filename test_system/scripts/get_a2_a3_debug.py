# test_system/scripts/get_a2_a3_debug.py
# -*- coding: utf-8 -*-
"""
最小脚本：获取A2/A3的S2/S3调试输出。
调用API并启用debug模式。
"""

import json
import sys
import time
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "test_system" / "data" / "test_cases.json"
API_URL = "http://127.0.0.1:8000/api/v1/analyze"
REQUEST_TIMEOUT = 120
PROVIDER_NAME = "deepseek"

def load_test_cases():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def call_analyze_with_debug(input_text):
    """调用API并启用debug模式"""
    payload = {
        "chat_text": input_text,
        "user_question": "",
        "provider_name": PROVIDER_NAME,
        "debug": True  # 启用debug模式
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API调用失败: {e}")
        return None

def extract_debug_info(result):
    """从结果中提取debug信息"""
    if not result:
        return None

    if result.get("status") != "success":
        print(f"API返回错误: {result.get('error_message')}")
        return None

    result_data = result.get("result", {})
    debug_info = result_data.get("debug")

    if not debug_info:
        print("警告: 结果中没有debug信息")
        return None

    return debug_info

def main():
    """主函数"""
    # 检查API是否可用
    try:
        requests.get("http://127.0.0.1:8000/docs", timeout=5)
        print("API服务似乎正在运行")
    except:
        print("警告: API服务可能没有运行")
        print("请先启动API服务: python run.py 或 uvicorn app.main:app --reload")
        print("继续执行，但可能会失败...")

    cases = load_test_cases()
    target_ids = {"A2", "A3"}

    results = {}
    for case in cases:
        sample_id = case.get("sample_id")
        if sample_id not in target_ids:
            continue

        print(f"\n{'='*60}")
        print(f"处理样本: {sample_id}")
        print(f"{'='*60}")

        input_text = case.get("input_text", "")
        print(f"输入文本: {input_text}")

        result = call_analyze_with_debug(input_text)
        if result:
            debug_info = extract_debug_info(result)
            if debug_info:
                results[sample_id] = {
                    "input_text": input_text,
                    "debug": debug_info
                }
                print(f"成功获取debug信息")

                # 打印关键信息
                if "s2" in debug_info:
                    s2 = debug_info["s2"]
                    print(f"S2输出:")
                    print(f"  主动性: {s2.get('initiative')}")
                    print(f"  回应长度: {s2.get('response_length')}")
                    print(f"  情感基调: {s2.get('emotional_tone')}")
                    print(f"  话题深度: {s2.get('topic_depth')}")
                    print(f"  互动承接性: {s2.get('interaction_reciprocity')}")
                    print(f"  关键信号: {s2.get('key_signals', [])}")

                if "s3" in debug_info:
                    s3 = debug_info["s3"]
                    print(f"S3输出:")
                    print(f"  亲密信号: {s3.get('has_intimacy_signal')}")
                    print(f"  关系试探: {s3.get('has_relationship_probe')}")
                    print(f"  正向承接: {s3.get('has_positive_reciprocity')}")
                    print(f"  拒绝信号: {s3.get('has_rejection_signal')}")
                    print(f"  推拉模式: {s3.get('has_push_pull_pattern')}")
                    print(f"  持续冷淡: {s3.get('has_sustained_coldness')}")
                    print(f"  信号摘要: {s3.get('signal_summary', [])}")

                if "r1_output" in debug_info:
                    r1 = debug_info["r1_output"]
                    print(f"R1输出:")
                    print(f"  关系阶段: {r1.get('relationship_stage')}")
                    print(f"  兴趣等级: {r1.get('interest_level')}")
                    print(f"  阶段原因: {r1.get('r1_stage_reason')}")
                    print(f"  兴趣原因: {r1.get('r1_interest_reason')}")
            else:
                print(f"警告: 没有debug信息")
        else:
            print(f"错误: API调用失败")

        # 短暂延迟避免过快请求
        time.sleep(1)

    # 保存结果
    if results:
        output_file = PROJECT_ROOT / "test_system" / "output" / "a2_a3_debug_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {output_file}")

        # 打印汇总
        print(f"\n{'='*60}")
        print("A2/A3 调试输出汇总")
        print(f"{'='*60}")
        for sample_id, data in results.items():
            print(f"\n{sample_id}:")
            debug_info = data["debug"]
            if "s2" in debug_info and "s3" in debug_info:
                s2 = debug_info["s2"]
                s3 = debug_info["s3"]
                print(f"  S2: {s2.get('initiative')}, {s2.get('response_length')}, {s2.get('emotional_tone')}, {s2.get('topic_depth')}, {s2.get('interaction_reciprocity')}")
                print(f"  S3: 关系试探={s3.get('has_relationship_probe')}, 正向承接={s3.get('has_positive_reciprocity')}")
    else:
        print("\n没有获取到任何结果")

if __name__ == "__main__":
    main()