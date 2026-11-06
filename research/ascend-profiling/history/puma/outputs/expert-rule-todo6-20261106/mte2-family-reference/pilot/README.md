# 配对 A 可辨识性 pilot：离线包

仅供后续明确安排现场执行；当前没有访问远端或 NPU。仅两臂 I0/I16 各一次 Default，每次 profiler 前各做独立单调用准入；没有自动复采。I0/I16 输入 stride 分别为 4096/4112，输出均为连续 4096；shape [128,4096]，BF16，weight [4096]，种子 20261106，eps=1e-6，其他调用参数沿用 D1。固定输入哈希分别为 `de4bacfab422cd53119861129b486bde426e790d8c26a34fda50671ceef694fd` 和 `98b7decd8bbb5d6283b774f82fa5a7a730ae01b1d043fff68d3c7919f3b4d318`。输出预填 -127；逐元素参考检查、前后 guard、全部写入、输入与 weight 未修改，且两臂输出逻辑值哈希必须一致。每次记录 input/output/weight 的数据与 backing 起始地址、backing 字节数、shape、stride、元素字节数；程序由这些值核验有效跨度位于 backing 内，三者起始地址模 128 均为零。不同进程绝对地址不要求一致，缓存、TLB、分配及布局仍可能改变，不能假定相同。

入口：目标机正确激活后 `python -B runner.py --run-root <不存在的新目录>`；只在完整复制本目录并核验以下 SHA256 后运行。运行器要求物理卡 5/E1、CANN 9.2.0、msprof op 26.2.0 build `884ac969494a186a9c63ac45c4c39ad7289b3215`、干净 TileKernels `c1cf914a82e6901c679445f872051ce44ac2cc63`，使用单 AIV kernel、warmup 5、kernel replay、MSTX；提前与结束检查进程，保留状态、命令、日志和原表，检查 56 行及源码/host/device hash。需要目标机独立确认工具路径、可见映射、单调用及 profiler 全流程；CPU 测试未证明设备可执行。结果中 `eligible_for_separate_repeat_design` 只有两次均未标记且 N 相等 G 不等才为真；通过也只表示可另行设计复采，不自动运行或证明关系稳定。

复用 TODO5 `p05-dev-pack/rms_wrapper.py` 的生成输入、公共 API、准入、guard、计数/产物与地址记录；复用 `runner_ab.py` 的环境、进程、单调用、Default 捕获与 56 行核验，副本仅增加两 case、固定 out stride、限定 pilot 调度。`frozen` 下两个参考文件是原文件副本，原文件未改。wrapper 保留历史分支，但 runner 只接受 I0/I16；不运行其他分支。

| 文件 | SHA256 |
|---|---|
| runner.py | 8eeae7e102b6e777960ad5130ea7d89244ae86b3e9ecb969cd427c09b72f3a03 |
| rms_wrapper.py | 479697a106309c8cbbfd2c3fadebadb3b1c075b9575c261ad67b0ea610dd9fd8 |
| test_pilot.py | 3e1facfaee783d0eac2aaf2cd3c4b2300fc6d7677eedbdec87a02f4f02afd827 |
| frozen/bridge-inputs.py | 7d05aaa197bb72336d07631c99fe82ee79981409386174319027b8db6b082095 |
| frozen/bridge-rmsnorm.py | b94b1eb9d0606b1e1bfbe52ef758fd9a15618516619c4ce901e2325e33119860 |

CPU 检查：`python -B test_pilot.py`，3 项通过，检查两臂 stride、固定输出和没有复采调度；不验证 NPU 精度或采集。数值目标只是先判断实际 N 相等且 G 不等，不保证成立。任何失败或干扰保留证据，不能换参数凑结果；缓存目录在 run-root 内，结束后只清理确认可再生中间物，保留二进制、源和证据。

