#!/usr/bin/env python3
"""
测试debug输出增强功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.pipeline_orchestrator import run_analysis

def test_debug_output():
    # 使用B1样本
    chat_text = "A：今天怎么不找我\nB：在想你啊\nA：真的假的\nB：骗你干嘛\nA：那你想我什么\nB：想见你"
    user_question = "他对我有兴趣吗？"

    print("测试debug输出增强...")
    print(f"chat_text: {chat_text}")
    print(f"user_question: {user_question}")
    print(f"provider_name: mock")

    # 使用mock provider测试debug=True
    result = run_analysis(chat_text, user_question, provider_name="mock", debug=True)
    print("\n=== 完整结果 ===")
    for key, value in result.items():
        if key != 'debug':
            print(f"  {key}: {value}")

    print("\n=== Debug信息 ===")
    if 'debug' in result:
        debug_info = result['debug']
        print(f"Debug字段: {list(debug_info.keys())}")

        # 检查是否有新增的字段
        expected_fields = ['s2_raw_response', 's2_parsed', 's3_raw_response', 's3_parsed', 'r1_input', 'r1_output', 's2', 's3', 'r1', 's5_raw', 's5_final']
        for field in expected_fields:
            if field in debug_info:
                print(f"  ✓ {field}: 存在")
                if field in ['s2_raw_response', 's3_raw_response']:
                    print(f"    值: {debug_info[field]}")
                elif field in ['s2_parsed', 's3_parsed', 'r1_input', 'r1_output']:
                    print(f"    值: {debug_info[field]}")
            else:
                print(f"  ✗ {field}: 缺失")
    else:
        print("错误: 未找到debug字段")

    # 检查结果是否非兜底
    print("\n=== 结果分析 ===")
    if result.get("relationship_stage") == "无法判断":
        print(f"⚠️  警告: relationship_stage 仍然是'无法判断' (兜底结果)")
    else:
        print(f"✅ 成功: relationship_stage = {result['relationship_stage']} (非兜底结果)")

    if result.get("interest_level") == "无法判断":
        print(f"⚠️  警告: interest_level 仍然是'无法判断'")
    else:
        print(f"✅ 成功: interest_level = {result['interest_level']}")

    return result

if __name__ == "__main__":
    test_debug_output()