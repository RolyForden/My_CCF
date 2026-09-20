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
| 换枝 | FocalAfford（3D affordance + 局部修正蒸馏） | 否（不再主攻） | 任务在快速过时、无人机关联弱；**机制骨架保留** |
| 迁移 | FocalLiDAR / FocalAerial（航空点云分割） | 否 | 组件被 PVD / M2SKD / LGENet 覆盖，G1 弱 |
| **当前** | **FocalNadir-VO（高空俯视单目视觉里程计）** | **主攻验证** | gap 真实且新（arXiv 2608.18632），专业匹配；G1=WEAK+，待表0 |

**贯穿始终的机制骨架**（源自博士 FocalAfford）：
> 训练期局部精细观察 → 全局结构解释局部 → 局部增量内化 → 推理期保持简单。

---

## D-018

- 日期：2026-09-14
- 阶段：IDEA
- 决策：不再把 FocalAfford（语言引导 3D affordance）作为主攻方向，转向更贴合专业与约束的纯三维/无人机问题。保留其机制骨架，删除语言、多模态、置信度、优势权重。
- 依据：三维 affordance 领域 2025-2026 向开放世界 / MLLM / 视频交互快速演进；LASO+GEAL 上的局部蒸馏到 2027 年易被视为旧 benchmark 上的局部增量；无人机联系牵强。
- 被否决选项：继续深挖 FocalAfford；新增多模态/MLLM 创新。
- owner：唐卓 + 博士
- 复查触发条件：FocalNadir-VO 表0 失败时回退。

## D-019

- 日期：2026-09-15
- 阶段：IDEA → LANDSCAPE
- 决策：FocalAerial（航空点云细长结构分割）经主张级查重判定 **G1=WEAK**；数据侧锁定 **DALES 为最稳主数据**（G2+G3 均过，SPT 提供完整训练评测）；ECLAIR 仅作评测参照；STPLS3D / UAVScenes / OpenGF 出局。
- 依据：文献情报（PVD/M2SKD/PatchTeacher/PointDistiller/LGENet 全文核验，E-045~E-054）+ 数据与基线核验（DALES 29/11 冻结划分、8 类含 power lines/poles/fences）。
- 关键纠错：PatchTeacher(AAAI 2024)=半监督三维**检测**（非分割）；PointDistiller=三维**检测**、CVPR **2023**；EZ-SP 存在但 venue 错；**DALES 2 不存在**。
- 被否决选项：UAVScenes 作主训练线（官方 baseline 未发布，G3 FAIL）；直接开工通用 FocalLiDAR。
- owner：唐卓 + 博士
- 复查触发条件：FocalALS 作为 CCF-C 保底时再启动。

## D-020

- 日期：2026-09-16
- 阶段：IDEA（立项决策）
- 决策：改定 **FocalNadir-VO** 为主攻方向——高空俯视无人机单目视觉里程计，训练期以全图主导平面运动解释原始分辨率局部非平面残差视差。判定 **G1=WEAK+**，须先用表0（A0–A4 / B0–B3）决定是否 SURVIVE，不得直接开发。
- 依据：博士机制骨架的任务原生几何迁移；2026-08 高空俯视单目 SLAM 评测（arXiv 2608.18632）记录俯视退化、垂向误差、长轨迹形变；G0/G2/G3/G4/G5 均 PASS。
- 已知弱点：方法层创新弱于 FocalAfford（删去优势加权蒸馏，换为共享权重辅助损失）；gap 属"场景/现象型"而非"方法缺陷型"，须在表0 与主张级查重中锚死 DPVO 的具体机制缺陷。
- 被否决选项：普通 LiDAR 里程计/去畸变（已被覆盖）；UAVScenes 主训练线（G3 FAIL）；VLN/VLA/WAM。
- owner：唐卓 + 同学 + 博士
- 复查触发条件：表0 SURVIVE → 正式开发；WEAK → 一次最小修正后复验；KILL → 回退 FocalALS。

## D-021

- 日期：2026-09-16
- 阶段：INTAKE（工作空间整理）
- 决策：把已否定方向与旧实验产物（方向坟场、旧方向说明书、旧实验/基线/交接记录、旧 LANDSCAPE/EVIDENCE_LEDGER/LITERATURE_MATRIX/DECISIONS）整体归档到独立工作空间 `Z:\科研总控台opencode-archive\`；主工作空间只保留高频使用内容，结构精简为 `intake/ landscape/ idea/ experiments/ paper/` + 五个核心文件。
- 依据：旧产物优先级降低，不应污染高频工作空间；后续可能让博士通过 git 仓库深度了解情况，需结构可读。
- 被否决选项：留在主仓库内（archive/ 子目录）；只归档坟场与旧实验。
- owner：唐卓
- 复查触发条件：需要回溯旧方向细节时到归档工作空间查阅。
