from typing import Any, Dict

import json
import requests

from app.utils.helpers import safe_json_loads
from configs.settings import COZE_API, REQUEST_TIMEOUT, TOKEN


def run_workflow(
    workflow_id: str,
    parameters: Dict[str, Any],
    timeout: int = REQUEST_TIMEOUT
) -> Dict[str, Any]:
    """
    调用 Coze Workflow
    临时增强版：
    1. 打印原始响应
    2. 尝试多种常见返回结构
    3. 不再静默吞掉信息
    """
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "workflow_id": workflow_id,
        "parameters": parameters,
    }

    resp = requests.post(COZE_API, headers=headers, json=payload, timeout=timeout)

    print("\n=== COZE DEBUG START ===")
    print("WORKFLOW_ID:", workflow_id)
    print("COZE_API:", COZE_API)
    print("REQUEST_PAYLOAD:", json.dumps(payload, ensure_ascii=False, indent=2))
    print("STATUS_CODE:", resp.status_code)
    print("RESPONSE_TEXT:", resp.text)
    print("=== COZE DEBUG END ===\n")

    resp.raise_for_status()

    raw = resp.json()
    print("=== COZE PARSED JSON ===")
    print(json.dumps(raw, ensure_ascii=False, indent=2))

    # -------------------------
    # 依次尝试常见返回位置
    # -------------------------
    candidates = [
        raw.get("data"),
        raw.get("output"),
        raw.get("outputs"),
    ]

    # data 下面再嵌套一层
    if isinstance(raw.get("data"), dict):
        data_obj = raw["data"]
        candidates.extend([
            data_obj.get("output"),
            data_obj.get("outputs"),
            data_obj.get("result"),
        ])

    for item in candidates:
        if item is None:
            continue

        # 直接是 dict
        if isinstance(item, dict):
            return item

        # 直接是 list，包装一下返回，避免吞掉
        if isinstance(item, list):
            return {"raw_list": item}

        # 是字符串，尝试 JSON 解析
        if isinstance(item, str):
            parsed = safe_json_loads(item)
            if parsed:
                return parsed

            # 有些接口会把 JSON 字符串再包一层
            try:
                parsed2 = json.loads(item)
                if isinstance(parsed2, dict):
                    return parsed2
            except Exception:
                pass

            return {"raw_data": item}

    # 如果走到这里，说明没匹配到任何有效输出
    return {
        "_debug_error": "No usable output found in Coze response",
        "_raw_response": raw,
    }