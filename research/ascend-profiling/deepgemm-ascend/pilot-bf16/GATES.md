# BF16 GEMM 小批试采验收

OWNS: research/ascend-profiling/deepgemm-ascend/pilot-bf16/**

范围：DeepGEMM-Ascend 普通 BF16 NT GEMM 的一小批官方形状，不带 bias 和累加。

- [x] G1: case 清单固定输入合同、来源、精度口径和环境。
  EVIDENCE: cases.json、environment.json 和 README.md。
- [x] G2: 采集脚本对精度失败、目标身份不符和采集不完整拒绝标记通过。
  EVIDENCE: 5 项 test_pilot_contract.py 测试通过，含精度、输入/输出和二进制负例。
- [x] G3: 所有计划 case 完成精度检查、Default 采集和独立验收，或保留明确失败原因。
  EVIDENCE: 6/6 采集与精度通过，verify.py 检验 114 个原始文件，audit.json 保存独立验收记录；指标有效性警告详见 RESULT.md。
- [x] G4: profile 原始数据、结果、脚本和清单同步私仓，hidev 和 GitHub 可核对。
  EVIDENCE: 数据提交 96a1fd006c6327739ec7a75b12eafffe25d82fc0 已推送 GitHub；hidev、A5 同步该提交后均通过 verify.py，6 个 case、114 个原始文件。
