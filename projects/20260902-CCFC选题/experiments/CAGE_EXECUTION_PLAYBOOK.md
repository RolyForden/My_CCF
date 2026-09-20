# CAGE 分阶段执行手册

版本：v1.0，2026-09-21。

本文件把 CAGE v0.4 转换为可执行任务。它规定每一阶段下载什么、运行什么、产生什么文件、看到什么结果后继续或停止。文中的“期望结果”是**预期产物与可判定现象**，不是对实验结论的预写。

## 1. 总原则

执行顺序固定为：

`A 数据可答性 -> B 行为现象 -> C 表示定位 -> D 因果验证 -> E 跨模型确认 -> F 可选修复`

硬边界：

- 单张 RTX 4090；优先公开数据、官方代码和官方权重。
- 每一阶段通过后才下载下一阶段资产。
- Stage D 通过前不训练新模型、不接第二个模型、不设计修复模块。
- 不预设一定存在 switching failure、spatial binding failure 或可修复 bottleneck。
- 不把 smoke test 写成复现，不把 probe 可读写成模型实际使用，不把 patch 成功写成唯一真实机制。
- 原始数据与 checkpoint 放在 `source_private/`，不进入 Git。
- 项目仓库只保存脚本、小型 manifest、配置、汇总表和结论。

## 2. 文件布局

执行时采用以下布局：

```text
source_private/cage/
  laso/raw/                 # LASO 官方原始数据，只读
  repos/geal/               # GEAL 官方仓库固定 commit
  checkpoints/geal/        # 按阶段下载的官方权重

projects/20260902-CCFC选题/experiments/
  CAGE_EXECUTION_PLAYBOOK.md
  stage_a_data/
    audit_laso.py
    build_pairs.py
    tests/
  stage_b_behavior/
    run_geal_official.py
    run_query_controls.py
    evaluate_behavior.py
    tests/
  stage_c_localization/
    hook_map.yaml
    record_representations.py
  stage_d_intervention/
    intervention_registry.yaml
    run_intervention.py
  results/
    stage_a/
    stage_b/
    stage_c/
    stage_d/
```

尚未进入的阶段不提前创建代码骨架。

## 3. 下载清单与触发条件

