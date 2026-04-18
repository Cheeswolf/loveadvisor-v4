"""
LoveAdvisor V3 - Streamlit Frontend Application
Phase 1: Engineering Skeleton Initialization

This module provides the Streamlit-based user interface for LoveAdvisor V3.
Users can input chat conversations and receive AI-powered relationship analysis.
"""

import streamlit as st
import requests
import json
import io
from typing import Dict, Any, List, Optional


def call_image_to_text_api(api_url: str, image_files: List) -> Dict[str, Any]:
    """
    Call the image-to-text API endpoint with uploaded images.

    Args:
        api_url: Base URL of the API (e.g., "http://localhost:8000")
        image_files: List of Streamlit UploadedFile objects

    Returns:
        Dictionary containing the API response data

    Raises:
        Exception: If the API call fails or returns an error
    """
    try:
        # Ensure API URL doesn't end with slash
        if api_url.endswith('/'):
            api_url = api_url.rstrip('/')
        # Prepare files for multipart/form-data
        files = []
        for img_file in image_files:
            # Reset file pointer to beginning if needed
            if hasattr(img_file, 'seek') and hasattr(img_file, 'tell'):
                if img_file.tell() > 0:
                    img_file.seek(0)

            # Create tuple (filename, file_bytes, content_type)
            file_bytes = img_file.getvalue()
            files.append(
                ('images', (img_file.name, file_bytes, img_file.type or 'image/jpeg'))
            )

        # Additional form data parameters
        data = {
            'provider': 'qwen_ocr',  # Use Qwen-OCR provider supported by backend
            'source_type': 'image'
        }

        # Make POST request
        response = requests.post(
            f"{api_url}/api/v1/image-to-text",
            files=files,
            data=data,
            timeout=30
        )

        # Check response status
        if response.status_code != 200:
            error_msg = f"API返回状态码 {response.status_code}"
            try:
                error_data = response.json()
                if 'error_message' in error_data:
                    error_msg = error_data['error_message']
                elif 'detail' in error_data:
                    error_msg = error_data['detail']
            except:
                error_msg = f"API返回状态码 {response.status_code}: {response.text}"
            raise Exception(error_msg)

        # Parse response
        result = response.json()

        # Check if processing succeeded
        if not result.get('success', False):
            error_msg = result.get('error_message', 'Unknown error from image-to-text API')
            raise Exception(error_msg)

        return result

    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"响应解析失败: {str(e)}")
    except Exception as e:
        raise Exception(f"图片转文字处理失败: {str(e)}")


def calculate_edit_ratio(text1: str, text2: str) -> float:
    """
    计算两个文本之间的编辑比例（字符差异比例）。

    使用简单的字符差异比例：不同字符数 / 最大长度。
    如果两个文本都为空，返回0.0。

    Args:
        text1: 原始文本（merged_text）
        text2: 修改后文本（confirmed_chat_text）

    Returns:
        差异比例，0.0表示完全相同，1.0表示完全不同
    """
    if not text1 and not text2:
        return 0.0

    # 计算最长文本的长度
    max_len = max(len(text1), len(text2))
    if max_len == 0:
        return 0.0

    # 使用简单的编辑距离计算不同字符数
    # 这里使用简单的逐字符比较，对于短文本足够
    diff_count = sum(1 for c1, c2 in zip(text1, text2) if c1 != c2)
    # 加上长度差异的部分
    diff_count += abs(len(text1) - len(text2))

    return diff_count / max_len


