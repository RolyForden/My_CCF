# CAGE 今日五卡执行任务书

版本：v1.0，2026-09-21  
执行窗口：今天连续执行，可用 5 张 GPU  
定位：从 GEAL 20% 工程筛选继续推进到行为判定；只有行为现象成立，才进入表示定位和因果干预。

## 1. 本轮采用的科研原则

本任务优先采用《博士科研决策规则与经验汇编》的实验经验：

- 20%（必要时 10%）子集用于快速筛选是有效做法；20% 不通过的路线不消耗全量算力。
- 先跑单样本，再跑 20%，筛选通过后再跑全量。
- 算力充足时并行跑，但不能并行跳过依赖关系。
- 先验证输入输出和现象，再定位机制；没有靶，不设计方法。
- 若进入训练，只比较少量机制对应方案，训练到收敛，不用固定 step 草率排名。

因此，队友返回的 GEAL 20% 结果记为：

> **工程筛选通过**：官方代码、权重、LASO seen 数据和 evaluator 已能端到端运行。

它足以放行下一轮工作，不要求先补一套“工业级复现”。但它还不能替代后续全量参考值，也不能证明 query switching failure 或任何机制成立。

## 2. 今日唯一目标

今天必须回答：

> 在单 query 本来预测合格的 LASO 样本上，改变合法 affordance query 后，GEAL 是否存在稳定且不能由标签模板、mask 过近、类别先验解释的 point-level switching failure？

今日产出优先级：

1. **必须完成**：数据审计、冻结 pair/query manifest、逐点预测导出、20% 行为筛选。
2. **20% 现象成立后必须完成**：全量 discovery 与一次冻结 confirmation。
3. **行为现象确认后才做**：表示定位。
4. **定位形成单一候选后才做**：因果干预。
5. **今天默认不做**：正式新方法、大规模训练、第二数据集、论文写作。

## 3. 人员与算力分工

主研究者保留研究裁决权；辅助队友负责运行、导出和事实回报，不自行改变 pair、query、阈值或主张。

| 资源 | 固定职责 | 条件性职责 |
|---|---|---|
| CPU/主研究者 | LASO 审计、pair/query 合法性、阈值冻结、最终裁决 | 检查候选 failure 和干预解释 |
| GPU 0 | GEAL canonical baseline、导出一致性 | 全量 reference run |
| GPU 1 | 行为实验 shard 0 | text/fusion hook |
| GPU 2 | 行为实验 shard 1 | point representation hook |
| GPU 3 | 行为实验 shard 2 | decoder hook |
| GPU 4 | 行为实验 shard 3、控制条件 | 随机/错位/破坏性干预控制 |

五张卡如果位于不同机器，先从已跑通实例克隆环境；如果在同一机器，用 `CUDA_VISIBLE_DEVICES` 固定任务。禁止五张卡各自修改一份不同代码。所有任务记录同一个 GEAL commit 和同一份实验代码快照的 SHA256。

### 3.1 权限和交付边界

辅助队友没有本仓库的 commit、push、merge 或改写历史权限。远端产生的代码与结果不能只留在服务器，也不能只交一份总结报告。

执行结束后，由一台汇总机器生成：

```text
CAGE_20260921_DELIVERY/
  DELIVERY.md
  commands.sh
  code/
  code_patch.diff
  configs/
  manifests/
  logs/
  metrics/
  summaries/
  sample_outputs/
  remote_large_files.csv
  SHA256SUMS.txt
```

交付要求：

- `DELIVERY.md` 写明完成/未完成任务、实际偏离、远端机器和 GPU。
- `code/` 只放本轮新增或修改的实验脚本，不复制整个 GEAL 仓库。
- `code_patch.diff` 用 `git diff --binary` 或等价方式生成，使主研究者能审查代码修改；不得由执行者提交。
- `configs/` 和 `manifests/` 必须是实际运行版本，不是计划模板。
- `logs/` 保留 stdout/stderr；`metrics/` 保留机器可读原始结果，不能只有 Markdown 摘要。
- `sample_outputs/` 至少包含能复核导出格式和指标计算的小批次 prediction/GT。
- 大型逐点预测、activation、数据集和 checkpoint 如果不随包交付，写入 `remote_large_files.csv`，包含绝对路径、大小、SHA256 和保留期限。
- `SHA256SUMS.txt` 覆盖交付包内所有关键文件。

