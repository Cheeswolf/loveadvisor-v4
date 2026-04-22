import json
from typing import Any, Dict, List

import requests
import streamlit as st


# =========================
# 页面基础配置
# =========================
st.set_page_config(
    page_title="LoveAdvisor",
    page_icon="💘",
    layout="wide"
)

st.title("💘 LoveAdvisor")
st.caption("AI 情感分析与恋爱决策助手")


# =========================
# 后端配置
# =========================
BACKEND_URL = "http://127.0.0.1:8000/api/v1/analyze"
REQUEST_TIMEOUT = 120


# =========================
# 工具函数
# =========================
def safe_str(value: Any, default: str = "无法判断") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def call_backend(chat_text: str, user_question: str) -> Dict[str, Any]:
    payload = {
        "chat_text": chat_text,
        "user_question": user_question
    }

    response = requests.post(
        BACKEND_URL,
        json=payload,
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def stage_badge(stage: str) -> str:
    stage = safe_str(stage, "")
    mapping = {
        "初识期": "🟦 初识期",
        "暧昧期": "🩷 暧昧期",
        "拉扯期": "🟨 拉扯期",
        "冷淡期": "⬜ 冷淡期",
        "无法判断": "🟥 无法判断",
    }
    return mapping.get(stage, f"📌 {stage}")


def interest_badge(level: str) -> str:
    level = safe_str(level, "")
    mapping = {
        "高": "🔥 高",
        "中": "🌤️ 中",
        "低": "🧊 低",
        "无法判断": "❓ 无法判断",
    }
    return mapping.get(level, f"📌 {level}")


def render_list(title: str, items: List[Any], empty_text: str = "暂无") -> None:
    st.markdown(f"### {title}")
    items = safe_list(items)

    if not items:
        st.info(empty_text)
        return

    for item in items:
        st.markdown(f"- {safe_str(item, '')}")


def render_result(result: Dict[str, Any]) -> None:
    relationship_stage = safe_str(result.get("relationship_stage"))
    interest_level = safe_str(result.get("interest_level"))
    key_signals = safe_list(result.get("key_signals"))
    signal_summary = safe_list(result.get("signal_summary"))
    psychological_analysis = safe_str(
        result.get("psychological_analysis"),
        "输入内容不足，当前无法形成有效判断。"
    )
    risk_points = safe_list(result.get("risk_points"))
    suggestions = safe_list(result.get("suggestions"))
    next_step = safe_str(result.get("next_step"))

    # 顶部结论区
    st.subheader("📊 分析结果概览")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("关系阶段", stage_badge(relationship_stage))
    with col2:
        st.metric("兴趣等级", interest_badge(interest_level))

    st.divider()

    # 中间分析区
    left, right = st.columns(2)

    with left:
        render_list("🔍 关键信号", key_signals, "暂无关键信号")
        render_list("🧩 信号总结", signal_summary, "暂无信号总结")

    with right:
        st.markdown("### 🧠 心理分析")
        st.write(psychological_analysis)

    st.divider()

    # 风险与建议区
    left2, right2 = st.columns(2)

    with left2:
        render_list("⚠️ 风险点", risk_points, "当前暂无明显风险点")

    with right2:
        render_list("✅ 建议", suggestions, "当前暂无建议")

    st.divider()

    # 下一步
    st.markdown("### 🚶 下一步建议")
    st.success(next_step)

    # 调试区
    with st.expander("查看原始返回 JSON（调试用）"):
        st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")


# =========================
# 输入区
# =========================
st.markdown("## ✍️ 输入聊天记录")

default_chat_text = """A：你好
B：你好
A：你是哪个专业的
B：金融
A：挺不错的"""

default_question = "请分析当前关系状态并给出建议"

chat_text = st.text_area(
    "聊天记录",
    value=default_chat_text,
    height=260,
    placeholder="请粘贴完整聊天记录，建议保留 A/B 说话人格式。"
)

user_question = st.text_input(
    "你的问题",
    value=default_question,
    placeholder="例如：他现在对我是什么态度？"
)

analyze_button = st.button("开始分析", type="primary", use_container_width=True)


# =========================
# 主逻辑
# =========================
if analyze_button:
    if not chat_text.strip():
        st.warning("请先输入聊天记录。")
    else:
        with st.spinner("正在分析中，请稍候..."):
            try:
                result = call_backend(chat_text, user_question)
                st.session_state["last_result"] = result
                st.session_state["last_error"] = None

            except requests.exceptions.Timeout:
                st.session_state["last_result"] = None
                st.session_state["last_error"] = "请求超时：后端或 Coze 工作流耗时过长。"

            except requests.exceptions.ConnectionError:
                st.session_state["last_result"] = None
                st.session_state["last_error"] = (
                    "无法连接后端。请确认 FastAPI 已启动，并检查 BACKEND_URL 是否正确。"
                )

            except requests.exceptions.HTTPError as e:
                st.session_state["last_result"] = None
                try:
                    detail = e.response.text
                except Exception:
                    detail = str(e)
                st.session_state["last_error"] = f"后端返回异常：{detail}"

            except Exception as e:
                st.session_state["last_result"] = None
                st.session_state["last_error"] = f"前端处理异常：{str(e)}"


# =========================
# 输出区
# =========================
if st.session_state.get("last_error"):
    st.error(st.session_state["last_error"])

if st.session_state.get("last_result"):
    render_result(st.session_state["last_result"])