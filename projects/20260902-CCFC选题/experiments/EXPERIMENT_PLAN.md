# Experiment Plan

## 核心主张

TBD

## 分阶段计划

### Smoke

- 目的：验证数据到指标的完整链路
- 样本/epoch：TBD
- 通过条件：无 NaN、保存与评测正常、输出形状正确

### Proxy

- 固定子集生成规则：TBD
- seed：TBD
- baseline：TBD
- 唯一改动：TBD
- 通过阈值：TBD
- 淘汰条件：TBD

### Full

- 数据与划分：TBD
- 训练预算：TBD
- seeds/repeats：TBD
- 主结果：TBD
- 消融：TBD
- 效率：TBD
- 失败分析：TBD

## 公平性检查

- [ ] 未在测试集调参
- [ ] baseline 与方法使用一致评测脚本
- [ ] 训练预算差异已说明
- [ ] 所有指标方向与单位已核对
- [ ] 图表可从原始结果重建
