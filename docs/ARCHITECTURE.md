# Deep Research 架构设计

## 概述

Deep Research 是一个自主研究 pipeline，具有验证和缓存功能。

## 状态机阶段

```
intake -> plan -> harvest -> fetch -> extract -> verify -> write -> audit -> cache
```

### 阶段说明

| 阶段 | 描述 |
|------|------|
| `intake` | 接收并验证输入，保存澄清数据 |
| `plan` | 创建研究策略，生成查询计划 |
| `harvest` | 发现相关 URL 和来源 |
| `fetch` | 从来源获取内容 (带缓存) |
| `extract` | 提取关键信息 |
| `verify` | 验证引用完整性 |
| `write` | 生成最终报告 |
| `audit` | 最终审计验证 |
| `cache` | 完成缓存 |

## 澄清门控逻辑

### 触发条件

主题需要澄清当满足以下任一条件:

1. **主题长度 < 20 字符**: 返回澄清问题
2. **包含模糊术语**: `it`, `this`, `that`, `they`, `them`, `something`, `anything`, `what`, `how`
3. **短缩写列表**: `ai`, `ml`, `dl`, `llm`, `nlp`, `cv`, `ag`, `ar`, `vr`, `mr`, `web`, `app`, `db`, `os`, `api`

### 澄清流程

```
用户输入 -> needs_clarification() 检查
    |
    +-- False --> 继续 pipeline
    |
    +-- True --> generate_questions() 生成问题
        |
        +-- 交互模式: 等待用户回答
        +-- 非交互模式: exit(2)
```

### 退出码对应

| 退出码 | 场景 |
|--------|------|
| 0 | 成功完成 |
| 1 | 澄清失败 (用户未回答/回答无效) |
| 2 | 非交互模式下需要澄清 |
| 3 | 验证失败 (引用检查未通过) |

## 组合通过逻辑

最终 `passed` 状态由多个检查组合决定:

```python
# verify.json 中的 passed 逻辑
passed = (
    report_passed and                          # 报告无缺失引用段落
    paragraphs_jsonl_cite_ids_passed and       # paragraphs.jsonl cite_ids 有效
    paragraph_end_citation_passed               # 每段末尾有引用
)
```

### 各检查项

1. **report_passed**: 报告每段以引用结尾
2. **paragraphs_jsonl_cite_ids_passed**: paragraphs.jsonl 每行有有效 cite_ids
3. **paragraph_end_citation_passed**: 段落末尾有引用 (paragraph_without_citation_count = 0)

## 模块说明

### state_machine.py

核心编排器，管理 8 阶段 pipeline 执行。

关键类:
- `StateMachine`: 主状态机
- `RunState`: 运行状态容器
- `Stage`: 阶段枚举

### clarify.py

澄清门控模块。

关键类:
- `Clarifier`: 澄清逻辑

关键方法:
- `needs_clarification(topic)`: 判断是否需要澄清
- `generate_questions(topic)`: 生成澄清问题

### verify.py

验证模块。

关键类:
- `Verifier`: 验证逻辑

关键方法:
- `verify_report(report_path)`: 验证报告引用
- `verify_paragraphs_jsonl(paragraphs_path)`: 验证 paragraphs.jsonl

### worker.py

并发工作池。

### citations.py

引用管理器。

### cache.py

缓存管理器，支持运行恢复。

## 数据流

```
用户输入
    |
    v
[澄清检查] ---- 需要澄清?
    |
    v
[状态机] -- 执行 8 阶段
    |
    +-> intake: 保存 clarify.json
    +-> plan: 生成计划
    +-> harvest: 生成 URL
    +-> fetch: 获取内容 (缓存检查)
    +-> extract: 提取信息
    +-> verify: 生成 paragraphs.jsonl
    +-> write: 生成 report.md
    +-> audit: 验证并生成 verification.md
    |
    v
输出文件
```

## 扩展点

各阶段方法可被覆盖以实现自定义逻辑:

```python
class CustomStateMachine(StateMachine):
    def _stage_harvest(self, state: RunState) -> bool:
        # 实现真实 harvest 逻辑
        pass
```