| 资产 | 官方来源 | 下载时机 | 已核实信息 |
|---|---|---|---|
| LASO 数据 | [LASO 官方仓库给出的 Google Drive](https://drive.google.com/file/d/1P4CwQeSALtUOgzhg1ILCiKovE-tcXlSu/view?usp=sharing) | Stage A 开始 | 文件名为 `LASO_dataset.tar.gz`；解压结构需现场核验 |
| GEAL 代码 | [DylanOrange/geal](https://github.com/DylanOrange/geal) | Stage A PASS 后 | 官方环境为 Python 3.10、CUDA 11.8、PyTorch 2.1.0 |
| GEAL LASO seen 权重 | [laso_seen.pt](https://huggingface.co/datasets/dylanorange/geal/blob/main/laso_seen.pt) | Stage B0 | 554 MB；SHA256 `0163519dcf732cf9c9a4db176f8df79b7c207e0ee14a1324988f714eb4b4191e` |
| GEAL LASO unseen 权重 | [laso_unseen.pt](https://huggingface.co/datasets/dylanorange/geal/blob/main/laso_unseen.pt) | seen 评测链路正常后 | 554 MB；SHA256 `949d5b686555a14d6d827539b436a7cd11a59f2d4bae5a49f7f19a44010ca7fb` |

Stage A 不下载 GEAL、PointRefer、CMAT、PIAD 或任何训练权重。Stage B 先下载 seen 权重，链路通过后再决定是否下载 unseen 权重。

## 4. Stage A：LASO 数据可答性

### A0. 获取并冻结原始数据

执行目标：只下载 LASO 官方数据，记录来源、文件大小与哈希，不修改原始文件。

建议命令：

```powershell
New-Item -ItemType Directory -Force source_private/cage/laso/raw
python -m pip install gdown
gdown 1P4CwQeSALtUOgzhg1ILCiKovE-tcXlSu -O source_private/cage/laso/LASO_dataset.tar.gz
Get-FileHash source_private/cage/laso/LASO_dataset.tar.gz -Algorithm SHA256
tar -xzf source_private/cage/laso/LASO_dataset.tar.gz -C source_private/cage/laso/raw
```

先验证实际压缩包内容，再决定是否执行解压；若下载页需要登录或文件已变更，停止并报告，不从非官方镜像补齐。

期望产物：

- `source_private/cage/laso/LASO_dataset.tar.gz`
- `experiments/results/stage_a/source_manifest.json`
- 数据文件清单、大小、SHA256、下载时间和官方 URL

官方 GEAL 文档预期 LASO 根目录至少包含：

```text
Affordance-Question.csv
anno_train.pkl
anno_val.pkl
anno_test.pkl
objects_train.pkl
objects_val.pkl
objects_test.pkl
```

若实际结构不同，以原始包为准并记录差异，不静默重命名。

### A1. Schema 与完整性审计

创建 `stage_a_data/audit_laso.py`，只读加载数据并输出：

- 每个 split 的 annotation 数、独立 shape 数、class 数、affordance 数。
- 每条 annotation 的字段、mask dtype、长度、取值范围、缺失值和异常值。
- object 文件中 point 数、shape id 覆盖关系、重复或缺失对象。
- `Affordance-Question.csv` 的列结构、每个 object-affordance 对应的问题数量。
- train/val/test 之间的 shape id 重叠。

运行接口固定为：

```powershell
python projects/20260902-CCFC选题/experiments/stage_a_data/audit_laso.py `
  --data-root source_private/cage/laso/raw `
  --output projects/20260902-CCFC选题/experiments/results/stage_a
```

期望产物：

- `schema_report.json`
- `split_summary.csv`
- `integrity_issues.csv`
- `language_schema.json`

Gate A1：只有字段可解释、shape 与 object 可关联、split 泄漏情况明确后，才构建 pair。损坏或无法解释的 pickle 不允许靠猜测修补。

### A2. Same-shape pair 审计

创建 `stage_a_data/build_pairs.py`。对每个 split 按 `shape_id` 聚合不同 affordance，枚举候选 pair，并计算：

- `shape_id`、split、class、`affordance_a/b`、原 annotation 索引。
- mask IoU、前景面积、面积比、`||y_b-y_a||_1`。
- 独立 shape 数，而不是只报告 pair 数。
- 每种 affordance-pair 和 object class 的独立 shape 分布。

所有候选 pair 先保留。IoU 或面积阈值只能在看到完整分布后冻结，不能边看结果边调。

自动统计后，对将进入主要比较的高频 pair 类型做一次人工语义核对，记录“可并存、共享区域、层级关系、歧义或不可比较”。这里只审主要候选类型，不建立庞大的双人标注工程；无法明确判断的 pair 从主分析移到附录。

期望产物：

- `candidate_pairs.parquet`
- `pair_type_summary.csv`
- `pair_distribution.md`
- 用于讨论的 IoU、面积差和类别分布图

### A3. 语言模板与泄漏审计

对 `Affordance-Question.csv` 输出：

- Label、object 名称、affordance 词在问题中的出现率。
- Question0–14 是否只是槽位替换；去掉 object/affordance 后的唯一模板数。
- 每个 affordance 的词汇和句式多样性。
- 相同语义表达是否跨 object 复用。
- Canonical 与未来 Paraphrase 之间可控制的长度、关键词和模板差异。

期望产物：

- `question_inventory.csv`
- `template_clusters.csv`
- `lexical_leakage.csv`
- `language_audit.md`

这一阶段不使用 LLM 自动生成 paraphrase。先确定原数据到底提供了什么语言变化。

### A4. Stage A 裁决

Stage A 结束时只允许三个结论：

| 状态 | 判定依据 | 下一步 |
|---|---|---|
| `PASS` | 至少一个主要对比能形成 shape-disjoint 的 discovery/confirmation；pair 不完全由单一类别垄断；mask 确有可测差异 | 进入 Stage B |
| `DOWNGRADE` | pair 可用，但语言基本由标签或固定模板决定 | RQ 改为 prompt-conditioned spatial control，再由人决定是否继续 |
| `KILL` | 无法形成可靠 same-shape 多 affordance pair，或无法建立独立确认集 | 停止 CAGE，不下载 GEAL |

Stage A 不预设固定的 shape/pair 数门槛。审计完成后，根据主要 estimand、实际 cluster 数和希望达到的置信区间精度，单独冻结统计门槛；冻结文件写入 `stage_a_gate.yaml`，之后不得因结果不好而修改。

## 5. Stage B：GEAL 行为现象

### B0. 环境和官方结果复现

仅在 Stage A 为 `PASS` 后执行。

下载代码并记录 commit：

```powershell
git clone https://github.com/DylanOrange/geal.git source_private/cage/repos/geal
git -C source_private/cage/repos/geal rev-parse HEAD
```

环境预检：

```powershell
nvidia-smi
conda --version
wsl -l -v
```

GEAL 官方说明使用 Python 3.10、CUDA 11.8、PyTorch 2.1.0，并需要编译修改版 Gaussian rasterizer。官方页面没有承诺原生 Windows 支持，因此先根据 WSL/Linux 可用性选择环境，不把编译失败误判成方法不可复现。

官方评测入口：

```text
python scripts/evaluation.py --config config/evaluation.yaml
```

运行前完成：

- 把论文/README 中对应 setting 的官方指标抄入 `baseline_reference.yaml`。
- 配置 `dataset=laso`、`setting`、`ckpt`、`data_root`。
- 校验 checkpoint SHA256。
- 先跑一个 sample 的 forward，再跑完整官方 evaluation。

期望产物：

- `environment.txt`
- `geal_commit.txt`
- `evaluation_config_frozen.yaml`
- `official_eval.log`
- `official_metrics.json`
- 峰值显存和总推理时间

Gate B0：评测脚本成功完成、样本数与 split 一致、指标定义一致。若与论文值不一致，先定位数据版本、setting、checkpoint 和 evaluator；在差异解释前不运行 CAGE 指标。

### B1. 冻结查询条件

对每个合法 affordance 构造：

- `Label`：只保留 affordance label。
- `Canonical`：使用 LASO 官方问题。
- `Paraphrase`：只有在 Stage A 证明原问题具有自然语言内容后才构造；生成来源、prompt 和人工审核另存 manifest。

同时构造三个非主实验控制：

- `object-only`
- `query-only`
- category-affordance empirical prior

`null`、shuffle、unsupported query 只作附录压力测试，不进入行为存在性的主要证据。

期望产物：

- `query_manifest.parquet`
- `query_protocol.md`
- `query_review.csv`

### B2. Query-swap 行为实验

对同一 shape 的合法 pair 分别运行：

```text
(P, q_a) -> p_a
(P, q_b) -> p_b
```

保存逐点预测，不只保存汇总值。计算：

- 官方 aIoU、AUC、SIM、MAE。
- 双向 margin `m_a`、`m_b` 与 Bidirectional Control Accuracy。
- `E+`：应增强区域的平均定向变化。
- `E-`：应抑制区域的平均定向变化。
- `L0`：不应变化区域的附带扰动。
- Paraphrase Instability，单独报告，不与 affordance switching 混合。

方向性读数固定为：

```text
delta_y = y_b - y_a
delta_p = p_b - p_a
w_plus  = max(delta_y, 0)
w_minus = max(-delta_y, 0)
w_zero  = 1 - abs(delta_y)      # 仅在 Stage A 已确认 mask 位于 [0,1] 时使用

E_plus  = sum(w_plus  * delta_p)  / (sum(w_plus)  + eps)
E_minus = sum(w_minus * -delta_p) / (sum(w_minus) + eps)
L_zero  = sum(w_zero  * abs(delta_p)) / (sum(w_zero) + eps)

m_a = S(p_a, y_a) - S(p_a, y_b)
m_b = S(p_b, y_b) - S(p_b, y_a)
BCA = 1[m_a > 0 and m_b > 0]
```

若 mask 不在 `[0,1]`，先追溯官方预处理；不得为了套公式静默归一化 GT。

主机制分析只看单-query 本来表现合格的样本；“合格”阈值在查看 query-control 结果前，根据官方 metric 分布冻结。

期望产物：

- `raw_predictions/`，按 shape/query 保存
- `single_query_metrics.parquet`
- `pair_metrics.parquet`
- `accuracy_control_plane.csv`
- `behavior_summary.md`

### B3. Stage B 裁决

| 状态 | 观察 | 下一步 |
|---|---|---|
| `SURVIVE` | 高单-query表现样本中存在可重复的错误 switching；在 confirmation shapes 上仍出现；类别、面积、共现和词汇控制不能解释 | 进入 Stage C |
| `WEAK` | failure 只出现在少数 pair/class，或对语言形式高度敏感 | 补一个针对该混淆的控制；仍不稳定则降级 |
| `LANGUAGE` | Label 有效而 Canonical/Paraphrase 系统失败 | 转为模板依赖或语言泛化问题，不进入空间机制主线 |
| `KILL` | GEAL 在主要合法 pair 上稳定正确切换，或 failure 只来自本来就错误的样本 | 停止当前机制假设 |

## 6. Stage C：表示与空间绑定定位

只在 Stage B 为 `SURVIVE` 后执行，不训练模型。

先阅读实际 GEAL 代码并冻结四个功能阶段的 hook：

1. text encoder output；
2. cross-modal fusion output；
3. point representation before decoder；
4. decoder input/output。

每个 hook 写入 `hook_map.yaml`：模块路径、张量 shape、点/token 维含义、LayerNorm 前后位置以及是否改变原 forward。

对 discovery shapes 记录 query A/B 表示，检查：

- query 差异是否可被简单 readout 识别；
- 差异是否从全局表示进入 `D+ / D-`；
- 是否扩散到 `D0`；
- decoder 前已有正确信号但输出没有使用。

期望产物：

- `hook_map.yaml`
- `representation_effects.parquet`
- `spatial_selectivity_by_stage.csv`
- `candidate_locus.md`

只允许以下候选结论：`query collapse`、`fusion attenuation`、`spatial binding failure`、`decoder dominance`、`distributed/unclear`。Stage C 只能定位候选位置，不能写“根因已证明”。

Gate C：只有某个候选现象在 discovery 内稳定、在 confirmation 上方向一致，并且不是 metric 选择造成，才进入 Stage D。若只有“某层距离较大”，停止。

## 7. Stage D：模型内部因果验证

Stage D 只选择一个在 Stage C 冻结的 candidate locus，不全面扫层后挑最好结果。

最小实验矩阵：

| 实验 | 目的 | 通过表现 |
|---|---|---|
| A->B restoration | 测试候选信号是否足以推动正确切换 | `E+`、`E-` 朝正确方向，`L0` 不无差别增大 |
| B->A restoration | 排除单方向偶然性 | 反方向结果对称或可解释 |
| correct-case destruction | 测试原路径是否被正常 forward 使用 | 正确 switching 受损 |
| paraphrase swap | 零效应控制 | 不应产生 affordance switching |
| norm-matched random | 排除能量/尺度效应 | 显著弱于语义定向干预 |
| spatial mismatch | 排除任意空间注入 | 错位 patch 不应产生正确 D+/D- 模式 |
| dose curve | 排除二值偶然 | 干预强度与方向性行为呈稳定关系 |

注意：activation patching 可能激活正常 forward 不使用的 dormant pathway。因此 restoration 必须与 clean-run evidence、destruction 和 held-out prediction 联合解释；单独 patch 成功不构成忠实机制证明。

期望产物：

- `intervention_registry.yaml`
- `intervention_raw.parquet`
- `controls_summary.csv`
- `heldout_effects.csv`
- `causal_decision.md`

Stage D 裁决：

| 状态 | 结论 | 下一步 |
|---|---|---|
| `CAUSAL_CANDIDATE` | 双向干预、控制和 held-out 均支持空间定向效应 | 进入 Stage E |
| `SUFFICIENT_ONLY` | restoration 成立但 destruction 不成立 | 只能称替代/充分路径；补一次联合路径检查 |
| `CORRELATIONAL` | probe 可读但干预无定向后果 | 放弃该 locus，最多回 Stage C 一次 |
| `REJECT` | 与随机/错位控制无区别，或第二次定位仍失败 | 停止机制主线 |

## 8. Stage E：第二模型与论文方向

只有 Stage D 得到 `CAUSAL_CANDIDATE` 才选择第二模型。选择顺序不是固定名单，而是：

1. 任务输入输出与 LASO 一致；
2. 有可核验代码和可行权重；
3. fusion/decoder 与 GEAL 明显不同；
4. 单卡可运行且能访问内部张量。

PointRefer、CMAT、GLANCE 只是候选。若只有代码没有权重，先估算训练成本，再由人决定是否值得训练；不得为了“两个模型”强行重实现。

第二模型只重复：官方 sanity、Stage B 行为、被冻结功能阶段的 Stage C/D confirmation。不重新搜索一套故事。

论文方向裁决：

| 已取得证据 | 推荐方向 |
|---|---|
| 只有稳定行为 failure | evaluation/内部报告，暂不宣称机制 |
| 行为指标改变模型认识或排序，但机制不稳定 | benchmark/analysis 候选 |
| GEAL 上形成完整因果候选 | C 级机制论文候选 |
| 第二架构在相同功能阶段复现，并预测 held-out failure | B 级候选 |
| 只得到已有通用 routing 结论 | 降级为领域验证 |

## 9. Stage F：可选修复

Stage F 不是必经阶段。只有机制明确指出位置和计算缺陷时才允许设计修复：

| 机制结果 | 首先比较的最小修复 |
|---|---|
| query collapse | 更强文本表示或简单 paraphrase augmentation |
| fusion attenuation | 最小 bypass/residual 或匹配的 fusion baseline |
| spatial binding failure | point-query binding supervision 或最小 point interaction |
| decoder dominance | query-conditioned decoder-use constraint |
| distributed redundancy | 联合路径干预；不急于增加新模块 |
| 类别共现捷径 | balanced sampling 或简单 paired supervision |

如果简单 baseline 已恢复内部空间选择性和外部 switching，就接受简单答案。不得为了贡献数量继续叠 router、教师学生、蒸馏或额外 cross-attention。

## 10. 每阶段统一回报格式

每次只汇报以下六项：

```text
Stage:
Status: PASS / WEAK / KILL / BLOCKED
Commands actually run:
Artifacts:
Observed facts:
Decision and next permitted action:
```

计划、预期和未运行实验不得写进 `Observed facts`。

## 11. 当前唯一允许执行的任务

当前停在 Stage A0。收到下载授权后，允许执行：

1. 从 LASO 官方链接下载 `LASO_dataset.tar.gz`；
2. 记录文件大小与 SHA256；
3. 检查压缩包内容并解压到只读原始目录；
4. 实现并测试 Stage A 审计脚本；
5. 运行全量数据与语言审计；
6. 输出 `PASS / DOWNGRADE / KILL`，等待 checkpoint。

在该 checkpoint 前，不下载 GEAL、不搭 CUDA 环境、不运行模型。
