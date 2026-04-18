#!/usr/bin/env python3
"""
测试B1样本使用DeepSeek provider（修复模型配置后）
"""
import sys
import os
import json
import asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置虚拟API密钥（不会实际调用，因为我们会模拟请求？）
os.environ['DEEPSEEK_API_KEY'] = 'dummy_key'
os.environ['LLM_PROVIDER'] = 'deepseek'

from app.llm.provider_factory import get_provider
from app.llm.base_provider import LLMRequest

async def test_deepseek_config():
    """测试DeepSeek配置"""
    print("=== 测试DeepSeek provider配置 ===")
    try:
        # 使用空配置，应使用默认值
        provider = get_provider('deepseek', {})
        print(f"Provider创建成功: {provider}")
        print(f"模型名称: {provider.get_model_name()}")
        print(f"配置中的model: {provider.model}")
        print(f"base_url: {provider.base_url}")

        # 检查默认配置
        from app.llm.provider_factory import _get_provider_default_config
        config = _get_provider_default_config('deepseek')
        print(f"默认配置: {config}")

        # 尝试发送请求（会因API密钥无效而失败，但我们可以看到请求payload）
        request = LLMRequest(prompt="Test", max_tokens=10)
        try:
            response = await provider.complete(request)
            print(f"响应: {response}")
        except Exception as e:
            print(f"请求失败（预期）: {e}")
            # 检查错误是否与模型相关
            if 'model' in str(e).lower() or 'not exist' in str(e).lower():
                print("⚠️  错误仍与模型相关，可能配置未生效")
            else:
                print("✅ 错误与模型无关，说明模型配置正确")

        return provider
    except Exception as e:
        print(f"创建provider失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_b1_sample():
    """测试B1样本"""
    print("\n=== 测试B1样本 ===")
    chat_text = "A：今天怎么不找我\nB：在想你啊\nA：真的假的\nB：骗你干嘛\nA：那你想我什么\nB：想见你"
    user_question = "他对我有兴趣吗？"

    # 导入pipeline_orchestrator（可能触发循环导入，尝试直接调用）
    try:
        from app.core.pipeline_orchestrator import run_analysis
        print("调用run_analysis...")
        result = run_analysis(chat_text, user_question, provider_name="deepseek", debug=True)
        print("结果获取成功")

        # 提取debug信息
        debug_info = result.get("debug", {})

        # 输出关键信息
        print(f"最终结果关系阶段: {result.get('relationship_stage')}")
        print(f"兴趣等级: {result.get('interest_level')}")

        # 检查debug中是否包含模型信息
        if debug_info:
            s2_raw = debug_info.get('s2_raw_response')
            s3_raw = debug_info.get('s3_raw_response')
            if s2_raw:
                print(f"s2_raw_response 包含模型信息: {s2_raw.get('model') if isinstance(s2_raw, dict) else 'N/A'}")
            if s3_raw:
                print(f"s3_raw_response 包含模型信息: {s3_raw.get('model') if isinstance(s3_raw, dict) else 'N/A'}")

        # 输出完整debug信息（JSON格式）
        output = {
            "sample": "B1",
            "provider": "deepseek",
            "final_result": {
                "relationship_stage": result.get("relationship_stage"),
                "interest_level": result.get("interest_level"),
                "psychological_analysis": result.get("psychological_analysis"),
                "risk_points": result.get("risk_points"),
                "suggestions": result.get("suggestions"),
                "next_step": result.get("next_step")
            },
            "debug_info": debug_info
        }

        print("\n=== 完整debug输出（JSON）===")
        print(json.dumps(output, ensure_ascii=False, indent=2))

        return result
    except ImportError as e:
        print(f"导入失败: {e}")
        print("跳过pipeline测试")
    except Exception as e:
        print(f"运行分析失败: {e}")
        import traceback
        traceback.print_exc()

    return None

async def main():
    print("LoveAdvisor V3 - DeepSeek模型配置修复测试")
    print("=" * 50)

    # 测试配置
    provider = await test_deepseek_config()

    if provider:
        # 测试B1样本
        await test_b1_sample()
    else:
        print("无法创建provider，跳过样本测试")

if __name__ == "__main__":
    asyncio.run(main())