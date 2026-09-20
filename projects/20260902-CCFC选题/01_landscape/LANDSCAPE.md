# LANDSCAPE — LiDAR/点云 3D 感知 · 鲁棒恢复与退化

- 生成日期：2026-09-02
- 阶段：LANDSCAPE（文献情报专项）
- 证据口径：本文件所有「已核实事实」链接到 `EVIDENCE_LEDGER.md` 的条目 ID；所有判断均标注证据等级，未读全文处标注为推断（D）或待验证，不以论文数量等价趋势。
- 核验范围：近 3 年（2023–2026）+ 少量 2021/2022 经典锚点；官方来源 DBLP（dblp.uni-trier.de）、OpenReview、OpenAlex、CVF openaccess（详见 EVIDENCE_LEDGER「核验限制说明」）。

## 0. 检索与核验结论（一句话）

主方向「点云鲁棒恢复/退化」近三年正在从**单任务（补全/去噪/上采样各自为战）**向**统一恢复（unified restoration under degradation）**收敛；代表性证据是 SuperPC（CVPR 2025，四任务统一，E-002）、PQDT（2026 预印本，统一恢复，E-004）、DWCNet（2025，去噪+补全联合，E-006）、PointMAC（NeurIPS 2025，测试时自适应补全，E-003）。次方向「退化下 SLAM」存在可复用的开源退化仿真框架（E-009）。

## 1. 三年时间线（按子方向）

### 1.1 补全（completion）

- 起点（窗口外锚点，E-010）：PoinTr（ICCV 2021，geometry-aware transformer）、SnowflakeNet（ICCV 2021，雪花点反卷积）、SeedFormer（ECCV 2022，patch seeds）。
- 2023：AdaPoinTr（TPAMI 2023，自适应几何感知 transformer）；「Learning Point Cloud Completion without Complete Point Clouds: A Pose-Aware Approach」（ICCV 2023，弱监督/无完整真值方向，L-020）。
- 2025：PointMAC（NeurIPS 2025，meta-auxiliary 测试时自适应补全，E-003）；SuperPC（CVPR 2025，四任务统一，E-002）。
- 2026：PQDT（arXiv 预印本，统一恢复含补全，E-004）。
- 已解决问题：合成数据（ShapeNet/PCN 类）上的单任务补全，已有成熟 SOTA 与公开代码（PoinTr/SeedFormer 等，E-010，代码存在为领域共识但本批未逐一核 GitHub）。
- 仍存在的可测失败（D，待验证）：对**真实传感器退化/复合退化**的补全鲁棒性；测试时分布漂移；未见腐蚀/噪声组合的泛化（PointMAC 评审明确指出静态推理的局限，E-003）。

### 1.2 去噪（denoising）

- 起点：PointFilterNet（TCSVT 2023，filtering network，L-017）。
- 2025：Point-DAE（TNNLS 2025，自监督去噪自编码器，L-018）。
- 2026：SIMPC（arXiv 2026，无监督 mirror-point consistency，L-019）。
- 已解决问题：单腐蚀（高斯噪声）下的点云去噪。
- 仍存在的可测失败（D）：真实传感器噪声（非高斯、非均匀、强度耦合）下的去噪；去噪与补全/上采样的联合（DWCNet 试图合并，E-006，但为期刊且我只核到元数据）。

### 1.3 上采样 / 超分（upsampling）

- 起点：PU-GCN（CVPR 2021，图卷积上采样，E-010）。
- 2024：RepKPU（CVPR 2024，kernel point 表示+形变，L-015）；S3U-PVNet（CVIU 2024，point-voxel + 自监督任意倍率，L-016）。
- 已解决问题：干净合成输入上的稠密上采样。
- 仍存在的可测失败（D）：稀疏/带噪输入上的上采样；与退化恢复耦合。

### 1.4 退化恢复 / 鲁棒恢复（unified restoration under degradation）

