import json
from typing import Any, Dict


def safe_json_loads(value: Any) -> Dict[str, Any]:
    """
    安全解析 JSON：
    - 如果本身就是 dict，直接返回
    - 如果是 JSON 字符串，尝试解析
    - 如果解析失败，返回空 dict
    """
    if isinstance(value, dict):
        return value

    if value is None:
        return {}

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return {}

        # 去掉 ```json ... ``` 包裹
        if value.startswith("```"):
            value = value.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
            return {}
        except Exception:
            return {}

    return {}


def ensure_json_string(value: Any) -> str:
    """
    确保传给 Coze 的是 JSON 字符串
    """
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def safe_str(value: Any, default: str = "无法判断") -> str:
    """
    字符串字段兜底
    """
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def safe_list(value: Any) -> list:
    """
    数组字段兜底
    """
    return value if isinstance(value, list) else []