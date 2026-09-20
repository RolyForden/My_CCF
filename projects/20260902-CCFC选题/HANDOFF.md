# 对接文档（跨模态重定位 + 跨候选证据重排）

> 用途：上下文重置后，新会话/新 AI **只靠这份文档**就能接上进度、继续干活。
> 先读这份，再动手。若与远程实际情况有出入，以远程 `/root/autodl-tmp/` 下的脚本和日志为准。

---

## 一、项目是什么

- **论文**：IJCNN 2027（CCF-C），截稿约 2027-01-31。
- **任务**：室内重复结构下，单帧相机 → LiDAR 点云/深度地图的**地点识别**（cross-modal place recognition）。
- **我们的贡献（不是检索本身，是重排）**：Baseline 负责「找得像」（检索出 Top-K 候选），我们负责「分得开」——**跨候选共同/区分几何证据重排**，纠正错误 Top-1。
- **核心对象**：Support Matrix `S_ij`（query 局部 patch × Top-K 候选）；核心机制 = 跨候选共同/区分分解。
- **博士最终方案原文**：桌面 `最终方案：室内重复结构下的跨候选几何证据重排.md`（20 节，必读）。
- **博士方法论汇编**：桌面 `课题说明\博士科研决策规则与经验汇编.md`。

### 动机（已彻底解决，结论：成立）
无人机已有 **LiDAR（Livox Mid-360 + Fast-LIO2，负责建图）** + **相机（跑 YOLO 识别乒乓球，已在流帧）**。
跨模态重定位 = **复用已在跑的相机流 + 已在建的 LiDAR 点云地图**，零新增硬件、不建 RGB 图库。
- 审稿人若问「为什么不建 RGB 图库做图→图（单模态 97%）」：标准回答 = 相机画面瞬时消费（检测完就丢、不存档），点云地图才是系统唯一持久参考；不想额外存照片（存储+隐私）。
- 单模态图→图虽强（~97%），但无人机没有也不想要 RGB 图库，所以必须做跨模态（图→深度）。

### 博士两条铁律
1. **不做「置信度/可信/风险校准/门控/拒识」类方向**（博士原话「AI 通病就是喜欢置信度研究」，明确否定；LIO 退化门控也算这条，别再提）。
2. **20% 子集策略**：先用小子集（我们用的 6 场景）快速筛方案，方案成立才上 100% 全量。**别擅自扩数据/扩全量。**

---

## 二、远程环境 + 怎么连（关键，新 AI 必须会用）

- SSH：`ssh -p <PORT> root@connect.westd.seetacloud.com`，密码 `<REDACTED>`（seetacloud 云 GPU；凭据请线下索取，勿写入仓库）。
- 硬件：RTX 3090（49GB 显存），数据盘 `/root/autodl-tmp`（50GB）。
- 软件：torch 2.8.0+cu128、conda base（Python 3.12）、timm 1.0.29、safetensors、opencv-python-headless 已装。

### 我（旧会话）留下的 SSH 助手脚本，在本机 `C:\Users\19564\AppData\Local\Temp\opencode\`：
- **`s.py`**：连远程跑一条命令。用法 `python s.py "<命令>" [超时秒]`。脚本里已硬编码 SSH 信息 + 自动加 `export PATH=/root/miniconda3/bin:$PATH`。
- **`up.py`**：把本地脚本上传到远程 `/root/autodl-tmp/_run.py` 并**同步**运行（会等它跑完打印输出）。用法 `python up.py "<本地脚本路径>" [超时秒]`。
- **`bg.py`**：把本地脚本上传成远程 `/<名字>.py` 并**后台** `setsid nohup` 运行，日志写 `/<名字>.log`。用法 `python bg.py "<本地脚本路径>" "<远程名字>"`。长任务（训练）用这个。
- ⚠️ 三个脚本里都硬编码了 SSH 主机/端口/密码。**换机器要改**（`connect.westd.seetacloud.com` / `<PORT>` / `<REDACTED>`，凭据请线下索取）。

### 查进度：`python s.py "grep -E 'epoch|Recall' /root/autodl-tmp/<名字>.log | tail"` 或 `python s.py "tail -30 /root/autodl-tmp/<名字>.log"`。

### ⚠️ 坑：远程连不上 HuggingFace（被墙）
权重一律「**本机梯子下载 → SFTP 上传**」。本机梯子 `http://127.0.0.1:7890`（curl 加 `-x http://127.0.0.1:7890`）。上传用 paramiko（可参考本机 `upload_dino.py` / `upload_scenes.py`）。

---

## 三、数据

