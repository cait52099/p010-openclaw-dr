# Deep Research Release Push Guide

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

## 概述

本指南用于将 `dr_mode_public/` 目录作为独立 GitHub 仓库发布。

## 前置条件

1. 已安装 `gh` CLI 并完成认证
2. 已在 GitHub 创建空仓库（或使用下方命令自动创建）

## Push 命令

### 方式一：使用 gh CLI（推荐）

```bash
cd dr_mode_public

# 1. 初始化 git（如果还没有）
git init

# 2. 添加所有文件
git add .

# 3. 创建初始提交
git commit -m "Deep Research MVP v1.0.0"

# 4. 创建仓库并推送（首次）
gh repo create deep-research-mvp --public --source=. --push

# 或已存在仓库时：
git remote add origin https://github.com/<username>/deep-research-mvp.git
git push -u origin main
```

### 方式二：使用 SSH

```bash
cd dr_mode_public

git init
git add .
git commit -m "Deep Research MVP v1.0.0"

# 使用 SSH 方式创建并推送
gh repo create deep-research-mvp --public --source=. --push --remote=ssh

# 或手动添加 SSH remote
git remote add origin git@github.com:<username>/deep-research-mvp.git
git push -u origin main
```

## 推送前检查

### 1. 确认目录干净

```bash
cd dr_mode_public

# 确认没有运行时产物
ls -la

# 确认没有 .omc, __pycache__, runs
find . -name ".omc" -o -name "__pycache__" -o -name "runs" | head
```

### 2. 敏感信息扫描

默认扫描**仅代码文件**（.py），排除文档：

```bash
cd dr_mode_public

# 扫描 API keys（仅 Python 代码）
grep -r "sk-" --include="*.py" . 2>/dev/null | grep -v "grep" || echo "OK: No API keys"
grep -r "ghp_" --include="*.py" . 2>/dev/null | grep -v "grep" || echo "OK: No GitHub tokens"
grep -r "BEGIN PRIVATE KEY" --include="*.py" . 2>/dev/null | grep -v "grep" || echo "OK: No private keys"

# 全文件扫描（谨慎使用，文档示例可能命中）
# grep -r "sk-" . 2>/dev/null | grep -v "grep"
```

**注意**：文档（docs/, notes/）中的示例可能包含 `sk-xxx` 等字面量用于说明目的，不含真实凭证。

## 本地验证

推送前可运行 smoke test：

```bash
cd dr_mode_public
bash scripts/smoke_dr.sh
```

预期输出：`=== All Smoke Tests PASSED ===`

## 发布后

1. 在 GitHub 仓库页面添加 Release
2. 填写版本号和 Release Notes（参考 `notes/RELEASE_NOTES_v1.0.0.md`）
3. 附件可添加 demo_run 产物：
   ```bash
   python3 scripts/make_demo_run.py
   ```