最终把整个目录压缩为 `CAGE_20260921_DELIVERY.zip` 或 `.tar.zst` 交给主研究者。主研究者把交付包带回本工作区后，再与主控 agent 共同检查、分析并决定哪些代码和结论可以进入仓库。

## 4. 统一目录和最小记录

远端工作根目录沿用：

```text
/root/autodl-tmp/cage/
```

新增：

```text
today/
  intake/
  data_audit/
  manifests/
  baseline_full/
  behavior_20pct/
  behavior_discovery/
  behavior_confirmation/
  hooks/
  interventions/
  decision.md
```

每个实际运行只保留四样东西：命令、冻结配置、原始输出、摘要表。不要再写重复的阶段协议。

## 5. Task 0：接收并核对上一轮产物（CPU，2 小时内）

从原实例复制以下文件到 `today/intake/`：

```text
subset20_test.json
evaluation_seen_20pct.yaml
official_metrics_seen_20pct.txt
sample_count_20pct.json
runtime_and_vram.md
smoke.log
eval20.log
environment_notes.md
geal_commit.txt
ckpt_sha256.txt
```

只处理两个矛盾：

1. 原报告同时写了 `missing_keys` 为空和缺少 `feature_downsampler.*`。保存实际 `load_state_dict` 返回值、`strict` 参数和调用位置。
2. 保存实际子集生成脚本，确认 seed 42 是按 shape 抽样，而不是按 annotation 抽样。

验收：能从原始文件恢复 493 pair、207 shape 和四个汇总指标。不能恢复则先补齐，不能只引用报告正文。

## 6. Task 1：LASO 数据与语言审计（CPU，与 Task 0 并行）

只读审计 train/val/test 三个 split，输出：

- annotation、shape、class、affordance 数量；
- 同 shape 多 affordance 的 shape 数、pair 数和 pair 类型；
- 每对 mask 的 IoU、前景比例、`mean(abs(y_b-y_a))`；
- object/annotation 对齐、重复和 split shape 重叠；
- 官方问题是否只是 object/affordance 槽位模板；
- affordance label、object name 在文本中的显式出现率。

产物：

```text
today/data_audit/schema.json
today/data_audit/pairs_all.parquet
today/data_audit/pair_type_summary.csv
today/data_audit/language_summary.md
today/data_audit/issues.csv
```

主研究者在看模型行为前冻结：

- 不可比较或语义含混的 pair 类型；
- discovery 使用的 split 和 20% shape 清单；
- confirmation 使用的 split/shape 清单；
- mask 差异过小的排除规则；
- “单 query 表现合格”的判据制定方法。

优先采用：val 做 discovery，test 做一次 confirmation。若 LASO 实际结构不支持，记录事实后由主研究者改成 shape-disjoint 划分，不允许执行者自行选择最有利划分。

Task 1 裁决：

| 结果 | 动作 |
|---|---|
| 有足量合法 pair，且 mask 有明显差异 | 继续 Task 2/3 |
| pair 可用，但语言接近闭集 label/template | 继续，但研究表述降为 prompt/label-conditioned spatial control |
| 无可靠 same-shape pair | 立即停止 CAGE 主线 |

## 7. Task 2：完整 baseline 与逐点导出（GPU 0）

20% 已完成工程筛选，不需要推倒重来。现在依次执行：

1. 用 batch size 8 跑 LASO seen 完整官方 evaluation，保留原 evaluator。
2. 用 batch size 32 复跑一次；若四项指标一致，后续推理可用 32。
3. 实现薄包装器，额外导出 `sample_id/shape_id/query/GT/prediction`，不改 forward。
4. 从导出结果离线重算四项指标，与在线 evaluator 对齐。

命令以 GEAL 实际 CLI 为准，最终必须落盘为：

```text
today/baseline_full/commands.sh
today/baseline_full/evaluation_seen_bs8.yaml
today/baseline_full/evaluation_seen_bs32.yaml
today/baseline_full/eval_bs8.log
today/baseline_full/eval_bs32.log
today/baseline_full/metrics_comparison.json
today/baseline_full/export_check.json
```

