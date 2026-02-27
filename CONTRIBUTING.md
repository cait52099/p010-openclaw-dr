# Contributing to Deep Research

## 开发环境设置

```bash
# 克隆仓库
git clone <repo-url>
cd clawd

# 安装依赖 (如需要)
# pip install -r requirements.txt
```

## 运行测试

### 烟雾测试

运行完整的 5 案例门控 + 1 回归测试:

```bash
bash scripts/smoke_dr.sh
```

测试案例:
1. **Case 1**: 无主题交互模式成功 (exit 0)
2. **Case 2**: 无主题非交互模式 (exit 2)
3. **Case 3**: 模糊主题失败 (exit 1)
4. **Case 4**: 正常主题成功 (exit 0)
5. **Case 5**: 验证失败 (exit 3)
6. **Regression**: verify.json 结构验证

## 提交 Pull Request

1. Fork 本仓库
2. 创建功能分支: `git checkout -b feature/your-feature`
3. 进行修改并确保烟雾测试通过
4. 提交提交信息: `git commit -m 'Add feature...'`
5. 推送到分支: `git push origin feature/your-feature`
6. 打开 Pull Request

## 接受标准

提交前请确保:

- [ ] `bash scripts/smoke_dr.sh` 全部通过
- [ ] 新功能有对应的测试案例
- [ ] 代码符合现有风格
- [ ] 文档已更新 (如需要)

## 问题排查

详见 [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
