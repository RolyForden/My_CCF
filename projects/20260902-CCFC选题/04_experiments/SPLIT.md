# 数据划分（已冻结，2026-09-10）

> 冻结规则：3RScan 29 个有效场景（剔除损坏的 `0ad2d399-...`）。
> - **dev**：已用于前期 α 比较/基线观测的 3 个场景，降级为开发集，不再作为最终评测。
> - **train/val/final_test**：由剩余 26 个场景按 `random.seed(42)` 洗牌划分；train 前 4 个为历史训练场景（强制保留在 train）。
> - **final_test 从未在任何实验中被查看**，只在方法定型后运行一次。

## dev（3 场景，已使用，不参与最终评测）
- 09582225-e2c2-2de1-9564-f6681ef5e511
- 09582244-e2c2-2de1-956c-357092d949d1
- 0958224e-e2c2-2de1-943b-38e36345e2e7

## train（16 场景）
- 02b33dfb-be2b-2d54-92d2-cd012b2b3c40
- 02b33e01-be2b-2d54-93fb-4145a709cec5
- 0958220d-e2c2-2de1-9710-c37018da1883
- 09582212-e2c2-2de1-9700-fa44b14fbded
- 0cac75ad-8d6f-2d13-8c74-5de4dfc4affc
- 0cac7580-8d6f-2d13-8c9d-d45247b5244b
- 0cac755e-8d6f-2d13-8c6a-c0979ca34a4f
- 0ad2d386-79e2-2212-9b40-43d081db442a
- 0cac7564-8d6f-2d13-8cb2-8b01c0a1b3d5
- 0ad2d3a3-79e2-2212-9a51-9094be707ec2
- 0cac75a7-8d6f-2d13-8fdc-083ff44d10fb
- 0cac7549-8d6f-2d13-8d56-b895956f571a
- 0cac7558-8d6f-2d13-8fe1-c8af0362735d
- 0ad2d382-79e2-2212-98b3-641bf9d552c1
- 0ad2d39b-79e2-2212-99ae-830c292cd079
- 0cac75c4-8d6f-2d13-8c37-fcfaf141ae5a

## val（5 场景，用于消融与超参选择）
- 0cac7574-8d6f-2d13-8db6-4304f437e6d5
- 0cac759b-8d6f-2d13-8e3b-2e3bc1ee1158
- 0cac75b1-8d6f-2d13-8c17-9099db8915bc
- 0cac753c-8d6f-2d13-8e27-e0664fc33bb9
- 0cac7578-8d6f-2d13-8c2d-bfa7a04f8af3

## final_test（5 场景，从未查看，方法定型后只跑一次）
- 0cac75c8-8d6f-2d13-8c08-b3c40c58e0f7
- 0cac7536-8d6f-2d13-8dc2-2f9d7aa62dc4
- 0ad2d38f-79e2-2212-98d2-9b5060e5e9b5
- 0cac7597-8d6f-2d13-8c9c-6f8542021d5c
- 0cac755a-8d6f-2d13-8fed-b1be02f4ef77
