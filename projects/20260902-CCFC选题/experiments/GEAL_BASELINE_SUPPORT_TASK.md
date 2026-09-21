# GEAL Baseline 辅助任务单

版本：v1.0，2026-09-21。

## 任务定位

本任务交给辅助队友执行。目标只有两个：

1. 在不修改模型和评测协议的前提下，复现 GEAL 官方 LASO baseline；
2. 准备一个接受冻结 query manifest、导出逐点预测的推理入口。

主研究者继续负责 LASO 数据审计、合法 pair、query 条件、指标、统计分析和所有研究裁决。辅助队友无权改变数据 split、样本选择、阈值、metric 或论文主张。

## 与主线并发方式

| 研究者A | 辅助队友 |
|---|---|
| 下载并审计 LASO 数据 | 克隆 GEAL、搭官方环境、下载官方 seen 权重 |
| 构建并冻结 pair/query manifest | 复现官方 evaluation，不加入 CAGE 逻辑 |
| 决定 Stage A 的 PASS/DOWNGRADE/KILL | 输出复现日志、指标、显存和运行时间 |
| 交付冻结 manifest | 按 manifest 跑推理并导出逐点预测 |
| 计算 CAGE 指标并解释结果 | 不解释 failure，不修改实验协议 |

如果 Stage A 最终为 `KILL`，辅助队友立即停止；已经完成的 GEAL 官方复现可保留，但不继续开发 CAGE 推理功能。

## 允许下载的资产

### GEAL 官方代码

```powershell
git clone https://github.com/DylanOrange/geal.git source_private/cage/repos/geal
git -C source_private/cage/repos/geal rev-parse HEAD
```

记录实际 commit，不使用第三方 fork。

### GEAL LASO seen 权重

官方文件：

```text
https://huggingface.co/datasets/dylanorange/geal/resolve/main/laso_seen.pt
```

已核实：

```text
文件大小：554 MB
SHA256：0163519dcf732cf9c9a4db176f8df79b7c207e0ee14a1324988f714eb4b4191e
```

下载后必须校验：

```powershell
Get-FileHash source_private/cage/checkpoints/geal/laso_seen.pt -Algorithm SHA256
```

暂不下载 unseen、PIAD、corruption benchmark 或任何训练权重。

## Task 1：环境预检

运行并保存输出：

```powershell
nvidia-smi
conda --version
wsl -l -v
```

官方环境要求：

```text
Python 3.10
CUDA 11.8
PyTorch 2.1.0
torchvision 0.16.0
torchaudio 2.1.0
```

GEAL 需要编译仓库中的修改版 `diff-gaussian-rasterization`。官方 README 没有承诺原生 Windows 支持；如果 Windows 编译失败，先记录错误，再切到能够访问 RTX 4090 的 WSL2/Linux 环境。不得为了编译通过修改模型计算逻辑。

产物：

```text
projects/20260902-CCFC选题/experiments/results/baseline_geal_support/
  system_info.txt
  geal_commit.txt
  environment_notes.md
```

## Task 2：按官方说明搭建环境

官方命令基线：

```bash
conda create -n cage-geal python=3.10
conda activate cage-geal
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 \
  --index-url https://download.pytorch.org/whl/cu118
pip install git+https://github.com/dreamgaussian/dreamgaussian.git#subdirectory=simple-knn
pip install git+https://github.com/ashawkey/kiuikit
cd source_private/cage/repos/geal/thirdparty/diff-gaussian-rasterization
pip install .
cd ../..
pip install -r requirements.txt
```

实际执行命令和任何兼容性调整全部写入 `environment_notes.md`。允许做依赖兼容修正，不允许改网络结构、推理公式或 evaluator。

验收：

- Python 能 import `torch`，且 `torch.cuda.is_available()` 为真；
- Gaussian rasterizer 能 import；
- GEAL evaluation 脚本能显示帮助或读取配置；
- 不运行训练。

## Task 3：接入主研究者提供的 LASO 数据

主研究者交付只读路径：

