from typing import Any, Dict

import requests

from app.rules import rules
from app.services.coze_client import run_workflow
from app.services.output_builder import assemble_output, default_output
from app.services.result_parser import extract_nested_output
from app.utils.helpers import ensure_json_string
from configs.settings import EXTRACT_WORKFLOW_ID, S5_WORKFLOW_ID

print("=== PIPELINE_SERVICE FILE LOADED ===")


def run_pipeline(text: str):
    print("=== PIPELINE FUNCTION HIT ===")
    print("=== RULES MODULE ===", rules)
    print("=== RULES FILE ===", getattr(rules, "__file__", "NO_FILE"))
    print("=== PIPELINE INPUT ===", text)

    if not str(text).strip():
        return default_output(
            psychological_analysis="输入内容不足，当前无法形成有效判断。",
            suggestions=["请提供更完整的聊天记录后再分析。"],
            next_step="补充更多上下文"
        )

    try:
        # =========================
        # Step 1: 调用前半段工作流（S1/S2/S3）
        # =========================
        extract_data = run_workflow(
            EXTRACT_WORKFLOW_ID,
            {
                "chat_text": text
            }
        )

        print("=== AFTER EXTRACT WORKFLOW ===", extract_data)

        s2 = extract_nested_output(extract_data, "S2_output")
        s3 = extract_nested_output(extract_data, "S3_output")

        print("=== DEBUG S2 ===", s2)
        print("=== DEBUG S3 ===", s3)
        print("=== DEBUG R1 INPUT READY ===")

        # =========================
        # Step 2: 后端规则引擎 R1（强制使用 rules.py）
        # =========================
        r1 = rules.infer_r1(s2, s3)
        print("=== DEBUG R1 ===", r1)

        # =========================
        # Step 3: 调用 S5 工作流
        # =========================
        s5_data = run_workflow(
            S5_WORKFLOW_ID,
            {
                "S2_output": ensure_json_string(s2),
                "S3_output": ensure_json_string(s3),
                "R1_output": ensure_json_string(r1),
                "user_question": ""
            }
        )

        print("=== AFTER S5 WORKFLOW ===", s5_data)

        s5 = extract_nested_output(s5_data, "S5_output")
        print("=== DEBUG S5 ===", s5)

        # =========================
        # Step 4: O1 后端组装
        # =========================
        final_output = assemble_output(s2, s3, r1, s5)
        print("=== FINAL OUTPUT ===", final_output)

        return final_output

    except requests.exceptions.Timeout:
        return default_output(
            psychological_analysis="请求超时，当前未能完成分析。",
            suggestions=["请稍后重试。"],
            next_step="检查工作流耗时或更换更轻量模型"
        )

    except requests.exceptions.RequestException as e:
        return default_output(
            psychological_analysis=f"接口请求异常：{str(e)}",
            suggestions=["请检查 Coze Token、workflow_id 和网络状态。"],
            next_step="排查接口配置"
        )

    except Exception as e:
        return default_output(
            psychological_analysis=f"系统处理异常：{str(e)}",
            suggestions=["请查看后端日志并检查返回结构。"],
            next_step="排查 JSON 解析与结束节点输出"
        )