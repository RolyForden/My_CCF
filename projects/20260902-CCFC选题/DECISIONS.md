# Decisions

只记录改变研究方向、核心假设或主要实验协议的决定。日常搜索、文案修订和文件产出不登记。

## 2026-09-16 - 旧方向移出主工作区

- 决定：停止 PACE-PC、跨模态地点检索、点云退化恢复等旧路线，将完整历史放入 `Z:\科研总控台opencode-archive\`。
- 依据：这些方向已经被查重、反例或可行性否定，继续放在高频工作区会干扰当前判断。
- 复查条件：出现能直接推翻原否定理由的新证据。

## 2026-09-20 - 否定旧 FocalInspect 方法主线

- 决定：不再推进“局部重渲染 + 全局语境 + 选择性蒸馏”。
- 依据：PointRefer、GEAL、GLANCE 和 CMAT 已分别覆盖多尺度、粒度自适应融合、local-global connector、几何先验和编码器语义增强。该组合解决的是合理工程问题，但缺少结构性机制矛盾。
- 仍然保留：language-guided 3D affordance grounding 的任务、公开数据和官方 baseline 资产。

## 2026-09-20 - CAGE 降级为测量装置

- 决定：研究对象改为 query control 沿 `query -> text encoder -> fusion -> point representation -> decoder -> mask` 的传播与因果作用。CAGE 只负责受控 pair、行为测量和干预，不作为正式方法。
- 依据：反事实评测、sensitivity metric、paired loss 和 activation patching 都已有直接先例；潜在研究价值在任务特有的 point-level spatial control failure，而不是工具本身。
- 继续条件：数据能形成可靠 pair，至少两个可复现模型出现无法由歧义、重叠或改写噪声解释的 switching failure，并能通过双向干预建立行为后果。
- 停止条件：数据不可答、强 baseline 无 failure，或内部变化只能得到相关性而不能形成任务特有的机制结论。