```text
source_private/cage/laso/raw/
```

辅助队友只检查 GEAL 需要的文件是否存在：

```text
Affordance-Question.csv
anno_train.pkl
anno_val.pkl
anno_test.pkl
objects_train.pkl
objects_val.pkl
objects_test.pkl
```

不得重写 pickle、调整 split 或重新生成 mask。若文件名或结构不匹配，报告差异，由主研究者决定映射方式。

## Task 4：官方 evaluation sanity check

复制一份 `config/evaluation.yaml` 到结果目录，修改且只修改：

```text
dataset: laso
setting: seen
ckpt: <laso_seen.pt 的绝对路径>
data_root: <LASO raw 的绝对路径>
```

先执行单样本或最短可行 forward，确认：

- checkpoint 能加载；
- point 数和 tensor shape 合理；
- prediction 无 NaN/Inf；
- 原始输入样本未被修改。

再运行官方评测：

```bash
python scripts/evaluation.py --config <冻结后的 evaluation.yaml>
```

必须保存：

```text
evaluation_seen.yaml
official_eval_seen.log
official_metrics_seen.json
sample_count.json
runtime_and_vram.md
```

如果官方脚本只输出文本，可额外写一个纯解析脚本把结果转为 JSON；不得改动指标计算。

验收：

- 评测进程正常结束；
- 样本数与官方 split 一致；
- 产出 aIoU、AUC、SIM、MAE；
- 指标与论文/官方说明的比较采用同一 setting 和 evaluator；
- 若数值不一致，只报告差异，不自行挑选更有利的配置。

## Task 5：准备逐点预测导出

只有官方 evaluation 完成后才做此任务。

目标是在**不改变 forward 和 evaluator**的前提下，为每次推理额外保存：

```text
sample_id
split
shape_id
class
affordance
query_id
query_text
prediction         # 逐点 float32
ground_truth       # 逐点 float32
point_count
checkpoint_sha256
geal_commit
```

输出格式：

- 元数据：Parquet 或 JSONL；
- 逐点数组：压缩 NPZ；
- 元数据必须能通过 `sample_id` 唯一定位 NPZ 中的数组。

新增代码单独放在：

```text
projects/20260902-CCFC选题/experiments/stage_b_behavior/geal_export/
```

不要直接重写官方仓库核心文件；优先用薄包装器调用官方 dataset/model/evaluator。

导出正确性检查：

1. 不启用导出时，官方指标与 Task 4 完全一致；
2. 启用导出后，用保存的 prediction 重新计算一个小批次指标，结果与在线 evaluator 一致；
3. 同一配置重复推理时 deterministic 输出一致；若不一致，记录来源。

## Task 6：等待主研究者的冻结 manifest

辅助队友不得自行创造 query pair。主研究者会提供：

```text
pair_manifest.parquet
query_manifest.parquet
stage_a_gate.yaml
```

只有 `stage_a_gate.yaml` 为 `PASS` 时，才实现 manifest-driven inference：

```text
(shape_id, query_text, query_condition) -> raw point prediction
```

本任务只负责批量运行并导出结果，不计算或解释 BCA、`E+ / E- / L0`，也不筛选“成功/失败”样本。

## 明确禁止

- 不训练 GEAL，不微调，不换 backbone。
- 不修改数据 split、mask、point 数或 evaluator。
- 不自行生成 paraphrase、unsupported query 或 pair。
- 不根据输出选择 layer、样本或阈值。
- 不开始 activation hook、patching 或方法修复。
- 不把 smoke test 写成“复现成功”。
- 不更新 proposal、README、EVIDENCE 或研究结论。

## 最终回传格式

```text
Status: REPRODUCED / MISMATCH / BLOCKED
GEAL commit:
Checkpoint SHA256:
Environment:
Commands actually run:
Official metrics:
Reference metrics and difference:
Sample count:
Peak VRAM and runtime:
Prediction export status:
Artifacts:
Blocking issue, if any:
```

回传只描述事实，不判断 CAGE 是否成立
