#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
sys.path.insert(0, '.')

from app.rules.rules import infer_r1_with_debug, _initial_medium_signal

def load_test_cases():
    with open('test_system/data/test_cases.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_debug_data():
    """从各种文件提取S2/S3 debug数据"""
    debug_map = {}

    # 从a2_a3_debug_output.json加载A2/A3
    try:
        with open('test_system/output/a2_a3_debug_output.json', 'r', encoding='utf-8') as f:
            a2a3 = json.load(f)
        for sample_id in ['A2', 'A3']:
            debug = a2a3[sample_id]['debug']
            debug_map[sample_id] = {
                's2': debug['r1_input']['s2'],
                's3': debug['r1_input']['s3']
            }
    except Exception as e:
        print(f"Warning: Could not load a2_a3_debug_output.json: {e}")

    # 从test_results.json加载其他样本的debug数据
    try:
        with open('test_system/output/test_results.json', 'r', encoding='utf-8') as f:
            results = json.load(f)
        for result in results:
            sample_id = result['sample_id']
            if 'debug' in result.get('raw_output', {}) and result['raw_output']['debug']:
                debug = result['raw_output']['debug']
                if 'r1_input' in debug:
                    debug_map[sample_id] = {
                        's2': debug['r1_input']['s2'],
                        's3': debug['r1_input']['s3']
                    }
    except Exception as e:
        print(f"Warning: Could not extract from test_results.json: {e}")

    return debug_map

def main():
    test_cases = load_test_cases()
    debug_data = extract_debug_data()

    print("=== 弱互动补偿分支验证报告 ===\n")

    # 统计信息
    total_cases = len(test_cases)
    has_debug = len(debug_data)
    print(f"总样本数: {total_cases}")
    print(f"有S2/S3数据的样本数: {has_debug}")
    print(f"缺失数据的样本: {[c['sample_id'] for c in test_cases if c['sample_id'] not in debug_data]}\n")

    # 分析每个有数据的样本
    compensation_triggered = []
    false_positives = []
    false_negatives = []

    for case in test_cases:
        sample_id = case['sample_id']
        if sample_id not in debug_data:
            continue

        s2 = debug_data[sample_id]['s2']
        s3 = debug_data[sample_id]['s3']

        # 检查补偿分支条件
        weak_interaction = (s2.get('response_length') == '短' and s2.get('interaction_reciprocity') == '弱承接')
        has_pos_recip = s3.get('has_positive_reciprocity', False)

        # 负向信号
        has_negative = (
            s3.get('has_rejection_signal', False) or
            s2.get('emotional_tone') == '冷' or
            s2.get('interaction_reciprocity') == '明显回避' or
            s3.get('has_sustained_coldness', False)
        )

        # 计算score
        score = 0
        if s3.get('has_relationship_probe', False):
            score += 1
        if has_pos_recip:
            score += 2
        if s2.get('emotional_tone') == '热':
            score += 1
        if s2.get('topic_depth') in ['中', '深']:
            score += 1
        if s2.get('interaction_reciprocity') == '正向承接':
            score += 1

        # 补偿分支是否触发
        compensation_eligible = (weak_interaction and has_pos_recip and not has_negative and score >= 2)

        # 实际R1结果
        r1_result = infer_r1_with_debug(s2, s3)
        actual_interest = r1_result['interest_level']
        expected_interest = case['expected_interest_level']

        # 检查误判
        if compensation_eligible:
            compensation_triggered.append(sample_id)
            # 如果补偿分支触发，期望兴趣等级应为中（初识期）
            # 但需要考虑关系阶段
            relationship_stage = r1_result['relationship_stage']
            if relationship_stage == '初识期':
                if actual_interest != '中':
                    false_negatives.append(sample_id)

        print(f"样本 {sample_id}:")
        print(f"  预期兴趣: {expected_interest}, 实际兴趣: {actual_interest}")
        print(f"  关系阶段: {r1_result['relationship_stage']}")
        print(f"  弱互动: {weak_interaction}, 正向承接: {has_pos_recip}, 负向信号: {has_negative}, 得分: {score}")
        print(f"  补偿分支条件满足: {compensation_eligible}")
        print(f"  补偿分支触发: {compensation_eligible and r1_result['relationship_stage'] == '初识期'}")
        print()

    print("\n=== 分析总结 ===")
    print(f"补偿分支条件满足的样本: {compensation_triggered}")
    print(f"补偿分支应触发但兴趣等级为低的样本（假阴性）: {false_negatives}")
    print(f"补偿分支误触发（不应为中但被抬高）的样本: {false_positives}")

    # A组专门分析
    print("\n=== A组样本详细分析 ===")
    for sample_id in ['A1', 'A2', 'A3']:
        if sample_id in debug_data:
            s2 = debug_data[sample_id]['s2']
            s3 = debug_data[sample_id]['s3']
            r1_result = infer_r1_with_debug(s2, s3)
            print(f"{sample_id}:")
            print(f"  关系阶段: {r1_result['relationship_stage']}")
            print(f"  兴趣等级: {r1_result['interest_level']}")
            print(f"  原因: {r1_result['r1_interest_reason']}")
            # 手动调用_initial_medium_signal
            medium_result = _initial_medium_signal(s2, s3)
            print(f"  _initial_medium_signal结果: {medium_result}")
            print()
        else:
            print(f"{sample_id}: 无S2/S3数据")

    # 检查所有has_positive_reciprocity=true的样本
    print("\n=== 所有has_positive_reciprocity=true的样本 ===")
    pos_recip_samples = []
    for sample_id, data in debug_data.items():
        if data['s3'].get('has_positive_reciprocity', False):
            pos_recip_samples.append(sample_id)

    for sample_id in pos_recip_samples:
        s2 = debug_data[sample_id]['s2']
        s3 = debug_data[sample_id]['s3']
        weak = (s2.get('response_length') == '短' and s2.get('interaction_reciprocity') == '弱承接')
        r1_result = infer_r1_with_debug(s2, s3)
        print(f"{sample_id}: 弱互动={weak}, 兴趣等级={r1_result['interest_level']}, 阶段={r1_result['relationship_stage']}")

if __name__ == "__main__":
    main()