- 这是主方向里最新、最接近「复合退化」的聚类，近两年才成形：
  - 2025：SuperPC（CVPR 2025，补全+上采样+去噪+着色四任务统一，E-002）；DWCNet（Computers & Graphics 2025，corruption 下去噪+补全联合，E-006）。
  - 2026：PQDT（arXiv 预印本，Pseudo-Query Dual Transformer 统一恢复，显式处理 completion+deformation+denoising 组合，E-004）。
  - 相邻 2D 线索：ZFusion（ICCV 2025，图像盲超分中的组合零样本退化学习，E-005，非点云）。
- 已解决问题：单模型同时处理多类退化的**可行性**已被证明（E-002/E-004 摘要明确声明）。
- 仍存在的可测失败（这是候选创新位点，但均为 D 级待验证）：
  - 「复合退化是否存在可学习的偏序」——无任何已核证据支持，纯假设（对应 PACE-PC 立项闸门，见 `docs/05`）。
  - 统一模型在**未见退化组合/顺序**上的泛化。
  - 各统一工作的**代码是否公开**尚未核验（E-002/E-004 的 code_url 为空）。

### 1.5 退化下 SLAM / 定位导航（次方向）

- 2022：Recognition of Degradation Scenarios for LiDAR SLAM（ROBIO 2022，E-011）。
- 2025：Degradation-Aware LiDAR-Thermal-Inertial SLAM（RA-L 2025，E-011）；「Sensor-Aware Phenomenological Framework for Lidar Degradation Simulation and SLAM Robustness Evaluation」（arXiv 2512.08653，E-009，声明开源 + Docker/ROS + 4 级 severity + 结构化 dropout/FoV/噪声/遮挡/稀疏化/运动畸变）。
- 已解决问题：给出了可复现、物理可解释的 LiDAR 退化仿真与 SLAM 压力测试框架（E-009）。
- 仍存在的可测失败（D）：真实退化下 SLAM 的端到端鲁棒提升；仿真退化到真实域的迁移。

## 2. 各子方向操作属性评估

> 以下「数据/代码成熟度」「进入成本」「单卡复现难度」均为基于 B 级元数据/摘要的方向性判断（D），未读全文、未实测显存/墙钟，进入 BASELINE 前必须由「数据与基线」专项实测确认。链接证据见各括号。

| 子方向 | 数据/代码成熟度 | 进入成本 | 同质化程度 | 单卡复现难度 | 判断依据 |
|---|---|---|---|---|---|
| 补全（单任务） | 高：公开基准+公开代码（PoinTr/SeedFormer 等） | 低 | **高**（大量换模块拼接） | 低 | E-010 |
| 去噪（单任务） | 中高 | 低 | 中高 | 低 | L-017/018/019 |
| 上采样（单任务） | 中高 | 低 | 中高 | 低 | E-010, L-015/016 |
| 退化恢复（统一/复合） | 低-中：论文新，代码未核 | 中 | **低**（窗口尚新） | 未知（未实测） | E-002/004/006 |
| 退化下 SLAM | 中：仿真框架开源（E-009），但端到端工程重 | **高**（ROS/仿真/多传感器） | 中 | 高 | E-009/011 |

### 2.1 「好操作」最强的子方向（按强度排序，D 级方向判断）

1. **补全（单任务，公开基准+公开代码）**：数据（ShapeNet/PCN 类）、代码（PoinTr/SeedFormer/AdaPoinTr）、单卡、短周期四项全满足（E-010）。**但同质化最严重**，纯换模块的「创新」会被红队淘汰；只有绑定一个可测失败（如真实腐蚀/复合退化下的鲁棒补全）才有立足点。
2. **去噪（单任务）**：操作性好，但单腐蚀已饱和（L-017/018/019），独立做难以区分度。
3. **退化恢复（统一/复合）**：创新窗口最新（E-002/004/006），同质化低；**但代码公开性未核、基准协议需自建**，工程风险与不确定性高于单任务，属于「好操作」与「新颖性」的权衡位，需红队 + 数据与基线先过闸门。
4. **上采样（单任务）**：操作性好，同质化中高。
5. **退化下 SLAM（次方向）**：与本人 SLAM/ROS 背景连续（见 CHARTER），仿真框架开源（E-009），但端到端系统工程重、单卡短周期难落地，**不是「低工程风险」首选**。

