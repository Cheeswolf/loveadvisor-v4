《I1 图转文接口协议（冻结版）》
—— LoveAdvisor V3.6 输入层节点规范
一、文档定位

本文件用于：

冻结 I1（Image → Text）接口协议与职责边界
⚠️ 强制说明

本阶段：

❌ 不写代码
❌ 不接入 OCR / 模型
❌ 不修改 analyze
❌ 不涉及 pipeline

仅做：

接口协议 + 数据结构 + 边界定义冻结
二、I1 节点定义
2.1 一句话定义
I1 = 图片 → 文本草稿生成器
2.2 节点定位
维度	说明
所属层	输入层
是否属于分析引擎	❌ 否
是否参与关系判断	❌ 否
是否可绕过 I2	❌ 不允许
2.3 在系统中的位置
截图输入
→ I1 图转文节点
→ I2 用户确认层
→ /api/v1/analyze
三、接口定义（冻结）
3.1 接口路径
POST /api/v1/image-to-text
3.2 接口职责

I1 只负责：

接收图片输入
提取文本内容
合并多图结果
输出文本初稿
❌ 明确不负责
关系阶段判断
兴趣等级判断
建议生成
用户问题理解
跳过 I2 直接分析
四、输入协议（冻结）
4.1 请求结构
{
  "images": [
    "<base64_or_file_ref>",
    "<base64_or_file_ref>"
  ]
}
4.2 字段说明
字段	类型	说明
images	list[string]	图片数据（base64或文件引用）
4.3 第一版限制

仅支持：

jpg / jpeg / png
单张或多张
按上传顺序处理
❌ 明确不支持
PDF
视频
拖拽排序增强
图像元数据解析
五、输出协议（核心冻结）
5.1 标准返回结构
{
  "success": true,
  "raw_text": "识别得到的原始文本",
  "merged_text": "整理后的聊天文本初稿",
  "provider": "vision_model_v1",
  "source_type": "image",
  "image_count": 2,
  "need_user_confirm": true,
  "error_message": ""
}
5.2 字段说明
字段	含义
success	是否成功
raw_text	原始识别文本
merged_text	面向用户的草稿文本
provider	当前图转文来源
source_type	固定为 image
image_count	图片数量
need_user_confirm	必须为 true
error_message	错误信息
5.3 关键设计（必须理解）
🔥 双字段机制
raw_text ≠ merged_text
为什么必须这样设计？
需求	对应字段
调试识别是否正确	raw_text
用户编辑体验	merged_text

👉 如果只保留一个字段：

后续调试几乎不可控
六、merged_text 生成规则（冻结）
6.1 最小整理规则
1. 保留识别文本
2. 去除明显空白噪声
3. 多图按顺序拼接
4. 保留换行结构
5. 不强制补说话人
❌ 明确不做
不做 A/B 角色自动识别
不做语义推断
不做关系分析
不做结构重建优化

👉 原因：

I1 = 草稿生成器，不是文本定稿器
七、错误协议（冻结）
7.1 统一错误结构
{
  "success": false,
  "raw_text": "",
  "merged_text": "",
  "provider": "vision_model_v1",
  "source_type": "image",
  "image_count": 0,
  "need_user_confirm": true,
  "error_message": "错误描述"
}
7.2 必须支持的错误类型
错误类型	描述
图片为空	未上传图片
识别失败	模型失败
无有效文本	识别为空
多图失败	任一失败则整体失败
❗策略说明
第一版：宁可失败，不做脏成功
八、与 I2 的衔接（强制规则）
8.1 唯一合法路径
I1 → I2 → analyze
❗强制约束
禁止：
I1 → analyze
8.2 I2 输入字段
{
  "confirmed_chat_text": "用户确认后的文本"
}

👉 I2 是：

唯一合法分析入口
九、系统边界冻结（极重要）
❌ 不允许修改
/api/v1/analyze
pipeline_orchestrator
rules.py
S2 / S3 / R1 / S5
❌ 不允许行为
OCR 写进 analyze
图片进入 pipeline
跳过 I2
合并接口
✅ 唯一允许扩展
新增 I1 输入节点
十、接口独立性裁决
为什么不能复用 analyze？
问题	后果
输入协议混乱	❌
错误难定位	❌
前端流程耦合	❌
无法替换实现	❌
✅ 正确做法
image-to-text ≠ analyze
十一、阶段结论
本文档冻结的本质
不是在定义一个接口
而是在定义一个“输入层新节点”
一句话总结
I1 = 最薄的图转文草稿节点
I2 = 唯一文本确认出口
analyze = 完全不动
十二、归档说明

建议路径：

/docs/architecture/v3_6_i1_image_to_text_spec.md