def main():
    """
    Main Streamlit application entry point.

    This function sets up the page configuration and initializes the UI components.
    """
    # Page configuration
    st.set_page_config(
        page_title="LoveAdvisor V3",
        page_icon="💘",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Application header
    st.title("💘 LoveAdvisor V3")
    st.markdown("### AI-powered emotional analysis and relationship decision assistant")

    # 添加重新开始按钮
    if st.button("🔄 重新开始", type="secondary", key="reset_top"):
        # 重置所有session_state变量
        keys_to_reset = [
            "analysis_result", "uploaded_images", "image_preview_list",
            "transcription_text", "transcription_status", "confirmed_chat_text",
            "example_chat", "example_question"
        ]
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        # 重新初始化必要的状态
        if "analysis_result" not in st.session_state:
            st.session_state.analysis_result = None
        if "uploaded_images" not in st.session_state:
            st.session_state.uploaded_images = []
        if "image_preview_list" not in st.session_state:
            st.session_state.image_preview_list = []
        if "transcription_text" not in st.session_state:
            st.session_state.transcription_text = ""
        if "transcription_status" not in st.session_state:
            st.session_state.transcription_status = "pending"
        if "confirmed_chat_text" not in st.session_state:
            st.session_state.confirmed_chat_text = ""
        st.rerun()

    # Initialize session state for results
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    if "input_source" not in st.session_state:
        st.session_state.input_source = "text"  # "text" or "image"

    # Initialize session state for input mode and image upload
    if "input_mode" not in st.session_state:
        st.session_state.input_mode = "text"  # "text" or "screenshot"
    if "uploaded_images" not in st.session_state:
        st.session_state.uploaded_images = []  # List of uploaded image files
    if "image_preview_list" not in st.session_state:
        st.session_state.image_preview_list = []  # List of image data for preview
    if "ready_for_transcribe" not in st.session_state:
        st.session_state.ready_for_transcribe = False  # Placeholder for next phase
    # Phase 3: Transcription confirmation state
    if "transcription_text" not in st.session_state:
        st.session_state.transcription_text = ""  # Transcribed text (placeholder/draft)
    if "transcription_status" not in st.session_state:
        st.session_state.transcription_status = "pending"  # "pending", "draft", "confirmed"
    if "confirmed_chat_text" not in st.session_state:
        st.session_state.confirmed_chat_text = ""  # Confirmed chat text after user approval
    if "trigger_image_to_text" not in st.session_state:
        st.session_state.trigger_image_to_text = False  # Flag to trigger image-to-text API call
    # API URL state
    if "api_url" not in st.session_state:
        st.session_state.api_url = "http://localhost:8000"  # Default API URL

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Provider selection
        provider = st.selectbox(
            "LLM Provider",
            options=["mock", "deepseek"],
            index=0,
            help="Select the LLM provider for analysis"
        )
        # Store provider in session state for use in other parts of the app
        st.session_state.provider = provider

        # Debug mode toggle
        debug = st.checkbox(
            "Debug Mode",
            value=False,
            help="Enable to see intermediate pipeline results"
        )

        st.session_state.debug_mode = debug

        # API endpoint configuration
        st.subheader("API Settings")
        api_url = st.text_input(
            "API URL",
            value="http://localhost:8000",
            help="Base URL of the LoveAdvisor API"
        )
        # Store API URL in session state for use in other parts of the app
        st.session_state.api_url = api_url

        # Example conversations
        st.subheader("💡 Examples")
        example = st.selectbox(
            "Load example conversation",
            options=[
                "Select an example...",
                "初识期示例",
                "暧昧期示例",
                "拉扯期示例",
                "冷淡期示例"
            ],
            index=0
        )

        if example != "Select an example...":
            example_texts = {
                "初识期示例": {
                    "chat": "A: 你好，我是通过朋友介绍认识你的\nB: 你好，很高兴认识你\nA: 听朋友说你也在互联网行业工作？\nB: 是的，我做产品经理",
                    "question": "对方对我印象如何？"
                },
                "暧昧期示例": {
                    "chat": "A: 昨晚的电影真好看，特别是和你一起看\nB: 我也觉得，和你在一起总是很开心\nA: 那下次我们再看一部？\nB: 好呀，你选片",
                    "question": "我们的关系有发展可能吗？"
                },
                "拉扯期示例": {
                    "chat": "A: 我觉得我们最近有点疏远了\nB: 可能是工作太忙了吧\nA: 但我觉得你回复消息也变慢了\nB: 别想太多，我只是最近压力大",
                    "question": "他是不是在回避我？"
                },
                "冷淡期示例": {
                    "chat": "A: 在吗？\nB: 嗯\nA: 晚上一起吃个饭？\nB: 不了，有事\nA: 那明天呢？\nB: 再看吧",
                    "question": "这段关系还有希望吗？"
                }
            }
            if example in example_texts:
                st.session_state.example_chat = example_texts[example]["chat"]
                st.session_state.example_question = example_texts[example]["question"]

    # Main content area
    st.header("📝 对话分析")

    # Input mode selection
    input_mode = st.radio(
        "选择输入模式",
        options=["文本输入", "截图上传"],
        index=0 if st.session_state.input_mode == "text" else 1,
        horizontal=True,
        key="input_mode_selector"
    )
    st.session_state.input_mode = "text" if input_mode == "文本输入" else "screenshot"

    # Initialize chat_text variable (used later for analysis)
    chat_text = ""

    if st.session_state.input_mode == "text":
        # Text input mode (existing)
        st.info("💡 **文本模式**: 直接输入聊天记录，格式为 'A: 说话内容\\nB: 回复内容'，其中A代表提问者，B代表对方。")
        chat_text = st.text_area(
            "对话内容",
            height=200,
            placeholder="请输入对话内容，格式为：\nA: 说话内容\nB: 回复内容\nA: ...",
            value=getattr(st.session_state, "example_chat", ""),
            help="输入完整的对话记录，A代表提问者，B代表对方"
        )
    else:
        # Screenshot upload mode
        st.subheader("📸 上传聊天截图")
        st.info("💡 **截图模式**: 请先上传聊天截图 → 确认转写文本 → 再进行分析。")
        st.caption("支持多张图片上传 (PNG/JPG/JPEG)，最大5MB每张，最多支持3张截图。")

        uploaded_files = st.file_uploader(
            "选择或拖拽图片文件",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="screenshot_uploader"
        )

        # Update session state with uploaded files
        if uploaded_files:
            # Only update if there are new files
            current_files = [file.name for file in st.session_state.uploaded_images]
            new_files = [file for file in uploaded_files if file.name not in current_files]
            if new_files:
                # Limit total number of images to 3
                total_after_add = len(st.session_state.uploaded_images) + len(new_files)
                if total_after_add > 3:
                    allowed = 3 - len(st.session_state.uploaded_images)
                    new_files = new_files[:allowed]
                    st.warning(f"最多支持3张截图，已上传{len(st.session_state.uploaded_images)}张，本次添加{allowed}张。")
                st.session_state.uploaded_images.extend(new_files)
                # Store file data for preview (read bytes)
                for file in new_files:
                    st.session_state.image_preview_list.append(file.read())
                # Reset transcription state when new images are added
                st.session_state.transcription_status = "pending"
                st.session_state.transcription_text = ""
                st.session_state.confirmed_chat_text = ""

        # Display uploaded images preview
        if st.session_state.uploaded_images:
            st.subheader("📷 已上传图片")
            cols = st.columns(3)
            for idx, (file, img_data) in enumerate(zip(st.session_state.uploaded_images, st.session_state.image_preview_list)):
                col = cols[idx % 3]
                with col:
                    st.image(img_data, caption=file.name, use_column_width=True)
                    if st.button(f"删除", key=f"delete_{idx}"):
                        # Remove the image
                        del st.session_state.uploaded_images[idx]
                        del st.session_state.image_preview_list[idx]
                        # Reset transcription state when images are removed
                        st.session_state.transcription_status = "pending"
                        st.session_state.transcription_text = ""
                        st.session_state.confirmed_chat_text = ""
                        st.rerun()

            # Clear all button
            if st.button("清空全部图片", type="secondary"):
                st.session_state.uploaded_images.clear()
                st.session_state.image_preview_list.clear()
                st.rerun()
        else:
            st.info("尚未上传任何图片。")

        # Phase 3: Transcription confirmation area (when images are uploaded)
        if st.session_state.uploaded_images:
            st.divider()
            st.subheader("📝 转写结果确认")
            st.caption("图片转文字服务已接入，请检查并修正自动转写的文本内容。")

            # 图转文按钮：手动触发图片转文字API调用
            if st.session_state.transcription_status == "pending":
                st.info("已上传图片，请点击下方按钮进行图转文处理。")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🔄 图转文", type="primary", use_container_width=True):
                        # 设置触发标志，将在后续处理中调用API
                        st.session_state.trigger_image_to_text = True
                        st.rerun()

            # 如果触发标志为True，则调用图片转文字API
            if st.session_state.transcription_status == "pending" and st.session_state.trigger_image_to_text:
                # 重置触发标志，避免重复调用
                st.session_state.trigger_image_to_text = False
                # Show loading state
                with st.spinner(f"正在处理 {len(st.session_state.uploaded_images)} 张图片..."):
                    try:
                        # Get API URL from session state (user may have configured it in sidebar)
                        api_url = st.session_state.get('api_url', 'http://localhost:8000')

                        # Call the image-to-text API
                        print(f"[I1→I2] 调用图片转文字API，图片数量: {len(st.session_state.uploaded_images)}")
                        result = call_image_to_text_api(api_url, st.session_state.uploaded_images)

                        # Check if processing succeeded
                        if result.get('success', False):
                            # Get merged_text from response
                            merged_text = result.get('merged_text', '')
                            image_count = result.get('image_count', 0)
                            ocr_provider = result.get('provider', 'unknown')

                            # 调试输出：打印接收到的 merged_text 信息
                            print(f"[I1→I2] 成功接收 merged_text，长度: {len(merged_text)}，内容预览: {merged_text[:100]}...")

                            # Check if merged_text is empty or only whitespace
                            if not merged_text or merged_text.strip() == '':
                                st.warning("图片转文字服务返回空文本，请手动输入对话内容。")
                                # 注意：merged_text 保持为空字符串，不替换为占位符

                            # Update transcription text with merged_text (可能为空字符串)
                            st.session_state.transcription_text = merged_text
                            st.session_state.transcription_status = "draft"
                            print(f"[I1→I2] merged_text 已写入 transcription_text，session_state 设置完成")

                            # Show success message
                            st.success(f"成功从 {image_count} 张图片中提取文本 (使用 {ocr_provider} 服务)")

                            # Store API result in session state for debugging
                            st.session_state.last_image_to_text_result = result
                        else:
                            # API returned success=false
                            error_message = result.get('error_message', '未知错误')
                            print(f"[I1→I2] API返回success=false，错误信息: {error_message}")
                            st.session_state.transcription_status = "error"
                            st.session_state.transcription_error = error_message
                            st.error(f"图片转文字处理失败: {error_message}")

                    except Exception as e:
                        # Handle any exceptions during API call
                        print(f"[I1→I2] 调用API时发生异常: {str(e)}")
                        st.session_state.transcription_status = "error"
                        st.session_state.transcription_error = str(e)
                        st.error(f"图片转文字处理失败: {str(e)}")

                # Rerun to update UI with new transcription text or error state
                st.rerun()

            # Display transcription status
            status_color = {
                "pending": "gray",
                "draft": "blue",
                "confirmed": "green",
                "error": "red"
            }.get(st.session_state.transcription_status, "gray")
            status_display = st.session_state.transcription_status
            if status_display == "error":
                status_display = "错误 - 点击重试"
            st.caption(f"状态: :{status_color}[{status_display}]")

            # Debug information for image-to-text processing
            if st.session_state.debug_mode:
                with st.expander("🔍 截图输入调试信息"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**transcription_status:**", st.session_state.transcription_status)
                        st.write("**confirmed:**", "是" if st.session_state.transcription_status == "confirmed" else "否")
                        if st.session_state.transcription_status == "confirmed":
                            st.write("**当前使用文本:**", "确认文本")
                        elif st.session_state.transcription_status == "draft":
                            st.write("**当前使用文本:**", "草稿文本")
                        else:
                            st.write("**当前使用文本:**", "无")

                    with col2:
                        if 'last_image_to_text_result' in st.session_state:
                            result = st.session_state.last_image_to_text_result
                            st.write("**I1 raw_text:**")
                            raw_text = result.get('raw_text', '')
                            # 显示raw_text的前500字符
                            if raw_text:
                                st.text_area("raw_text", raw_text[:500] + ("..." if len(raw_text) > 500 else ""), height=150, disabled=True, label_visibility="collapsed")
                            else:
                                st.write("（空）")

                            st.write("**I1 merged_text:**")
                            merged_text = result.get('merged_text', '')
                            if merged_text:
                                st.text_area("merged_text", merged_text[:500] + ("..." if len(merged_text) > 500 else ""), height=150, disabled=True, label_visibility="collapsed")
                            else:
                                st.write("（空）")

                            # 计算修改比例（如果已确认）
                            if st.session_state.transcription_status == "confirmed" and merged_text:
                                confirmed_text = st.session_state.confirmed_chat_text
                                if confirmed_text:
                                    edit_ratio = calculate_edit_ratio(merged_text, confirmed_text)
                                    st.write(f"**用户修改比例:** {edit_ratio:.2%}")
                        else:
                            st.write("尚未调用图片转文字API")

            # Retry button for error state
            if st.session_state.transcription_status == "error":
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    if st.button("🔄 重试图片转文字", type="secondary", use_container_width=True):
                        # Reset status to pending to trigger API call again
                        st.session_state.transcription_status = "pending"
                        st.session_state.transcription_text = ""
                        if 'transcription_error' in st.session_state:
                            del st.session_state.transcription_error
                        st.rerun()
                st.text(f"错误详情: {st.session_state.get('transcription_error', '未知错误')}")

            # Editable text area for transcription correction
            edited_text = st.text_area(
                "转写结果 (可编辑修正)",
                height=250,
                placeholder="转写结果将显示在这里，您可以进行编辑修正...",
                key="transcription_text"
            )

            # Update transcription text if edited
            if edited_text != st.session_state.transcription_text:
                st.session_state.transcription_text = edited_text
                # If text is edited after confirmation, revert to draft status
                if st.session_state.transcription_status == "confirmed":
                    st.session_state.transcription_status = "draft"
                    st.rerun()

            # Confirmation button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                confirm_disabled = st.session_state.transcription_status == "confirmed"
                confirm_button = st.button(
                    "✅ 确认文本",
                    type="primary",
                    disabled=confirm_disabled,
                    use_container_width=True,
                    key="confirm_transcription"
                )

            if confirm_button:
                st.session_state.confirmed_chat_text = st.session_state.transcription_text
                st.session_state.transcription_status = "confirmed"
                st.success("文本已确认！下一阶段将接入分析流程。")
                st.info(f"已确认文本长度: {len(st.session_state.confirmed_chat_text)} 字符")
                st.rerun()

            # Display confirmation status
            if st.session_state.transcription_status == "confirmed":
                st.divider()
                st.subheader("✅ 文本确认完成")
                st.success("转写文本已确认，下一阶段将接入分析流程。")
                with st.expander("查看已确认的文本"):
                    st.text(st.session_state.confirmed_chat_text)
        else:
            # No images uploaded - show original placeholder and reset transcription state
            st.info("请上传聊天截图以使用图片转文字功能。")
            # Reset transcription state when no images are uploaded
            if st.session_state.transcription_status != "pending":
                st.session_state.transcription_status = "pending"
                st.session_state.transcription_text = ""
                st.session_state.confirmed_chat_text = ""

    # User question input
    user_question = st.text_input(
        "分析问题",
        placeholder="例如：对方对我有兴趣吗？我们的关系处于什么阶段？",
        value=getattr(st.session_state, "example_question", ""),
        help="输入你想分析的具体问题"
    )

    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Disable button based on input mode and validation
        if st.session_state.input_mode == "text":
            disabled = (not chat_text.strip()) or (not user_question.strip())
        else:  # screenshot mode
            disabled = (st.session_state.transcription_status != "confirmed") or (not st.session_state.confirmed_chat_text.strip()) or (not user_question.strip())

        analyze_button = st.button(
            "🚀 开始分析",
            type="primary",
            use_container_width=True,
            disabled=disabled
        )
        if st.session_state.input_mode == "screenshot":
            if st.session_state.transcription_status != "confirmed":
                st.caption("请先确认转写文本以启用分析功能。")
            elif not st.session_state.confirmed_chat_text.strip():
                st.caption("确认的文本为空，请重新转写。")

    if analyze_button:
        # Get API URL and provider from session state
        api_url = st.session_state.get('api_url', 'http://localhost:8000')
        # Ensure API URL doesn't end with slash
        if api_url.endswith('/'):
            api_url = api_url.rstrip('/')
        provider = st.session_state.provider
        debug = st.session_state.get('debug_mode', False)

        # Determine chat text based on input mode and record input source
        if st.session_state.input_mode == "text":
            analysis_chat_text = chat_text
            st.session_state.input_source = "text"
        else:  # screenshot mode
            # Additional safety check (should already be enforced by button disabled state)
            if st.session_state.transcription_status != "confirmed":
                st.error("文本未确认，无法进行分析。")
                st.stop()
            if not st.session_state.confirmed_chat_text.strip():
                st.error("确认的文本为空，无法进行分析。")
                st.stop()
            analysis_chat_text = st.session_state.confirmed_chat_text
            st.session_state.input_source = "image"

        # Calculate edit ratio for image mode (if applicable)
        edit_ratio = None
        if st.session_state.input_source == "image" and 'last_image_to_text_result' in st.session_state:
            merged_text = st.session_state.last_image_to_text_result.get('merged_text', '')
            if merged_text and analysis_chat_text:
                edit_ratio = calculate_edit_ratio(merged_text, analysis_chat_text)

        # Log analysis information to console
        print("\n" + "="*60)
        print("[Image Flow]") if st.session_state.input_source == "image" else print("[Text Flow]")
        print(f"input_source={st.session_state.input_source}")
        if st.session_state.input_source == "image":
            image_count = len(st.session_state.uploaded_images) if 'uploaded_images' in st.session_state else 0
            print(f"image_count={image_count}")
            text_length = len(analysis_chat_text)
            print(f"text_length={text_length}")
            if edit_ratio is not None:
                print(f"edit_ratio={edit_ratio:.2%}")
            status = st.session_state.transcription_status if 'transcription_status' in st.session_state else "unknown"
            print(f"status={status}")
        else:
            text_length = len(analysis_chat_text)
            print(f"text_length={text_length}")
        # 新增可观测信息
        request_url = f"{api_url}/api/v1/analyze"
        print(f"当前模式: {'image' if st.session_state.input_source == 'image' else 'text'}")
        print(f"实际发送到 analyze 的 chat_text 前300字: {analysis_chat_text[:300]}")
        print(f"文本长度: {len(analysis_chat_text)}")
        print(f"请求 URL: {request_url}")
        print(f"provider_name: {provider}")
        print("="*60 + "\n")

        # 如果开启debug模式，在前端显示调试信息
        if debug:
            with st.expander("🔍 分析请求调试信息"):
                st.write("**当前模式:**", 'image' if st.session_state.input_source == 'image' else 'text')
                st.write("**文本长度:**", len(analysis_chat_text))
                st.write("**请求 URL:**", request_url)
                st.write("**provider_name:**", provider)
                st.write("**chat_text 前300字:**")
                st.text(analysis_chat_text[:300])

        with st.spinner("正在分析中，请稍候..."):
            try:
                # Prepare request payload
                payload = {
                    "chat_text": analysis_chat_text,
                    "user_question": user_question,
                    "provider_name": provider,
                    "debug": debug
                }
                # 调试：打印发送的 provider_name
                print(f"[前端] 发送的 provider_name: {provider}")
                print(f"[前端] payload: {payload}")

                # Make API request
                request_url = f"{api_url}/api/v1/analyze"
                response = requests.post(
                    request_url,
                    json=payload,
                    timeout=30
                )

                # 打印响应信息
                print("\n" + "="*60)
                print("分析响应信息")
                print(f"HTTP 状态码: {response.status_code}")
                # 打印响应体前1000字符
                response_text = response.text
                print(f"响应体长度: {len(response_text)}")
                print(f"响应体前1000字符: {response_text[:1000]}")
                # 初始化变量
                relationship_stage = "N/A"
                interest_level = "N/A"
                has_error_field = False
                response_status = "N/A"
                error_message = "N/A"
                if response.status_code == 200:
                    try:
                        result = response.json()
                        st.session_state.analysis_result = result
                        st.success("分析完成！")
                        # 提取结果字段
                        relationship_stage = result.get("result", {}).get("relationship_stage", "N/A")
                        interest_level = result.get("result", {}).get("interest_level", "N/A")
                        has_error_field = "error" in result
                        response_status = result.get("status", "N/A")
                        error_message = result.get("error_message", "N/A")
                        print(f"返回的 status: {response_status}")
                        print(f"返回的 relationship_stage: {relationship_stage}")
                        print(f"返回的 interest_level: {interest_level}")
                        print(f"是否有 error 字段: {has_error_field}")
                        print(f"error_message: {error_message}")
                        # 打印 metadata 中的 provider_used
                        metadata = result.get("metadata", {})
                        provider_used = metadata.get("provider_used", "N/A")
                        print(f"metadata.provider_used: {provider_used}")
                    except json.JSONDecodeError as e:
                        print(f"JSON 解析失败: {e}")
                        print(f"原始响应: {response_text[:500]}")
                else:
                    st.error("分析请求失败，请稍后重试")
                    print(f"错误响应: {response_text[:500]}")
                print("="*60 + "\n")

                # 如果开启debug模式，在前端显示调试信息
                if debug:
                    with st.expander("🔍 分析响应调试信息"):
                        st.write("**HTTP 状态码:**", response.status_code)
                        if response.status_code == 200:
                            st.write("**relationship_stage:**", relationship_stage)
                            st.write("**interest_level:**", interest_level)
                            st.write("**是否有 error 字段:**", has_error_field)
                        else:
                            st.write("**错误响应:**")
                            st.code(response.text[:1000], language="text")

            except requests.exceptions.RequestException:
                st.error("网络异常或服务不可用")
                if st.session_state.debug_mode:
                    st.info("请确保LoveAdvisor API服务正在运行。可运行: `python run.py`")

    # Display results if available
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        st.divider()
        st.header("📊 分析结果")

        # 显示输入来源
        source_display = "截图输入" if st.session_state.input_source == "image" else "文本输入"
        st.caption(f"本次分析来源: **{source_display}**")

        # 1. 顶部摘要区
        st.subheader("📋 摘要")
        col1, col2, col3 = st.columns(3)
        with col1:
            relationship_stage = result["result"]["relationship_stage"]
            st.metric("关系阶段", relationship_stage)
        with col2:
            interest_level = result["result"]["interest_level"]
            st.metric("兴趣水平", interest_level)
        with col3:
            # 一句话结论
            one_sentence_conclusion = f"当前关系处于{relationship_stage}阶段，对方兴趣水平为{interest_level}。"
            st.markdown(f"**一句话结论：** {one_sentence_conclusion}")

        st.divider()

        # 2. 关键信号区（使用心理分析字段）
        st.subheader("🔍 关键信号分析")
        st.info(result["result"]["psychological_analysis"])

        st.divider()

        # 3. 风险提示区
        st.subheader("⚠️ 风险提示")
        risk_points = result["result"]["risk_points"]
        if risk_points:
            for i, risk in enumerate(risk_points, 1):
                st.warning(f"**风险 {i}:** {risk}")
        else:
            st.success("✅ 未识别到明显风险点")

        st.divider()

        # 4. 建议区
        st.subheader("💡 建议")
        suggestions = result["result"]["suggestions"]
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                st.info(f"**建议 {i}:** {suggestion}")
        else:
            st.write("暂无具体建议")

        st.divider()

        # 5. 下一步动作区（单独高亮）
        st.subheader("🎯 下一步动作")
        next_step = result["result"]["next_step"]
        st.success(f"**{next_step}**")

        # Debug information
        if st.session_state.debug_mode and "debug" in result["result"]:
            st.divider()
            st.header("🔍 调试信息")

            debug_info = result["result"]["debug"]

            tabs = st.tabs(["S2信号", "S3信号", "R1推理", "S5策略"])

            with tabs[0]:
                if "s2" in debug_info:
                    st.json(debug_info["s2"])

            with tabs[1]:
                if "s3" in debug_info:
                    st.json(debug_info["s3"])

            with tabs[2]:
                if "r1" in debug_info:
                    st.json(debug_info["r1"])

            with tabs[3]:
                if "s5_raw" in debug_info and "s5_final" in debug_info:
                    st.subheader("原始S5输出")
                    st.json(debug_info["s5_raw"])
                    st.subheader("经过Guardrail后的S5输出")
                    st.json(debug_info["s5_final"])

        # Raw JSON view (collapsible)
        with st.expander("📋 查看原始API响应"):
            st.json(result)

        # 结果页重新开始按钮
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 重新开始分析", type="secondary", use_container_width=True, key="reset_results"):
                # 重置所有session_state变量
                keys_to_reset = [
                    "analysis_result", "uploaded_images", "image_preview_list",
                    "transcription_text", "transcription_status", "confirmed_chat_text",
                    "example_chat", "example_question"
                ]
                for key in keys_to_reset:
                    if key in st.session_state:
                        del st.session_state[key]
                # 重新初始化必要的状态
                if "analysis_result" not in st.session_state:
                    st.session_state.analysis_result = None
                if "uploaded_images" not in st.session_state:
                    st.session_state.uploaded_images = []
                if "image_preview_list" not in st.session_state:
                    st.session_state.image_preview_list = []
                if "transcription_text" not in st.session_state:
                    st.session_state.transcription_text = ""
                if "transcription_status" not in st.session_state:
                    st.session_state.transcription_status = "pending"
                if "confirmed_chat_text" not in st.session_state:
                    st.session_state.confirmed_chat_text = ""
                st.rerun()

    # Footer
    st.divider()
    st.caption("LoveAdvisor V3 • Phase 6: API + 前端联调")


if __name__ == "__main__":
    main()