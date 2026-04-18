from typing import Any, Dict

from app.utils.helpers import safe_json_loads


def extract_nested_output(data: Dict[str, Any], key: str) -> Dict[str, Any]:
    """
    统一提取类似 S2_output / S3_output / S5_output
    兼容：
    1. data[key] 直接存在
    2. data["raw_data"] 中嵌套 JSON 字符串
    """
    if key in data:
        return safe_json_loads(data.get(key))

    nested = safe_json_loads(data.get("raw_data"))
    return safe_json_loads(nested.get(key))