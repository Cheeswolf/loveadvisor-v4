# 《LoveAdvisor V3.6 方案补丁：I1 图转文 Provider 切换为 Qwen-OCR》

---

## 一、补丁性质

```text
技术路线补丁 / 输入层架构修订方案 / V3.6 正式实施补丁
```

---

## 二、补丁结论

```text
I1 主 Provider：Qwen-OCR
I1 备用 Provider：传统 OCR（仅兜底）
```

```text
V3.6 的 I1 节点正式从“传统 OCR 优先”切换为“Qwen-OCR 优先”
```

---

## 三、架构不变部分（冻结）

以下内容严格不允许修改：

* `/api/v1/analyze`
* `rules.py`
* `pipeline_orchestrator.py`
* S2 / S3 / R1 / S5
* 结果页逻辑
* I2 用户确认层（必须保留）

---

## 四、输入链路（修订后）

```text
用户上传截图
→ /api/v1/image-to-text
→ Qwen-OCR
→ merged_text（文本草稿）
→ I2 用户确认
→ confirmed_chat_text
→ /api/v1/analyze
→ 输出结果
```

---

## 五、I1 节点职责

### 5.1 I1 负责

```text
1. 接收图片
2. 调用 Qwen-OCR
3. 提取文本
4. 合并多图
5. 输出 raw_text + merged_text
```

### 5.2 I1 不负责

```text
- 关系分析
- 兴趣判断
- 说话人最终纠正
- 跳过 I2 直接分析
- 文本最终定稿
```

---

## 六、Provider 定义

### 6.1 统一命名

```text
provider = qwen_ocr
```

### 6.2 废弃

```text
mock
vision_model_v1
ocr_space（仅保留兜底）
```

---

## 七、接口设计

### 7.1 接口保持独立

```text
POST /api/v1/image-to-text
```

### 7.2 职责划分

| 接口            | 职责      |
| ------------- | ------- |
| image-to-text | 图片 → 文本 |
| analyze       | 文本 → 分析 |

---

## 八、Qwen-OCR 接入规范

### 8.1 Base URL

```text
https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 8.2 模型

```text
qwen-vl-ocr
```

### 8.3 请求格式

```json
{
  "model": "qwen-vl-ocr",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "请提取图片中的聊天文本，按阅读顺序输出为纯文本草稿，不要解释。"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,......"
          }
        }
      ]
    }
  ]
}
```

---

## 九、I1 输出协议（不变）

```json
{
  "success": true,
  "raw_text": "...",
  "merged_text": "...",
  "provider": "qwen_ocr",
  "source_type": "image",
  "image_count": 1,
  "need_user_confirm": true,
  "error_message": ""
}
```

---

## 十、merged_text 生成规则

```text
- 按识别顺序拼接
- 保留换行
- 去除明显噪声
- 不强行补说话人
- 不做关系推断
```

---

## 十一、错误处理（最小版本）

```text
E1：未上传图片 → 直接返回失败
E2：API调用失败 → 返回错误信息
E3：识别为空 → 返回“未识别到文字”
E4：任意一张失败 → 整体失败
```

---

## 十二、配置项

```text
DASHSCOPE_API_KEY=你的key
QWEN_OCR_MODEL=qwen-vl-ocr
QWEN_OCR_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

---

## 十三、施工边界（强制）

```text
只允许修改：
- image_to_text_service.py
- image_to_text.py
- settings.py

禁止修改：
- analyze
- rules
- pipeline
- S2/S3/R1/S5
```

---

## 十四、MTU 拆分

### MTU-1

```text
接入 Qwen-OCR provider
```

### MTU-2

```text
实现 raw_text / merged_text 输出
```

### MTU-3

```text
单图测试
```

### MTU-4

```text
多图拼接测试
```

---

## 十五、验收标准

```text
1. 截图可返回 merged_text
2. I2 编辑框成功回填
3. 用户可编辑
4. 可进入 analyze
5. 文本路径未受影响
```

---

## 十六、最终结论

```text
V3.6 架构正确
问题在于 I1 Provider 选择错误
```

```text
修订后：
I1 主方案 = Qwen-OCR
I2 = 用户确认
analyze = 保持不变
```

---

## 一句话总结

```text
把“识字工具”换成“可生成聊天草稿的视觉模型”，系统才能真正可用
```