- **3RScan**（ICCV 2019，室内 RGB-D 重扫描），下了 30 个场景。
- 每场景目录（远程 `/root/autodl-tmp/3rscan_scenes/<scanId>/sequence/`）内文件：
  - `frame-XXXXXX.color.jpg`（RGB，960×540）
  - `frame-XXXXXX.depth.pgm`（16 位深度，224×172，单位 mm）
  - `frame-XXXXXX.pose.txt`（4×4 位姿矩阵，平移单位米）
  - `_info.txt`（内参）
  - 每场景约 107~571 帧。
- **本地** 30 个场景 zip 在 `C:\Users\19564\AppData\Local\Temp\opencode\3rscan_upload\`。
- ⚠️ 场景 `0ad2d399-79e2-2212-99cf-7a3512734bd7` 的 zip 损坏（解压后 0 帧），**实际只有 29 个有效场景**，脚本里用 `len(glob(f"{d}/frame-*.color.jpg"))>0` 过滤。
- 下载：本机梯子下 `https://campar.in.tum.de/public_datasets/3RScan/Dataset/<scanId>/sequence.zip`。

---

## 四、关键代码参数（都写死在脚本里，别记错）

- 输入 resize：`(800, 128)`（宽×高）；DINOv2 用 `(518, 518)`。
- 深度归一化：`clip(depth, 0, 6000mm) / 6000 * 255`，再复制成 3 通道。
- patch 网格：**8×4 = 32 个 patch**（不做自适应分割）。
- 训练：20 epoch，batch 8，lr 1e-4，triplet loss margin 0.3，负样本 `dist > 1m`、每 query 10 个负样本。
- 评测：pose-based GT，阈值 tau ∈ {0.25, 0.5, 1.0}m；正确 = (同场景 且 平移距离 < tau)。Top-K 取 20。
- 重排公式：`G_j = Σ_i D_i·S_ij / Σ_i D_i`；`F_j = 0.5·norm(B_j) + 0.5·norm(G_j)`。
- 场景级划分：前 2/3 训练、后 1/3 测试（6 场景子集 = 4 训练 + 2 测试）。

---

## 五、进度（全部在 6 场景子集 = 4 训练 + 2 测试）

### 5.1 Baseline（对比方法）
| baseline | 设置 | Recall@1 @1m | Recall@10 @1m | 备注 |
|---|---|---|---|---|
| ResNet34 + NetVLAD（训练过） | 跨模态 图→深度 | **32.66%** | 74.94% | 我们的地板；模型在 `/root/autodl-tmp/baseline_model.pth` |
| DINOv2（冻结零训练） | 跨模态 图→深度 | 28.86% | 82.78% | 更强 backbone **不解决排序**（gap 53.9 点） |
| DINOv2（冻结零训练） | 单模态 图→图（去自匹配） | ~97%（0.25m 就 96.7%） | ~100% | 单模态极强 → 跨模态鸿沟 68 点 → **这就是论文动机** |

- DINOv2 权重：远程 `/root/autodl-tmp/dino_vits14.safetensors`（ViT-S/14，本机下载上传的）。
- **Oracle 闸门（重要）**：跨模态 Recall@1=32.7% vs Recall@10=74.9% → 42 点空间 → 确认是 **ranking failure（排错）不是 retrieval failure（找不到）** → 重排有空间，动机扎实。

### 5.2 方法（跨候选证据重排）

- 已实现 **edge-depth Support**：query RGB 的 Sobel 边缘图 vs 候选 depth 的 Sobel 边缘图，逐 patch 余弦相似度。
- 区分性 `D_i`：已试 entropy / margin / variance / std / max / none 六种。

### 5.3 方法结果（三次迭代：edge → dino → rel_depth，最新已破墙）

三种 Support 全景（同一 harness，6 场景子集）：

| Support | 纯支持纠错 | best_vote | best_Di | Oracle | Di/Oracle |
|---|---|---|---|---|---|
| edge（Sobel 边缘） | 4.2% | 8.4% | 7.56% | 79.4% | 0.095 |
| dino（DINOv2 patch） | 10.5% | 10.5% | 10.92% | 57.6% | 0.190 |
| **rel_depth（相对深度顺序，Depth Pro 估 query 深度）** | 17.65% | 14.71% | **19.75%** | 79.0% | **0.250** |

