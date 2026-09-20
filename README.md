# 科研工作区

这是一个轻量的科研协作目录。目标是减少重复文书，把注意力放在三个问题上：研究问题是否真实、最近邻是否已经覆盖、下一项实验能否改变判断。

## 当前项目

- [20260902-CCFC选题](projects/20260902-CCFC选题/README.md)
- 当前方向：language-guided 3D affordance grounding 中 query control 的传播与因果定位
- 当前状态：尚未证明 failure 存在，暂不设计正式方法
- 当前下一步：导师讨论后，先做数据可答性审计，再决定是否运行行为诊断

## 日常用法

进入一个项目时只读：

1. 根目录 [AGENTS.md](AGENTS.md)
2. 项目 `README.md`
3. 本次任务直接相关的论文、代码或实验文件

一次迭代默认只回答：

1. 新发现了什么？
2. 它改变了什么判断？
3. 下一步最小动作是什么？

不再维护阶段机、Gate 编号、证据数量、固定角色回传或每轮 artifact 清单。完整原则见 [轻量工作流](workflow/README.md)。

## 目录

- `projects/`：实际研究项目。每个项目的 `README.md` 是唯一状态入口。
- `docs/`：仍有参考价值的方法、课程和导师经验材料，按需读取。
- `templates/`：仅保留项目、证据、决策和实验四份轻量模板。
- `scripts/`：新建项目和轻量检查。
- `legacy_workflow/`：旧阶段制、Gate、科研内阁和模板，仅供回看，不参与当前工作。
- `source_private/`：私密原始材料，不进入外部服务。

## 新建项目

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\new_topic.ps1 `
  -Name "选题名称" -Venue "候选会议" -Deadline "YYYY-MM-DD"
```

脚本只生成 `README.md`、`EVIDENCE.md` 和 `DECISIONS.md`。实验和论文文件等真正需要时再创建。

## 保留的严谨性

精简的是行政流程，不是研究诚信。引用核验、公平 baseline、数据划分、实验可复现、负结果保留和投稿政策核对仍然必须执行，但只在相关任务发生时记录。
