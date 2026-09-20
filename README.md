# 科研总控台（opencode 科研工作空间）

把 2026-09 的科研方法论课程变成可执行、可检查的研究工作空间。它不承诺“自动发论文”，而是把选题、检索、验证、复现、实验、写作和审稿拆成可检查的阶段，让 opencode 承担高重复工作，让人保留研究判断和责任。

## 当前在做什么

- **当前项目**：[20260902-CCFC选题](projects/20260902-CCFC选题/README.md)
- **主攻方向**：FocalNadir-VO —— 高空俯视无人机单目视觉里程计（训练期平面运动归一化局部细节学习）
- **当前闸门**：`G1 = WEAK+`，须用表0 止损实验决定是否 SURVIVE
- **目标**：CCF-C 会议，2027-03 前投出

> **归档说明**：已否定方向与旧实验产物（PACE-PC、跨模态地点检索、点云退化恢复、FocalAfford / FocalLiDAR / FocalAerial）已移到独立工作空间 `Z:\科研总控台opencode-archive\`，**不在本仓库**。

## 先看什么

1. 当前项目：[20260902-CCFC选题](projects/20260902-CCFC选题/README.md) —— 内含阅读顺序与当前状态
2. 方法论：[可复用科研 SOP](docs/03_可复用科研SOP.md)
3. 博士规则：[博士科研决策规则与经验汇编](docs/08_博士科研决策规则与经验汇编.md)
4. 选题锋利度：[导师选题思路与 gap 锋利度判断](docs/09_导师选题思路与gap锋利度判断.md)
5. 写作术：[全网科研经验汇编](docs/10_全网科研经验汇编.md)
6. 内阁调度：[科研内阁与任务调度](docs/07_科研内阁与任务调度.md)

其余课程资产（材料校订、课程校订稿、Codex 方法剖析、多角色提示词库、PACE-PC 报告审计）在 [`docs/`](docs/)。

## 目录约定

- `projects/`：实际研究项目，每个题目单独存放。项目内结构：`intake/ landscape/ idea/ experiments/ paper/` + `README / STATE.yaml / RESEARCH_CHARTER.md / GATE.md / DECISIONS.md`。
- `docs/`：课程资产、方法论和审计结论。
- `templates/`：每个研究阶段的固定模板。
- `scripts/`：新建选题（`new_topic.ps1`）和完整性检查（`validate_project.ps1`）脚本。
- `workflow/`：跨选题共用的状态与证据规则。
- `.opencode/`：总控台与 5 个 subagent（文献情报 / 数据与基线 / 选题红队 / 工程实验 / 论文与审稿）配置。
- `source_private/`：原始录音转写、截图和私密报告，只在本机保存，不进入版本控制。

## 开始一个新选题

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\new_topic.ps1 -Name "选题名称" -Venue "目标会议" -Deadline "YYYY-MM-DD"
```

脚本会在 `projects/` 下生成独立研究目录。随后让 opencode 先读取该目录的 `RESEARCH_CHARTER.md` 和根目录的 `AGENTS.md`，从当前阶段继续，而不是直接写模型或论文。

## 核心方法

该博士最有价值的能力不是“换模块”，而是把研究限制翻译成一串连续决策：

`约束定义 → 近年态势 → 候选方向 → 反驳与查重 → 邻域迁移 → 代码/数据/算力审计 → 基线复现 → 小规模试验 → 完整实验 → 论证与审稿`

需要删除或改写的做法：“20% 数据失败则全量必败”“全程不需要编码”“换模块就是创新”“先看到指标上涨再倒推动机”。AI 给出的论文名、分数和录取概率都不是证据。

## 使用边界

这套流程可以压缩检索、工程和文书时间，但不能替代：研究问题的真实性、实验公平性、结果复核、引用核验、作者贡献和投稿合规。opencode 是研究执行器与审计助手，不是论文责任主体。
