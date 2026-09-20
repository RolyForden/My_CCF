# Evidence Ledger

> 本账本只记录**当前主攻方向 FocalNadir-VO** 相关的证据。旧方向（跨模态/点云恢复）的证据已随 `DECISIONS.md` 归档至 `Z:\科研总控台opencode-archive\`。

| ID | 主张 | 证据等级 | 来源 | 已读范围 | 直接支持内容 | 核验人 | 日期 | 状态 |
|---|---|---|---|---|---|---|---|---|
| E-001 | 高空俯视单目 SLAM 存在特定退化：弱视差、长轨迹形变、垂向误差大 | A | arXiv 2608.18632《Evaluation of Monocular SLAM Systems on High-Altitude Nadir UAV Footage》(2026-08) | 摘要全文 | 五系统评测；无 IMU/GNSS；DROID-SLAM 综合 2.88%、MASt3R-SLAM DJI 水平 0.53%；垂向仍差、长序列 ALTO/GES 形变 | 总控台 | 2026-09-16 | VERIFIED |
| E-002 | MARS-LVIG 是公开的真实无人机多传感器 SLAM 数据集 | B | IJRR 2024《MARS-LVIG dataset》(doi:10.1177/02783649241227968) | 元数据 | DJI M300；含 LiDAR-视觉-惯性-GNSS；本方案只取 RGB、RTK 作 GT | 总控台 | 2026-09-16 | VERIFIED(B) |
| E-003 | DPVO 是 patch 图上的可训练单目 VO，单卡可训 | B | arXiv 2208.04726《Deep Patch Visual Odometry》(NeurIPS 2023) | 元数据 | patch 图 + 可微 BA；单张 3090、bs1、24 万步约 3.5 天 | 总控台 | 2026-09-16 | VERIFIED(B) |
| E-004 | 平面—视差分解已存在，且已用于深度估计 | B | MonoPP, WACV 2025 (doi:10.1109/wacv61041.2025.00275) | 元数据 | 度量尺度自监督单目深度，planar-parallax 几何；**非 VO** | 总控台 | 2026-09-16 | VERIFIED(B) |
| E-005 | ALTO 是公开的无人机视觉定位/地点识别数据集 | B | arXiv 2207.12317《ALTO》(2022) | 元数据 | 大规模 UAV VPR/定位；被 E-001 评测用作长距离序列 | 总控台 | 2026-09-16 | VERIFIED(B) |
| E-006 | DALES 是航空 LiDAR 语义分割基准，细长类为最差类 | A | CVPRW 2020《DALES》(doi:10.1109/cvprw50498.2020.00101) | 全文 | 8 类含 power lines/poles/fences；细长类 IoU 显著低于 ground/buildings | 数据与基线 | 2026-09-16 | VERIFIED(A) |
| E-007 | PT-WNO 已在 DALES 上做局部点特征+全局小波语境 | B | arXiv 2606.11466《PT-WNO》(2026) | 元数据 | 论文存在；"81.05 mIoU"具体数字**未核** | 总控台 | 2026-09-16 | UNVERIFIED(数字) |
| E-008 | EZ-SP 存在（superpoint 快速划分），非蒸馏 | B | arXiv 2512.00385《EZ-SP》(2025) + Zenodo 2026 | 元数据 | superpoint 分割 GPU 快速划分；"ICRA 2026 接收"未在 OpenAlex 直接核到 venue 标签 | 总控台 | 2026-09-16 | VERIFIED(存在)/venue 待核 |
| E-009 | PatchTeacher 是半监督三维**检测**，非分割蒸馏（纠错） | A | arXiv 2407.09787《Semi-supervised 3D Object Detection with PatchTeacher and PillarMix》(AAAI 2024) | 摘要 | patch 高分辨率体素化教师→全场景学生**伪标签**（非蒸馏）；任务=检测 | 文献情报 | 2026-09-16 | VERIFIED(纠错) |
| E-010 | PointDistiller 是三维**检测** KD，CVPR **2023**（纠错） | A | arXiv 2205.11098《PointDistiller》(CVPR 2023, doi:10.1109/cvpr52729.2023.02087) | 摘要 | local distillation + reweighted learning；任务=检测 | 文献情报 | 2026-09-16 | VERIFIED(纠错) |
| E-011 | "DALES 2 (CVPRW 2026)" 不存在（纠错） | A | 检索记录 | 检索 | 只有 DALES(CVPRW 2020) 与 DALES Objects(2021)；无 "DALES 2" | 文献情报 | 2026-09-16 | VERIFIED(否定) |

## 规则

- `A`：全文/官方代码已核并定位到相关内容。
- `B`：官方元数据或摘要已核。
- `C`：二手材料、截图或转写。
- `D`：推断或假设。
- 任何 `VERIFIED` 条目必须包含可访问来源与核验范围。