### 2.2 陷阱（应谨慎/淘汰的方向特征）

- **纯换模块拼接**：补全/去噪/上采样三方向里大量「把 X 换成 Mamba/Transformer/卷积」式工作，同质化极高，无法回答「为什么解决什么问题」（与 CHARTER「不做纯粹拼模块」一致）。
- **代码缺失的统一恢复**：SuperPC/PQDT 的官方代码未核（E-002/E-004 code_url 空），若 BASELINE 拿不到代码，统一恢复方向会退化为高风险。
- **退化下 SLAM 端到端**：工程链太长（数据→退化仿真→多传感器 SLAM→评测），与「5 个月投 IJCNN + 单卡 + 低工程风险」冲突（见 VENUE_CANDIDATES 时间压力）。
- **把 PACE-PC 的「复合退化偏序」当作既定事实**：无已核证据，属 D 级假设，禁止在未过五闸门（`docs/05`）前进入实验。

## 3. 种子论文核验结果摘要（详见矩阵与账本）

| 种子 | 核验结果 |
|---|---|
| SuperPC (CVPR 2025) | ✅ 核实（E-002），四任务统一扩散 |
| PQDT (CVPR 2026) | ⚠️ 仅 arXiv 预印本，**非 CVPR 2026**（E-004） |
| PointMAC (NeurIPS 2025) | ✅ 核实（E-003），测试时自适应补全 |
| ZFusion (ICCV 2025) | ✅ 核实但为 **2D 图像**盲超分（E-005） |
| DWCNet | ✅ 核实为 Computers & Graphics 2025 期刊（E-006） |
| SSUMamba | ⚠️ 实际是**高光谱图像去噪**（TGRS 2024），非点云（E-007） |
| CPCCD | ❌ 未定位到独立公开条目（E-008） |
| PConv (AAAI 2025) | ❌ 未定位到点云版（E-008） |
| AKCMamba-YOLO (CVPR 2026) | ❌ 未定位（E-008） |

## 4. 给总控台的下一步（供 IDEA 红队参考，非本专项决策）

- 先把「统一/复合退化恢复」的 3 篇核心（SuperPC、PQDT、DWCNet）做**全文+代码核验**（升 A），确认代码可得性——这是该方向能否进入 BASELINE 的前提。
- 对 PACE-PC 的「复合退化偏序」主张，须先过 `docs/05` 五闸门中的「查重闸门」与「最小反例闸门」，本专项未发现任何支持该偏序可学习的已核证据。
- 若追求「好操作」优先，单任务补全 + 一个**真实可测失败**（如退化/腐蚀下鲁棒补全）是最现实的落点，但须由红队证明确有未被 SuperPC/DWCNet/PQDT 覆盖的空缺。

---

# LANDSCAPE — 方向 B：跨模态室内定位 + 选择性接受（2026-09-05 追加核验）

> 本段是「文献情报」专项对另一份提案（跨模态室内定位 + 选择性接受）的**文献核验结果**，与上方「点云鲁棒恢复/退化」方向并行。证据口径一致：所有已核实事实链接 `EVIDENCE_LEDGER.md` E-012~E-028；未读全文处标注 D 级推断；不以论文数量等价趋势。
> 一句话背景（提案原文）：室内 GNSS 拒止下，单张 RGB 图像查询先验 3D 点云地图做地点/子地图级粗定位（跨模态检索），并对「重复结构 + 部分视野」歧义做候选竞争重排序 + 选择性接受（独立校准集离线选阈值，不做 ACI/覆盖率保证）。