通过标准：完整 split 正常结束；样本数正确；导出开关不改变在线指标；离线重算与在线结果在数值精度内一致。与论文参考值有偏差可以继续行为实验，但必须把偏差原样保留，不能改配置追数字。

## 8. Task 3：冻结行为实验输入（CPU）

每个合法 pair 至少包含：

```text
(shape_id, affordance_a, affordance_b, query_a, query_b, mask_a, mask_b)
```

查询分三层：

- `Label`：affordance label；
- `Canonical`：LASO 官方问题；
- `Paraphrase`：仅在 Task 1 证明存在值得检验的自然语言变化时加入。

控制条件：

- 正确 object + 错误但语法合法、该 shape 不支持的 affordance；
- object-only；
- query-only 或类别-affordance empirical prior；
- 同义改写控制不得与 affordance switching 混算。

输出：

```text
today/manifests/pair_manifest.parquet
today/manifests/query_manifest.parquet
today/manifests/discovery20_shapes.json
today/manifests/discovery_full_shapes.json
today/manifests/confirmation_shapes.json
today/manifests/frozen_rules.yaml
```

20% 子集按 shape 抽样，并尽量覆盖主要 pair 类型；只允许在运行前根据数据分布冻结一次。不得因为模型结果不好重新抽样。

## 9. Task 4：20% 行为筛选（GPU 1-4 并行）

将 `discovery20_shapes.json` 按 shape 分成 4 个互斥 shard。每张卡运行同一代码、同一 checkpoint，只改变 shard id。每个 `(shape, query)` 只推理一次，保存逐点预测，汇总时去重。

计算：

- 官方 aIoU、AUC、SIM、MAE；
- 每个 query 的单独表现；
- query A/B 的预测变化量；
- BCA、`E+`、`E-`、`L0`；
- 近零预测变化比例，同时报告对应 GT 变化量；
- Label/Canonical/Paraphrase 的分层结果；
- 按 class、affordance pair、mask IoU、区域大小分层。

分析顺序固定：先筛出单 query 本来预测合格的样本，再判断 switching。不得把“模型本来就预测错”包装成 query-control failure。

20% 裁决：

| 状态 | 观察 | 下一步 |
|---|---|---|
| `SURVIVE` | 合格样本中存在重复出现的错误 switching，且至少跨多个 shape/pair 类型 | 立即跑全量 discovery |
| `LANGUAGE` | Label 明显有效，但 Canonical/Paraphrase 系统失败 | 转向模板依赖问题，不做空间机制干预 |
| `AMBIGUOUS` | 只在单一类别、微小 GT 差异或少量异常样本出现 | 补一个针对性控制，最多半天 |
| `KILL` | 合格样本基本能随 query 正确切换 | 停止当前机制主线 |

报告必须给分母和分布，不为 `SURVIVE` 预设一个漂亮百分比。判断依据是可重复、跨 shape、不能被数据歧义解释。

## 10. Task 5：全量 discovery 与冻结 confirmation（条件：Task 4=SURVIVE）

1. GPU 1-4 运行 full discovery 的四个 shape shard。
2. 合并结果后只允许修复实现错误，不再更改指标或排除规则。
3. 主研究者写下对 confirmation 的方向性预测，例如“candidate failure 主要出现在某类 mask relation，而不是某个单词”。
4. GPU 0-4 对 confirmation shapes 分片运行一次。

产物：

```text
today/behavior_discovery/raw_predictions/
today/behavior_discovery/pair_metrics.parquet
today/behavior_discovery/summary.md
today/behavior_confirmation/raw_predictions/
today/behavior_confirmation/pair_metrics.parquet
today/behavior_confirmation/summary.md
```

只有 confirmation 方向一致，才允许进入表示定位。若 discovery 强、confirmation 消失，结论是现象未确认，不回头调阈值。

## 11. Task 6：表示定位（条件：行为 confirmation 成立）

先检查实际 GEAL 代码，再在 `today/hooks/hook_map.yaml` 冻结四个功能位置，不从结果反选层：

1. text encoder 输出；
2. cross-modal fusion 输出；
3. decoder 前 point representation；
4. decoder 输入与输出。

