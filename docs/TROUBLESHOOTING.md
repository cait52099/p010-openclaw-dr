# Deep Research 故障排查

## 常见问题

### EOFError: EOF when reading a line

**问题**: 运行 `smoke_dr.sh` 时出现 `EOFError: EOF when reading a line`

**原因**: 脚本尝试从 stdin 读取输入，但 stdin 已关闭。

**解决方案**:

```bash
# 使用 echo 提供输入
echo "climate change impact on agriculture" | python3 scripts/run_deep_research.py
```

### 非交互模式退出码 2

**问题**: 使用 `--non-interactive` 时收到退出码 2

**原因**: 在非交互模式下，主题需要澄清但无法获取用户输入。

**解决方案**:
- 使用更具体的主题 (>= 20 字符)
- 或移除 `--non-interactive` 标志

### exit(3) 验证失败

**问题**: 运行后收到退出码 3

**原因**: 验证失败，通常是因为:
- paragraphs.jsonl 中某行 cite_ids 为空
- 引用格式不正确

**排查步骤**:
1. 检查 `runs/<run_id>/evidence/verify.json`
2. 检查 `paragraph_without_citation_count` 是否 > 0
3. 检查 `paragraphs_jsonl_cite_ids_passed` 是否为 false

### 澄清失败 (exit 1)

**问题**: 主题需要澄清但用户未回答或回答无效

**原因**:
- 交互模式下用户未提供有效回答
- 回答仍不满足澄清条件

**解决方案**:
- 提供更具体的主题
- 回答所有澄清问题

### 缺少 verify.json

**问题**: `evidence/verify.json` 文件不存在

**原因**: pipeline 未完成 audit 阶段

**解决方案**:
- 重新运行完整 pipeline
- 检查 `logs/pipeline.jsonl` 查看失败的阶段

## 调试技巧

### 查看运行日志

```bash
# 查看 pipeline 日志
cat runs/<run_id>/logs/pipeline.jsonl

# 查看验证详情
cat runs/<run_id>/evidence/verify.json
```

### 检查段落引用

```bash
# 统计缺失引用的段落
grep "paragraph_without_citation_count" runs/<run_id>/final/verification.md

# 检查报告中的引用
grep "(C" runs/<run_id>/final/report.md
```

### 恢复运行

```bash
# 使用已有 run_id 恢复
./scripts/dr --run-id <existing_run_id>
```

## 烟雾测试故障

### Case 2 失败

检查是否正确使用了 `--non-interactive`:

```bash
python3 scripts/run_deep_research.py --non-interactive --runs-dir="./runs"
```

### Case 3 失败

确保澄清问题被正确处理:

```bash
# 检查 clarify.json
cat runs/<run_id>/clarify.json
```

### Case 4 失败

检查所有输出文件是否存在:

```bash
ls -la runs/<run_id>/final/
ls -la runs/<run_id>/evidence/
```

## 性能问题

### Worker 数量过多

默认 worker 数为 5。减少数量可降低资源使用:

```bash
./scripts/dr "topic" --workers 2
```

### 缓存未生效

检查缓存目录:

```bash
ls -la runs/.cache/
```

## 获取帮助

如遇到未列出的问题，请:
1. 查看 `logs/pipeline.jsonl` 了解失败阶段
2. 查看 `final/verification.md` 了解验证详情
3. 提交 Issue 并附上相关日志
