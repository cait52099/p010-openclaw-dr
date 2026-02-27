## Install (local)

```bash
./install.sh --local --prefix "$HOME/.local/bin"
```

## Run

```bash
dr "your topic"
```

## Optional: /dr shortcut (zsh)

```bash
bash scripts/enable_dr_slash.sh --shell zsh
source ~/.zshrc
/dr "your topic"
```

> bash does not support `/dr` alias. Use `drs "your topic"` after enabling bash shortcut.
# Deep Research (深度研究)

> 自主研究 pipeline，内置验证和缓存机制

## 特性

- **8 阶段研究 pipeline**: intake -> plan -> harvest -> fetch -> extract -> verify -> write -> audit -> cache
- **澄清门控**: 自动检测模糊主题（<20字符），要求用户澄清（最多3个问题）
- **段落级引用**: 每段必须以引用结尾 (C001, C002...)
- **并发工作池**: 默认 5 个 worker
- **缓存与恢复**: 支持中断后恢复运行
- **验证机制**: 自动验证引用完整性
- **Combined Passed**: 单一真值（report通过 AND paragraphs.jsonl通过 AND paragraph_without_citation_count=0）

## 快速开始

```bash
# 运行烟雾测试
bash scripts/smoke_dr.sh

# 生成 demo_run（可选，用于预览产物结构）
python3 scripts/make_demo_run.py

# 基本用法
./scripts/dr "人工智能发展趋势 2024"

# 指定参数
./scripts/dr "量子计算应用" --depth deep --workers 10
```

## 退出码

> **重要发布流程**：详见 [RELEASE_PUSH.md](./RELEASE_PUSH.md)

| 退出码 | 含义 | 场景 |
|--------|------|------|
| 0 | 成功 | 研究完成，报告已生成 |
| 1 | 错误 | 运行异常（网络、API等） |
| 2 | 需要澄清 | 非交互模式，主题模糊（显示≤3问题） |
| 3 | 验证失败 | pipeline完成但验收未通过（combined_passed=false） |

### Exit(2) 澄清流程

当主题不足20字符时触发：
```
$ ./scripts/dr "ai" --non-interactive
Deep Research - Clarification Required
========================================
Topic: ai

Please clarify your topic by answering:
  1. What specific topic would you like to research?
  2. What aspect or angle are you interested in?
  3. What is the purpose of this research?
```
澄清后自动继续运行。

### Exit(3) 验证失败

当验证失败时触发（smoke Case5 证明）：
- `paragraph_without_citation_count > 0` → exit(3)
- `paragraphs.jsonl` 中 `cite_ids` 为空 → exit(3)
- `combined_passed = false` → exit(3)

## 扩展：OpenClaw 全文贴回

本项目可集成到 OpenClaw 编排器，实现 `/dr` 命令的全文贴回：

### 命令示例

```
/dr 人工智能发展趋势 2024
```

### 处理流程

1. **Exit(0) 成功**: 读取 `runs/<run_id>/final/report.md`，按 channel 限制（3500字符）分段发送
2. **Exit(2) 澄清**: 发送澄清问题，等待用户回答后继续
3. **Exit(3) 验证失败**: 发送 `verification.md` 全文 + 重试建议

### 集成方式

详见 `docs/OPENCLAW_DR_FULL_REPLY.md`

## 输出结构

```
runs/<run_id>/
├── final/
│   ├── report.md           # 带引用的研究报告
│   └── verification.md     # 验证结果
├── evidence/
│   ├── citations.json       # 引用数据
│   └── verify.json          # 验证详情
├── drafts/
│   └── paragraphs.jsonl     # 段落草稿
├── logs/
│   ├── pipeline.jsonl       # 阶段转换日志
│   └── plan.json           # 研究计划
└── clarify.json            # 澄清问答 (如有)
```

## 配置选项

| 选项 | 默认值 | 描述 |
|------|--------|------|
| `--workers` | 5 | 并发 worker 数量 |
| `--depth` | medium | 研究深度 (brief/medium/deep) |
| `--budget` | 10 | 来源数量预算 |
| `--lang` | en | 输出语言 |
| `--runs-dir` | ./runs | 运行目录 |

## Python API

```python
from deep_research import StateMachine

sm = StateMachine(
    runs_dir="./runs",
    workers=5,
    depth="medium",
    budget=10,
    lang="en",
)

state = sm.run(topic="人工智能发展趋势 2024")
```

## 项目结构

```
deep_research/
├── __init__.py          # 模块入口
├── state_machine.py     # 8 阶段 pipeline 编排
├── clarify.py           # 模糊主题澄清
├── worker.py            # 并发工作池
├── citations.py         # 引用管理器
├── verify.py            # 引用验证
└── cache.py             # 内容缓存
```