## 0. 一句话结论

「单张 RGB 图像 → 先验 3D 点云地图」的**跨模态检索/位置识别**是 2024–2026 年已高度拥挤的方向（ModaLink/C2L-PR/InsCMPR/G2IA/SceneGraphLoc/WildCross，E-016~019/022/026 等）；「选择性接受/拒答」也已有多条独立路线（percentile rejection / 分类 / 回归 / 共形，E-012/020/021/025/013）。**两者各自均不构成护城河**；唯一未见直接撞车的是「跨模态检索 + 针对重复结构/部分视野歧义的选择性接受」这一组合，但它落在组件拼接风险区，须由 IDEA 红队用可测失败证伪支撑（详见 §4）。

## 1. 三年时间线（按子方向）

### 1.1 跨模态位置识别/检索（image → 3D 点云/场景图地图）

- 起点（2024）：ModaLink（IROS 2024，FoV 变换消除深度估计，E-017）、C2L-PR（T-IV 2024/2025，模态对齐 + 朝向投票，E-018）、SceneGraphLoc（ECCV 2024，图像 → 3D 场景图粗定位，室内，E-016）。
- 2025：InsCMPR（ICRA 2025，SAM 实例对齐 + Mamba-Transformer，E-019）；PRGS（Pattern Recognition 2025，但为**视觉单模态** VPR，E-015，非跨模态）。
- 2026：G2IA（arXiv 2606.15287，几何引导实例感知检索 + 候选重排序，E-014）、WildCross（arXiv 2603.01475，自然户外跨模态基准，E-022）、VLM-Loc（arXiv 2603.09826，文本→点云，非图像查询，E-024）。
- 已解决问题（B 级，各摘要声明）：城市场景 image→pointcloud 检索的模态鸿沟已有多套有效方案并声称 SOTA；实时性已有方案（ModaLink/InsCMPR 称 real-time）。
- 仍存在的可测失败（D，待验证）：**室内**重复结构 + 部分视野导致的检索歧义未被直接针对（现有工作集中 KITTI/HAOMO/NCLT/Oxford 等户外/城市场景）；跨模态检索的**拒答/选择性接受**未见直接工作（G2IA 只做重排序，不做拒答，E-014）。

### 1.2 定位/配准的「质量估计 + 拒答」（选择性接受的上游）

- 起点（2025）：Localization Meets Uncertainty（Technologies 2025 + arXiv 2504.07677，percentile-based rejection + aleatoric/epistemic 不确定性，冻结模型 + 接受层，E-012）；Decision PCR（arXiv 2507.14965，配准对错二分类，E-020）。
- 2026：MATTER（ICASSP 2026，配准误差**回归**取代分类，E-021）、Conformal-KF（ICASSP 2026，共形 + 卡尔曼滤波，跟踪域，E-025）、SAFEVPR（arXiv 2605.28048，视觉序列 VPR 的 Mondrian 共形 FDR 保证，E-013）。
- 已解决问题：定位回归/配准的「质量估计 + 拒答」已有多种范式（percentile / 分类 / 回归 / 共形）。
- 仍存在的可测失败（D）：**跨模态检索歧义**（离散候选竞争，非连续回归不确定性、非配准对错）的拒答未见直接工作；「无覆盖率保证的离线阈值」与「共形保证」两种路线在跨模态检索上的取舍未被对标。

## 2. 各子方向操作属性评估（B 级元数据/摘要的方向判断，D）

| 子方向 | 数据/代码成熟度 | 进入成本 | 同质化程度 | 判断依据 |
|---|---|---|---|---|
| 跨模态检索（image→点云，城市） | 高（KITTI/HAOMO/NCLT/Oxford 公开；ModaLink/InsCMPR 官方代码） | 中 | **高**（拥挤） | E-017/018/019/022 |
| 跨模态检索（室内） | 低-中（LaMAR/3RScan/ScanNet 可自建，但无现成室内跨模态点云检索基准） | 中高（需自建评测） | **低**（窗口） | E-026/027/028 |
| 选择性接受/拒答（定位侧） | 中（多种范式，但跨模态检索上无直接工作） | 中 | 中（共形 2026 明显升温） | E-012/013/020/021/025 |

