#!/usr/bin/env python3
"""
最小测试脚本，用于验证修复后的 /api/v1/analyze 是否返回非兜底结果。
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.pipeline_orchestrator import run_analysis

def test_minimal():
    chat_text = "A: 你好，今天天气不错。\nB: 是啊，适合出去走走。\nA: 你有空的话可以一起散步。\nB: 好啊，下午三点可以吗？"
    user_question = "他对我有兴趣吗？"

    print("测试最小输入...")
    print(f"chat_text: {chat_text}")
    print(f"user_question: {user_question}")

    # 使用默认 provider (mock)
    result = run_analysis(chat_text, user_question, provider_name="mock", debug=False)
    print("\n结果:")
    for key, value in result.items():
        print(f"  {key}: {value}")

    # 检查是否包含兜底结果
    if result.get("relationship_stage") == "无法判断":
        print("\n⚠️  警告: relationship_stage 仍然是'无法判断' (兜底结果)")
    else:
        print(f"\n✅ 成功: relationship_stage = {result['relationship_stage']} (非兜底结果)")

    if result.get("interest_level") == "无法判断":
        print("⚠️  警告: interest_level 仍然是'无法判断'")
    else:
        print(f"✅ 成功: interest_level = {result['interest_level']}")

    if "系统处理异常" in str(result.get("risk_points")):
        print("⚠️  警告: 风险点包含'系统处理异常'")

    if "系统错误" in result.get("next_step", ""):
        print("⚠️  警告: next_step 包含'系统错误'")

    return result

if __name__ == "__main__":
    test_minimal()