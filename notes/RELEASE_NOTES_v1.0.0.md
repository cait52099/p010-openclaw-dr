# Deep Research v1.0.0 Release Notes

## 发布日期

2026-02-26

## 概述

Deep Research v1.0.0 是一个自主研究 pipeline，具有验证和缓存功能。

## 新特性

### 核心功能

- **8 阶段研究 Pipeline**: intake -> plan -> harvest -> fetch -> extract -> verify -> write -> audit -> cache
- **澄清门控**: 自动检测模糊主题并要求澄清
- **段落级引用**: 每段必须以引用结尾 (C001, C002...)
- **验证机制**: 自动验证引用完整性
- **缓存与恢复**: 支持中断后恢复运行

### 组件

- **StateMachine**: 8 阶段 pipeline 编排
- **Clarifier**: 模糊主题澄清
- **WorkerPool**: 并发工作池 (默认 5 workers)
- **CitationManager**: 引用管理
- **Verifier**: 引用验证
- **CacheManager**: 内容缓存

### CLI

- Unix: `./scripts/dr`
- Windows: `.\scripts\dr.ps1`
- Python API: `from deep_research import StateMachine`

### 测试

- 烟雾测试脚本: `bash scripts/smoke_dr.sh`
- 5 案例门控 + 1 回归测试

## 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 成功 |
| 1 | 澄清失败 |
| 2 | 非交互模式下需要澄清 |
| 3 | 验证失败 |

## 已知限制

### MVP 限制

1. **Mock 实现**: 以下阶段使用模拟实现
   - `harvest`: 生成示例 URL
   - `fetch`: 返回模拟内容
   - `extract`: 生成模拟关键点

2. **验证限制**:
   - 仅验证引用格式和位置
   - 不验证引用内容真实性
   - 不检测冲突声明

3. **澄清限制**:
   - 最多 3 个澄清问题
   - 简单字符串匹配检测模糊术语

### 未来计划

- 集成真实搜索 API
- 集成真实网页抓取
- 引用内容真实性验证
- 冲突声明检测
- 多语言支持增强

## 依赖

- Python 3.12+
- 标准库: `json`, `pathlib`, `concurrent.futures`, `re`, `datetime`

## 升级说明

v1.0.0 是首个正式版本，无升级指南。

## Release Workflow (IMPORTANT)

Follow this exact order:

1. Run smoke test in MAIN CLAWD DIR (NOT in dr_mode_public):
   ```bash
   cd /path/to/clawd
   bash scripts/smoke_dr.sh
   ```

2. After smoke passes, export clean public repo:
   ```bash
   bash scripts/export_public_repo.sh
   ```

3. Verify dr_mode_public is clean (run inside dr_mode_public):
   ```bash
   cd dr_mode_public
   find . -name runs -o -name __pycache__ -o -name .omc -o -name "*.pyc"
   # Should return NOTHING
   ```

4. If smoke test needed again: re-run export (step 2)

5. Push to GitHub:
   ```bash
   cd dr_mode_public
   git init
   git add .
   git commit -m "v1.0.0"
   gh repo create deep-research-mvp --public --source=. --push
   ```

## GitHub Push Commands

### 方式一：使用 gh CLI

```bash
cd dr_mode_public

# 1. 认证（如未认证）
gh auth login

# 2. 创建仓库（首次）
gh repo create deep-research-mvp --public --source=. --push

# 或已存在仓库
git remote add origin https://github.com/<username>/deep-research-mvp.git
git push -u origin main
```

### 方式二：使用 SSH

```bash
cd dr_mode_public

# 1. 确保 SSH key 已配置
# 2. 创建仓库
gh repo create deep-research-mvp --public --source=. --push --remote=ssh

# 或使用 SSH URL
git remote add origin git@github.com:<username>/deep-research-mvp.git
git push -u origin main
```

### 推送前敏感扫描

在推送前，运行以下命令确保无敏感信息：

```bash
cd dr_mode_public

# 扫描代码文件（排除 docs/ 和 notes/，因为示例可能包含 token pattern）
grep -r "sk-" --include="*.py" . 2>/dev/null | grep -v "grep" | head -5 || echo "OK: No API keys in Python code"
grep -r "ghp_" --include="*.py" . 2>/dev/null | grep -v "grep" | head -5 || echo "OK: No GitHub tokens in Python code"
grep -r "BEGIN PRIVATE KEY" --include="*.py" . 2>/dev/null | grep -v "grep" | head -5 || echo "OK: No private keys in Python code"
grep -r "Bearer " --include="*.py" . 2>/dev/null | grep -v "grep" | head -5 || echo "OK: No bearer tokens in Python code"

# 检查 git status
git status
```

注意：敏感扫描以代码文件为主。文档（docs/、notes/）中的示例可能包含 `sk-xxx` 等字面量用于说明目的，不含真实凭证。

### 生成 Demo Run

```bash
# 生成 demo_run 产物（可选）
python3 scripts/make_demo_run.py
```

## 贡献者

感谢所有参与测试和反馈的贡献者。