## 3. 数据集可行性（核存在性与关键属性，不下载）

- 3RScan + 3DSSG（E-026）：室内 RGB-D 重扫描，1482 扫描 / 478 环境，含实例与 6DoF 重扫描真值；**公开**；可做地点级划分（D 推断，需自建划分协议）。
- ScanNet（E-027）：1513 场景 / 2.5M 视图 RGB-D，含相机位姿与语义；**地图模态是表面网格（mesh），非 LiDAR 点云**——若提案以「先验 3D 点云地图」为前提，ScanNet 需额外转换或改述。
- LaMAR（E-028）：ECCV 2022 AR 定位建图基准，头戴+手持 AR 设备，含 LiDAR 点云（2023-10 发布完整原始数据），激光扫描对齐得到精确 6DoF GT；**公开（需申请）**；「能否做地点级重定位评估」为 D 级推断（有 6DoF GT 理论上可派生，需读全文/实测确认）。

## 4. 护城河判断（本专项对提案 v3 的关键结论）

> 停止条件判定：`Localization Meets Uncertainty`（E-012）与 SAFEVPR（E-013）经核均**不构成**与「跨模态检索 + 选择性接受」的不可区分撞车，故不触发「护城河不成立」硬停；但逐项结论如下。

1. **护城河①「跨模态检索任务结构」→ 不成立**。这是拥挤方向：ModaLink、C2L-PR、InsCMPR、G2IA、SceneGraphLoc、WildCross 已覆盖 image→点云/场景图的检索（E-016~019/022/026）。
2. **护城河②「选择性接受」→ 不新颖**。Localization Meets Uncertainty 已做**无覆盖率保证的 percentile rejection**（与我们"独立校准集离线选阈值"定位几乎一致，只是用在回归而非检索，E-012）；SAFEVPR 已做**有 FDR 保证的共形**（比我们"不做保证"更强，E-013）。
3. **组合位「跨模态检索 + 选择性接受（针对重复结构/部分视野歧义）」→ 尚无直接撞车，但属组件拼接风险位**。要立得住，必须证明：(a) 室内跨模态检索的歧义是一个真实、可测、可复现的失败（现有城市工作未针对，E-014/018/019 均为城市场景）；(b) 选择性接受对**检索歧义**（离散候选竞争）与对**回归不确定性/配准对错**有本质不同，而非简单套用 percentile threshold。
4. **最危险最近邻是 G2IA（E-014），不是 Localization Meets Uncertainty / SAFEVPR**。G2IA 已做「跨模态检索 + 候选重排序」，与提案任务结构最接近；差距仅剩「室内 vs 城市」与「是否加选择性接受」两处，需红队验证这两处是否为真缺口。

## 5. 给总控台的下一步（供 IDEA 红队参考，非本专项决策）

- 若继续此方向：**必须**把 G2IA（E-014）列为头号最近邻并做全文+代码核验（升 A）；同时核 Localization Meets Uncertainty（E-012）的 percentile 阈值细节，证明"选择性接受用在检索歧义上"非其已有内容的平移。
- 需要补的实证：室内跨模态点云检索基准（基于 LaMAR / 3RScan / ScanNet 自建，E-026~028），以及"重复结构 + 部分视野歧义"的最小反例。
- 若红队判定"室内 + 歧义拒答"缺口不成立或仅为组件拼接，则本方向应**降级/淘汰**，回到既有「点云退化恢复」方向（上方主 landscape）比较。

---

# LANDSCAPE — 方向 C：候选条件下的空间对应与几何验证（题内重构查重，2026-09-11 追加核验）

