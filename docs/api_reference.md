# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json`

## 接口列表

### 1. 健康检查

```
GET /api/health
```

**响应**：
```json
{"status": "ok", "service": "审思明辨-智判法案双擎系统"}
```

---

### 2. 对话式法律问答

```
POST /api/chat
```

**请求体**：
```json
{
  "query": "上班途中发生车祸，能认定为工伤吗？",
  "session_id": "user_001"
}
```

**响应**：
```json
{
  "answer": "根据《工伤保险条例》第十四条...",
  "related_laws": [
    {"title": "工伤保险条例", "publisher": "国务院", "id": "xxx"}
  ],
  "related_cases": [
    {"title": "某工伤认定案", "court": "北京市中级人民法院", "date": "2023-05-10"}
  ],
  "session_id": "user_001"
}
```

---

### 3. 类案检索

```
POST /api/case/search
```

**请求体**：
```json
{
  "keywords": ["劳动合同", "违法解除"],
  "page_no": 1,
  "page_size": 5,
  "court_level": ["1", "2"]
}
```

---

### 4. 法条检索

```
POST /api/law/search
```

**请求体**：
```json
{
  "keywords": ["房屋买卖合同纠纷"],
  "field_name": "semantic",
  "page_no": 1,
  "page_size": 5
}
```

---

### 5. 法规详情

```
GET /api/law/detail?law_id=<law_id>
```

---

### 6. 诉讼策略推演

```
POST /api/strategy/analyze
```

**请求体**：
```json
{
  "complaint_text": "原告XXX诉称...",
  "case_type": "civil"
}
```

**响应**：
```json
{
  "case_type": "civil",
  "report": "## 一、案情要素提炼\n...",
  "export_ready": true
}
```

---

### 7. 导出至腾讯文档

```
POST /api/export/doc
```

**请求体**：
```json
{
  "title": "劳动争议案件分析报告",
  "content": "## 报告内容..."
}
```
