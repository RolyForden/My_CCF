# Decision Log

> 旧方向（PACE-PC、跨模态地点检索、点云退化恢复）的完整决策记录 D-001~D-017 已归档到独立工作空间：
> `Z:\科研总控台opencode-archive\projects\20260902-CCFC选题\DECISIONS.md`
> 本文件只保留**方向演变摘要**与**当前决策**，保持精简可读。旧决策编号不复用。

---

## 方向演变摘要（2026-09）

| 顺序 | 方向 | 结局 | 一句话原因 |
|---|---|---|---|
| 起点 | PACE-PC（点云退化恢复） | 否 | 未过主张级查重与最小反例（D-002） |
| 探索 | 跨模态室内定位 + 候选重排 | 否 | 核心机制（D_i / D_ij / 门控）三重否证 + 题内重构撞车（D-006~D-015） |
| 备选 | 点云退化恢复 / 退化感知地点识别 | 否 | G1 被 ResLPR / LTDNet / LPR-Mate 等覆盖（D-017） |
| 换枝 | FocalAfford（3D affordance + 局部修正蒸馏） | 否（后经 D-022 回归为 FocalInspect-NBV 感知核心） | 任务在快速过时、无人机关联弱；**机制骨架保留** |
| 迁移 | FocalLiDAR / FocalAerial（航空点云分割） | 否 | 组件被 PVD / M2SKD / LGENet 覆盖，G1 弱 |
| 弯路 | FocalNadir-VO（高空俯视单目视觉里程计） | 否（废弃，D-022） | 与后续实际推进脱节 |
| **当前** | **FocalInspect-NBV（任务驱动无人机巡检）** | **主攻** | FocalAfford 感知 + 冻结下游观察验证；RQ 待按导师意见修订 |

**贯穿始终的机制骨架**（源自博士 FocalAfford）：
> 训练期局部精细观察 → 全局结构解释局部 → 局部增量内化 → 推理期保持简单。

---

## D-021

- 日期：2026-09-16
- 阶段：INTAKE（工作空间整理）
- 决策：把已否定方向与旧实验产物（方向坟场、旧方向说明书、旧实验/基线/交接记录、旧 LANDSCAPE/EVIDENCE_LEDGER/LITERATURE_MATRIX/DECISIONS）整体归档到独立工作空间 `Z:\科研总控台opencode-archive\`；主工作空间只保留高频使用内容，结构精简为 `intake/ landscape/ idea/ experiments/ paper/` + 五个核心文件。
- 依据：旧产物优先级降低，不应污染高频工作空间；后续可能让博士通过 git 仓库深度了解情况，需结构可读。
- 被否决选项：留在主仓库内（archive/ 子目录）；只归档坟场与旧实验。
- owner：唐卓
- 复查触发条件：需要回溯旧方向细节时到归档工作空间查阅。

## D-022

- 日期：2026-09-20
- 阶段：IDEA（方向切换）
- 决策：主攻方向由 **FocalNadir-VO（高空俯视单目视觉里程计）** 切换为 **FocalInspect-NBV（任务驱动无人机巡检：FocalAfford 感知 + 冻结下游观察验证）**。FocalNadir-VO 废弃，其立项书与证据链归档至 `Z:\科研总控台opencode-archive\projects\20260902-CCFC选题\FocalNadir-VO_废弃\`。
- 依据：实际讨论的 proposal 为 `FocalInspect-NBV_Research_Report.pdf`（2026-09-17），导师已就该 proposal 提出评价意见（gap 锋利度不足，须重审根问题：分辨率不足 vs 全局语义—局部空间精度的结构性矛盾），团队计划于今日按导师意见修订 FocalInspect-NBV。原 D-020 定的 FocalNadir-VO 已与后续实际推进脱节。
- 待办：按导师意见修订 FocalInspect-NBV 的 RQ（结构性矛盾方向尚未实证，当前为 D 级假设）；重建 landscape 证据账本与文献矩阵（旧 VO 证据已随本决策归档）。
- 被否决选项：继续 FocalNadir-VO；两个方向并行推进。
- owner：唐卓
- 复查触发条件：导师修订意见定稿后，重写 RQ 与 IDEA_CARD，再走选题红队。