> 背景（DECISIONS D-014）：原「跨候选区分证据」叙事已被否证，博士建议题内重构为「**候选条件下的空间对应与几何验证**」——不再给 Top-K 加权打分，而是对（query RGB ↔ 候选深度/点云）建立空间对应，再用几何验证（PnP/RANSAC 等）或空间布局一致性判断哪个候选更对。三条候选路线：① 传统局部特征匹配 + PnP/RANSAC；② 相对深度结构/空间布局一致性匹配；③ 学习式 RGB↔深度 patch 跨模态匹配。本专项执行主张级查重，判定是否真 gap。

## 0. 一句话结论

**该「题内重构」方向不是干净 gap（已读 G2IA/SOLVR/LiDAR-VFM/DXPR 全文，升 A 确认）。** 三条路线均已存在直接覆盖工作：路线①被 SOLVR（ICRA 2025，E-032）与 LiDAR Registration with VFM（RSS 2025，E-033）覆盖（对应 + RANSAC/ICP 几何验证，peer-reviewed）；路线②被 G2IA（arXiv 2606.15287，E-034）显式覆盖（GLM 验证「归一化成对距离 = 相对空间布局」跨模态一致性，且其未来工作正是引入度量深度）；路线③是高度拥挤的全局/实例级跨模态描述子匹配（ModaLink/InsCMPR/C2L-PR/GeoUniPR/DXPR/VXP 等）。唯一未见同名文献的是博士指名的「Depth-Guided Reranking（2025）」，但该文**未定位到**（E-036），且不能作为「存在缺口」的证据。

## 1. 四篇指名工作的核实结论（逐条）

| 工作 | 方法（核实后） | 是否做空间对应+几何验证 | 与三路线重叠 | 证据 |
|---|---|---|---|---|
| (LC)²（RA-L 2023，E-029/L-041） | 相机 disparity + LiDAR range 统一转 2.5D 深度图 → 描述子级跨模态匹配 → 位姿图回环 | **否**（无对应、无 PnP/RANSAC） | 路线③（全局描述子级）；不碰①② | B（摘要） |
| PDPR（Neurocomputing 2026，E-030/L-042） | 全景图 + 单目深度(Depth Anything v2)相对深度图 → 同一冻结 VPR 模型 late fusion → 全局描述子；model-agnostic；**单模态** VPR | **否** | 路线③浅层 + 与 rel_depth 资产概念相似（E-037，D）；不碰① | B（摘要+项目页） |
| DXPR（arXiv 2609.09005，E-031/L-043） | 相机(Depth Anything)+LiDAR(DOC-Depth)统一深度图 → DINOv2-SALAD 全局描述子；geometry-aware overlap miner 仅用于训练期 pair mining + loss 自适应 margin | **否**（overlap miner 是训练期 mining，非推理期候选验证；推理=纯描述子检索） | 路线③；路线②浅层；不碰① | **A（全文）** |
| Depth-Guided Reranking（2025） | **未定位到同名论文**（E-036） | 无法判断 | — | D/UNVERIFIED |

## 2. 额外高召回检索：直接覆盖三路线的工作（2023–2026，已读全文升 A）

> 本批用本机代理（http://127.0.0.1:7890）下载 G2IA / SOLVR / LiDAR-VFM / DXPR 的 arxiv 全文 HTML（arxiv.org/html/<id>），以下路线①②覆盖判断已从 B（摘要）升 A（全文），关键原文见 E-031~E-034。

