# Deep Research JSON Schema

## clarify.json

澄清数据文件，位于 `runs/<run_id>/clarify.json`。

```json
{
  "status": "string - 状态 (pending/clarified/failed)",
  "questions": ["string - 澄清问题列表"],
  "answers": ["string - 用户回答列表"],
  "failure_reason": "string|null - 失败原因"
}
```

### 示例

```json
{
  "status": "clarified",
  "questions": [
    "Could you provide more context about 'ai'? What specifically would you like to learn?",
    "Your topic seems vague. Could you be more specific about what you mean?",
    "What depth of research do you need? (brief overview / comprehensive analysis)"
  ],
  "answers": ["artificial intelligence trends", "2024", "comprehensive analysis"],
  "failure_reason": null
}
```

### 失败时

```json
{
  "status": "failed",
  "questions": [
    "Could you provide more context about 'ai'?"
  ],
  "answers": [],
  "failure_reason": "No clarification provided"
}
```

## paragraphs.jsonl

段落草稿文件，位于 `runs/<run_id>/drafts/paragraphs.jsonl`。

每行是一个有效的 JSON 对象，表示一个段落。

### 格式

```json
{
  "text": "string - 段落文本",
  "cite_ids": ["C001", "C002", ...] - 引用 ID 数组
}
```

### 约束

- `cite_ids` 数组不能为空
- 每个 cite_id 格式: `C` + 3位数字 (如 `C001`, `C002`)

### 示例

```json
{"text": "Key point from Source 0", "cite_ids": ["C001"]}
{"text": "Key point from Source 1", "cite_ids": ["C002"]}
{"text": "Key point from Source 2", "cite_ids": ["C003"]}
```

## verify.json

验证结果文件，位于 `runs/<run_id>/evidence/verify.json`。

### 格式

```json
{
  "stage": "string - 当前阶段 (audit/verify)",
  "status": "string - 状态 (completed/failed)",
  "verified_claims_count": "number - 已验证声明数",
  "single_source_claims_count": "number - 单来源声明数",
  "conflicts_count": "number - 冲突数",
  "total_paragraphs": "number - 总段落数",
  "paragraph_without_citation_count": "number - 缺失引用的段落数",
  "paragraph_end_citation_passed": "boolean - 段落末尾引用检查",
  "paragraphs_jsonl_cite_ids_passed": "boolean - cite_ids 格式检查",
  "citations_found": "number - 找到的引用数",
  "passed": "boolean - 综合通过状态"
}
```

### 示例

```json
{
  "stage": "audit",
  "status": "completed",
  "verified_claims_count": 3,
  "single_source_claims_count": 3,
  "conflicts_count": 0,
  "total_paragraphs": 3,
  "paragraph_without_citation_count": 0,
  "paragraph_end_citation_passed": true,
  "paragraphs_jsonl_cite_ids_passed": true,
  "citations_found": 3,
  "passed": true
}
```

## citations.json

引用数据文件，位于 `runs/<run_id>/evidence/citations.json`。

### 格式

```json
[
  {
    "cid": "C001",
    "url": "string - 来源 URL",
    "title": "string - 来源标题",
    "locator": "string - 定位符",
    "fetched_at": "ISO timestamp",
    "quote_hash": "string | null",
    "local_path": "string | null"
  }
]
```

### 示例

```json
[
  {
    "cid": "C001",
    "url": "https://example.com/0",
    "title": "Source 0",
    "locator": "https://example.com/0",
    "fetched_at": "2026-02-26T21:26:58.536923",
    "quote_hash": null,
    "local_path": null
  }
]
```

## pipeline.jsonl

阶段转换日志，位于 `runs/<run_id>/logs/pipeline.jsonl`。

每行是一个 JSON 对象，记录一个阶段的状态转换。

### 格式

```json
{
  "timestamp": "ISO timestamp",
  "run_id": "string",
  "stage": "string - 阶段名称",
  "status": "string - started/completed/failed",
  "details": {
    "success": "boolean - 成功标志",
    "error": "string - 错误信息 (可选)"
  }
}
```

### 示例

```json
{"timestamp": "2026-02-26T21:26:58.123456", "run_id": "demo_run", "stage": "intake", "status": "started", "details": {}}
{"timestamp": "2026-02-26T21:26:58.234567", "run_id": "demo_run", "stage": "intake", "status": "completed", "details": {"success": true}}
{"timestamp": "2026-02-26T21:26:58.345678", "run_id": "demo_run", "stage": "plan", "status": "started", "details": {}}
```

## plan.json

研究计划文件，位于 `runs/<run_id>/logs/plan.json`。

### 格式

```json
{
  "workers": "number - worker 数量",
  "depth": "string - 研究深度 (brief/medium/deep)",
  "budget": "number - 来源预算",
  "lang": "string - 输出语言",
  "plan": {
    "queries": ["string[] - 查询列表"],
    "sources": ["string[] - 来源类型"],
    "estimated_sources": "number - 预估来源数",
    "depth": "string"
  }
}
```

### 示例

```json
{
  "workers": 5,
  "depth": "medium",
  "budget": 10,
  "lang": "en",
  "plan": {
    "queries": ["climate change impact on agriculture"],
    "sources": ["web", "academic"],
    "estimated_sources": 50,
    "depth": "medium"
  }
}
```