**第 6 次推进「rel_depth 破墙」关键结论**：
1. 无监督纠错从 ~10%（dino）升到 **19.75%**（rel_depth entropy），接近翻倍。
2. **「跨候选区分分解」第一次给出稳定正增量**：entropy (19.75%) > 软平均 (17.65%) > 硬投票 (14.71%)——论文核心机制（共同/区分分解）第一次兑现，且 rel_depth 是博士《最终方案》第 10 节菜单里本来就有的候选（relative depth ordering）。
3. go/no-go 未触发（硬投票 14.71% ≠ 软平均 17.65% → 支持分布不「平」）→ 方向确认继续。
4. **重大发现：α=0.5 是历史错误设定**：
   - baseline 全局描述子 Recall@1 = 32.66%；
   - rel_depth **纯几何** Recall@1 = **56.46%**（+24 点）；
   - 混合 α=0.5 = 只有 44.81%（掺 baseline 反而掉 12 点）。
   - 含义：相对深度几何信号本身就是远强于全局描述子的跨模态地点信号；baseline 相似度在错例上是负信号，混合必须几何主导（α 很小或 α=0）。

**剩余问题**：19.75% vs Oracle 79% 还有 4 倍空间；α/β 未调；depth 归一化未扫。

---

## 六、接下来干什么（精确到可执行）

**主线已确认：rel_depth 是正路，继续优化它，不换第五个 Support。** 仍在 6 场景子集，不扩全量。

按优先级三步：
1. **修 α/β**：扫 α ∈ {0, 0.1, 0.2, 0.3, 0.5}，看 Recall@1 曲线，定几何主导的值（或纯几何 α=0）。当前 α=0.5 是历史错误，纯几何已经 56.46%。
2. **depth 归一化**：log / z-score / rank 三种扫一遍，看哪个让支持分布更「尖」——这是逼近 Oracle 79% 的杠杆。
3. **D_i 定死 entropy**（博士《最终方案》第 8 节公式 `D_i = 1 − H(P_i)/logK`），不再加变体。

### 之后
- 方法在 6 场景子集把「无监督纠错」明显抬起来（往 Oracle 79% 靠）→ 补最后一个 baseline **Patch-NetVLAD**（已有重排方法，作直接对照，要适配跨模态，最贵）。
- 全部成立 → 上全量（博士 100% 场景）→ 写论文（八股文结构）。

### 未定、需要用户/博士拍板的
- 若 rel_depth 优化后（α/β + 归一化都调过）纠错仍远低于 Oracle（比如还卡在 ~20%），是否拿「重复结构下 patch 级支持不够尖」去和博士重议机制。

---

## 七、文件位置速查

**本机（旧会话工作目录 `C:\Users\19564\AppData\Local\Temp\opencode\`）**：
- SSH 助手：`s.py`、`up.py`、`bg.py`
- 上传脚本：`upload_scenes.py`、`upload_dino.py`
- 各实验脚本源码：`train_clean.py`、`stage_cd.py`、`ablation.py`、`oracle_test.py`、`try_D.py`、`dino_baseline.py`、`dino_single.py`（这些也上传到远程同名列了）
- 场景 zip：`3rscan_upload\*.zip`（30 个）

**远程 `/root/autodl-tmp/`**：
- `baseline_model.pth`（训练好的 baseline）
- `dino_vits14.safetensors`（DINOv2 权重）
- 各脚本 + `.log` 日志
- `3rscan_scenes/`（数据）、`ml-depth-pro/`（Depth Pro 仓库）

**桌面 `课题说明\`**：
- `对接文档.md`（本文件）、`方法内部组件工作存档.md`（方法详细存档）、`博士科研决策规则与经验汇编.md`、`最终方案：室内重复结构下的跨候选几何证据重排.md`、各版 CUE-Loc PDF

**项目仓库 `Z:\科研总控台opencode\projects\20260902-CCFC选题\`**：`STATE.yaml`、`DECISIONS.md`、`HANDOFF.md`（=本文件副本）、`01_landscape/EVIDENCE_LEDGER.md`、`LITERATURE_MATRIX.csv`

---

## 八、避坑清单

1. 别做置信度/可信/门控方向（博士红线）。
2. 别扩全量，停在 6 场景子集筛方案（博士 20% 策略）。
3. 训练三件事：负样本只在 train 场景采样、去重 ref 场景、GT 用 pose-based 不是 scene-level。
4. 远程连不上 HuggingFace，权重本地梯子下载再上传。
5. 场景 `0ad2d399-...` zip 损坏，跳过。
6. PowerShell 里传含 `$`、`"`、`2>/dev/null` 的 bash 命令会被转义搞坏——复杂逻辑写成本地 Python 脚本用 `up.py`/`bg.py` 跑，别塞进 `s.py` 的命令字符串里。
7. 模型 forward 要 `@torch.no_grad()`，否则 `tensor.numpy()` 报 requires_grad 错。