并行方式：GPU 1/2/3 各负责一个主要功能阶段，GPU 4 负责 clean-run 与 paraphrase/random controls，GPU 0 保留用于复核。所有 hook 必须先证明不改变原始 prediction。

对行为 failure 和 matched correct cases 比较：

- query A/B 表示差异是否存在；
- 差异能否在 held-out shape 上被简单 readout 识别；
- point-level 差异是否集中在 GT 应变化区域，而非均匀扩散；
- decoder 前已有空间定向信号、decoder 后是否被压掉。

只允许输出一个优先候选：`query collapse`、`fusion attenuation`、`spatial binding failure`、`decoder dominance` 或 `distributed/unclear`。若没有单一候选，停止，不为了用满 GPU 扫所有层。

## 12. Task 7：因果干预（条件：Task 6 有单一候选）

先在 20% failure discovery 样本筛选：

| GPU | 干预 |
|---|---|
| 0 | A→B restoration |
| 1 | B→A restoration |
| 2 | correct-case destruction |
| 3 | norm-matched random + paraphrase control |
| 4 | spatial mismatch + dose curve |

成功不能只看总 mask 变化，必须同时满足：

- `E+`、`E-` 朝正确方向；
- `L0` 没有无差别增大；
- random、paraphrase、spatial mismatch 明显弱于语义定向干预；
- correct-case destruction 对正常 switching 有破坏作用；
- 20% 筛选成立后，在冻结 confirmation 上复现方向。

裁决：

| 状态 | 含义 |
|---|---|
| `CAUSAL_CANDIDATE` | restoration、destruction、controls、confirmation 共同支持 |
| `SUFFICIENT_ONLY` | restoration 有效但 destruction 无效，只能称替代路径 |
| `CORRELATIONAL` | 表示可读但干预不恢复行为 |
| `REJECT` | 与随机或错位控制无区别 |

今天只有得到 `CAUSAL_CANDIDATE` 才允许另写方法任务书；本文件不预设 paired loss、router、binding module 或 decoder 改造。

## 13. 今日调度

| 时间块 | 主路径 | 五卡使用 |
|---|---|---|
| 第 0-1 小时 | 接收上一轮产物，启动数据审计 | GPU 0 启动 full baseline；GPU 1-4 做导出和 shard smoke |
| 第 1-2 小时 | 完成审计，冻结 pair/query manifest | GPU 0 做导出一致性；GPU 1-4 待命接收 shard |
| 第 2-3 小时 | 跑 20% 行为筛选并立即裁决 | GPU 1-4 分片；GPU 0 汇总与复核 |
| 第 3-5 小时 | 若 `SURVIVE`，跑 full discovery | 五卡按 shape 分片 |
| 第 5-6 小时 | 跑冻结 confirmation，形成行为裁决 | 五卡按 shape 分片 |
| 第 6-8 小时 | 若行为确认，冻结 hook map 并完成表示定位 | GPU 1-4 按功能阶段并行；GPU 0 做无扰动复核 |
| 第 8-10 小时 | 若有单一候选，跑 20% 因果干预 | 五类干预并行 |
| 第 10-12 小时 | 跑干预 confirmation 或停止，汇总事实 | 只运行尚未完成的决定性实验 |

时间块是调度目标，不是伪造的完成承诺。某一步出现代码错误或科学裁决为 `KILL` 时，立即停止后续依赖任务；不得为了“今天跑完”而跳过审计、冻结或控制实验。

若某一阶段提前 `KILL`，空出的 GPU 不自动转去训练新方法。先由主研究者决定是否转向语言模板问题、第二个公开 baseline，或结束当前课题。

## 14. 一次性回传格式

```text
Completed tasks:
Commands actually run:
GEAL commit and experiment-code snapshot SHA256:
Data/checkpoint hashes:
20% screening result:
Full discovery result, if permitted:
Confirmation result, if permitted:
Representation candidate, if permitted:
Intervention result, if permitted:
Raw artifact paths:
Observed failures or protocol deviations:
Next scientifically permitted action:
Delivery archive path and SHA256:
```

把计划、估计和期待放在单独说明中，不写入 observed result。不得将“20% 工程筛选通过”改写为“query-control 假设成立”。
