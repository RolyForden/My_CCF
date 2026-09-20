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

## D-023

- 日期：2026-09-20
- 阶段：IDEA（导师反馈吸收）
- 决策：旧 FocalInspect-NBV proposal 不进入 baseline。导师指出其“局部放大 + 全局语境 + 选择性蒸馏”主要是在证明组合不 trivial，而非解决已实证的结构性问题；无人机下游验证不能补足方法新颖性。
- 依据：导师完整评价（C 级决策材料）；LASO/GEAL/GLANCE/CMAT 全文与官方代码核验表明，多尺度、global-local fusion、2D-3D transfer 和细粒度几何先验已有直接覆盖。
- 被否决选项：继续给旧 proposal 加模块；先接 FlightBench/Aerial Gym 再寻找 motivation。
- owner：唐卓
- 复查触发条件：出现可量化、可证伪且不能被简单 crop/分辨率解释的根 failure。

## D-024

- 日期：2026-09-20
- 阶段：IDEA（候选 RQ）
- 决策：把“同一几何输入下的 instruction-conditioned counterfactual faithfulness”保留到最小诊断，形成条件式 Proposal v2；旧 global semantic-local precision 路线降为尺度解释对照，不作为主张。Gate 不推进。
- 依据：LASO 官方论文和 loader 显示问题由 object-affordance 组合生成，训练随机问题、测试固定 Question0；相邻 grounding 研究表明语言扰动与反事实重问可揭示 shortcut，但该现象尚未在 LASO/GEAL 上实证。
- 候选 RQ：模型能否对同义问题保持 mask 不变，并在同一 shape 的不同有效 affordance 指令下正确切换 mask？
- 被否决选项：把协议可疑直接写成模型走 shortcut；把 GroundBench/BEACON3D 的结论直接迁移为本任务事实。
- owner：唐卓 + 同学
- 复查触发条件：D0 数据审计和 D1 预训练模型诊断完成后，按 SURVIVE/WEAK/KILL 规则裁决。

## D-025

- 日期：2026-09-20
- 阶段：IDEA（研究对象重置）
- 决策：终止把 CAGE 定位为 `faithfulness evaluation + metrics + paired loss` 方法主线。CAGE 降级为 measurement apparatus，只用于行为 probe、controlled pairs、sensitivity measurement 和替代解释排除。新的候选研究对象是 query information 沿 `q -> E_q -> Fusion -> Z_point -> Decoder -> Mask` 的传播机制及其对 point-level mask switching 的因果作用；正式方法在 D2 通过前保持空白。
- 依据：诊断、指标和通用 loss 是研究工具，不是机制贡献。仅观察层间 representation similarity 也不能定位根因；必须经过 `Behavioural existence -> Representation localization -> Causal intervention -> Mechanism-derived method`，并用 restoration/destruction 的行为后果区分 candidate locus 与决定性机制。
- 优先候选假设：query collapse、fusion attenuation、point-level conditioning failure、decoder dominance；其中 global-to-point query routing / query-part binding failure 仅为优先验证假设，不是结论。
- paired loss 定位：non-mechanistic intervention control。若其完整恢复内部链路与 switching，优先解释为 supervision deficiency；若只改善输出指标而不恢复内部机制，则不能作为正式解法。
- 被否决选项：继续润色 Proposal v2；把 CAGE-Pair/CSM 当主贡献；在机制定位前预设 routing、binding、conditional modulation 或 point-query interaction 方法。
- owner：唐卓 + 同学
- 复查触发条件：D0 证明行为 failure 且排除数据歧义后，才进入 D1；D2 双向定点干预成立后，才允许设计 D3 方法。
