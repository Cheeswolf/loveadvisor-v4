#!/usr/bin/env python3
"""
测试异步修复是否消除了 asyncio.run() 错误。
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟一个运行中的事件循环，然后调用同步包装器
import asyncio
import threading
import time

def run_in_separate_thread():
    """在一个新线程中运行事件循环，模拟 FastAPI 的异步上下文"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def inner_test():
        from app.core.pipeline_orchestrator import run_analysis_async
        # 在运行中的事件循环内调用异步版本
        try:
            result = await run_analysis_async(
                chat_text="A：今天怎么不找我\nB：在想你啊\nA：真的假的\nB：骗你干嘛\nA：那你想我什么\nB：想见你",
                user_question="他对我有兴趣吗？",
                provider_name="mock",
                debug=True
            )
            print("✅ 异步调用成功")
            print(f"relationship_stage: {result.get('relationship_stage')}")
            return True
        except RuntimeError as e:
            if "cannot be called from a running event loop" in str(e):
                print(f"❌ 仍然出现 asyncio.run() 错误: {e}")
                return False
            else:
                raise

    try:
        success = loop.run_until_complete(inner_test())
        return success
    finally:
        loop.close()

def test_sync_wrapper():
    """测试同步包装器（无事件循环）"""
    from app.core.pipeline_orchestrator import run_analysis
    try:
        result = run_analysis(
            chat_text="A：今天怎么不找我\nB：在想你啊\nA：真的假的\nB：骗你干嘛\nA：那你想我什么\nB：想见你",
            user_question="他对我有兴趣吗？",
            provider_name="mock",
            debug=True
        )
        print("✅ 同步包装器调用成功")
        print(f"relationship_stage: {result.get('relationship_stage')}")
        return True
    except Exception as e:
        print(f"❌ 同步包装器失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("测试异步修复...")
    print("1. 测试同步包装器（无事件循环）...")
    sync_ok = test_sync_wrapper()
    print("\n2. 测试在运行中的事件循环内调用异步版本...")
    # 在新线程中运行，避免干扰主线程
    import threading
    thread = threading.Thread(target=run_in_separate_thread)
    thread.start()
    thread.join()
    print("\n测试完成。")