- **路线①（空间对应 + PnP/RANSAC 几何验证）——已被覆盖，非 gap（A）**：
  - SOLVR（ICRA 2025，E-032/L-044）：立体深度(Unimatch)+occupancy 融合建 submap，与候选 LiDAR 提取稀疏关键点对应 → 几何一致性矩阵 → 特征向量作 inlier 概率 → 加权最小二乘求 6DoF（替代 RANSAC）。其相关工作总结 CorrI2P/VP2P-Match 已用「EPnP + RANSAC」做 pixel↔point 配准。
  - LiDAR Registration with Visual Foundation Models（RSS 2025，E-033/L-045）：DINOv2 图像特征经 point-to-pixel 投影作 LiDAR 点描述子 → 余弦相似点对应 → 3-point RANSAC → point-to-point ICP，官方代码公开。
  - 结论：RGB 特征 ↔ 深度/点云对应 + RANSAC/ICP 几何验证已是被 peer-reviewed（ICRA/RSS 2025）覆盖的成熟机制，博士 D-014 自注「最成熟、创新小」属实。
- **路线②（相对深度/空间布局一致性做候选判定）——已被 G2IA 覆盖，非 gap（A）**：
  - G2IA（arXiv 2606.15287，E-034）：CRM = Geometric Layout Matcher + Shape Feature Matcher。GLM 用 SAM 3D Objects 得实例 latent shape + 图像侧「pairwise distance matrix of all instance centers」，点云侧 DBSCAN 取主簇得 layout，双方「pairwise Euclidean distances normalized within each modality」后比较——**即归一化成对距离矩阵 = 相对远近/空间布局一致性**，与题内重构路线②（门框/边缘/平面远近顺序+空间布局）机制同构，仅锚点不同（G2IA=语义实例，博士=非语义几何基元+单目相对深度）。
  - 关键：G2IA 自述局限「GLM uses normalized pairwise distances, such normalization may discard useful metric cues... we plan to integrate powerful metric depth estimation methods into G2IA」——其未来工作正是引入度量深度（= rel_depth 方向），说明连「度量深度化」也已在 G2IA 的路线图上。
  - GeoUniPR（arXiv 2608.11263，E-035/L-046）：几何一致深度图视图建立「直接 RGB-LiDAR 对应」+ SC-InfoNCE（表征级对应，非显式点对应）。
- **路线③（学习式跨模态匹配）——高度拥挤**：
  - ModaLink/InsCMPR/C2L-PR（E-017/018/019，已在矩阵）、GeoUniPR（E-035）、DXPR（E-031）、Monocular VPR via SSM+Multi-View Matching（ICRA 2025，L-047）、MS2-CL（Sensors 2026）、VXP（3DV 2025）、Fine-grained Image-to-LiDAR Contrastive Distillation with VFM（NeurIPS 2024）。Raw RGB-patch↔depth-patch 是其中覆盖最浅的一档，但全局/实例级学习式跨模态对齐已饱和。

## 3. 给总控台的下一步（供 IDEA 红队裁决，非本专项决策）

- **本方向「题内重构」不构成 gap（A 级确认）**：路线②与 G2IA 同构、路线①与 SOLVR/RSS 2025 同构、路线③拥挤。建议红队按「与 G2IA 的不可区分性」做 stop 判定（G2IA 的 CRM = GLM+SFM 正是「验证实例形状 + 相对空间布局」）。
- 若要继续，唯一可能残留的微位是「用**非实例级、无监督相对深度顺序**（rel_depth 式）做跨模态候选判定」，但：(a) G2IA 的 GLM「归一化成对距离」已概念覆盖，且其未来工作明确要「integrate powerful metric depth estimation methods」（= rel_depth 方向）；(b) PDPR 已用「单目相对深度」做（单模态）VPR；(c) 这一微位太薄，难以支撑 IJCNN/IROS 级别创新，且与 D-014「把论文降级为相对深度特征+固定融合」的否决理由直接冲突。
- **建议**：回传「淘汰/重议」信号，让总控台 + 博士决定是回到既有「点云退化恢复」主线，还是给出「Depth-Guided Reranking（2025）」的可核 DOI/标题/作者后二次查重。本批 G2IA/SOLVR/LiDAR-VFM/DXPR 已读全文升 A，(LC)²/PDPR 仍为 B（摘要）口径，未读其全文。
