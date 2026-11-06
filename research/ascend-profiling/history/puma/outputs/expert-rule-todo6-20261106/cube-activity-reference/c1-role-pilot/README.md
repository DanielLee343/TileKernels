# C1 同合同 Cube 角色与字段试采入口

本包准备在 950PR / CANN 9.2.0、同物理卡上，对固定 `[256,256]` FP16 矩阵乘执行两臂试采。CANN 使用 `torch.mm`，Triton 原样调用既有 `c1-exact/matmul_demo.py`。两臂读取同一份 1/2 整数输入，全部 65,536 个输出与整数黄金参考逐位比较。每个阶段都保留完整输出。

执行顺序为两臂独立正确性 → 两臂普通 trace → 两臂 BasicInfo → 两臂角色准入 → 两臂各一次 Default → Default 字段检查。普通 trace 的 `AI_CORE` 标签不能单独证明纯 Cube；同时要求 BasicInfo 为 `cube` 且 block 数匹配。BasicInfo 与 trace 是不同调用，这种关联目前是运行合同、输入、源码和任务维度的证据，尚未直接证明两次调用加载了相同设备 ELF。只有上述角色准入成功后，才开始两臂 Default。

本包仅为开发字段试采。一次 Default 不能支持比较谁快，也不决定专家、参考阈值或客户是否还有优化空间。普通 trace 如果出现多个计算任务、BasicInfo 为 mixed/vector、任何输出或 ND 不匹配，现场停在对应失败证据，不剔除额外任务强行进入 Default。Triton 教学实现与当前 CANN 9.2.0 / Triton 环境是否兼容尚未实机确认，导入或编译失败即保留现场错误。

## 输入及实现

复用 `outputs/expert-rule-todo5-20261106/cube-mix-expert-intake/c1-exact/` 下现有三文件，不能编辑或覆盖。原文件 SHA256：

| 文件 | SHA256 |
|---|---|
| run.py | `cea1822476618578a11004d30909d3ff57c7417829da3ecea0449d51d7c4f838` |
| fixture.py | `f3bbead8a517852e5573b639f8252dec14a1da91c824c97ffae1ab303251afd7` |
| matmul_demo.py | `340d51f935e3ad47d2f13c3f374a47c201c9d6afd3fb845d61fdb21b2d8661fc` |

`run.py` 是原独立正确性入口。`application.py` 同样调用原来的 `torch.mm` 或 `tiled_matmul`，标记一次 `c1_exact_target`，BasicInfo/Default 前执行五次应用预热。额外保留输入散列、全部输出、tensor shape/stride/dtype/format、Python、包版本及进程映射。`gate.py` 按记录逐位复算文件散列，检查上述源码 SHA、各阶段运行时映射和两个关键库的文件 SHA。

## 现场执行合同

由「评测体系 (2)」负责现场执行。先按已有共同项目锁、物理卡/BDF 映射、持续空闲和过程中竞争监控程序准入，采集中发现竞争按现有规则停止并归档。下面的应用和 `gate.py` **不负责实现上述设备门、外部进程监控或自动串行队列**。开始前须独立记录和核对现场激活路径 `/data2/lyuze/tilekernels-cann920-20261106/activate.sh`、物理卡及单卡可见映射；不能把 `run.py` 中命令行自声明的 PCI 当实测映射。

记录实际 `msprof op --version` 与所用 profiler 路径，核对已登记构建 `884ac969494a186a9c63ac45c4c39ad7289b3215`。`CANN_PY` 是 9.2.0 环境 Python，`TRITON_PY` 是可加载同一 9.2.0 的 Triton Python。两者可以指向同一路径。必须真实记录两者版本与进程映射，若 Triton 环境不可用，保留错误并停止。使用新空工作目录，不覆盖先前采集。

下列示例展示命令结构；`SITE`、`SRC`、`RUN`、两条 Python、设备和 BDF 由现场按真实路径设置。`SRC` 必须指向保留原始哈希的 c1-exact 三文件，`SITE` 是本包路径。所有阶段在同一冻结的工具、设备和 fixture 下进行。

```bash
set -eu
source /data2/lyuze/tilekernels-cann920-20261106/activate.sh
export ASCEND_RT_VISIBLE_DEVICES=6
CANN_ROOT=/home/pkg/cann920/cann-9.2.0
test "$(readlink -f "$ASCEND_HOME_PATH")" = "$(readlink -f "$CANN_ROOT")"
test ! -e "$RUN"
mkdir -p "$RUN/cann" "$RUN/triton"
msprof op --version > "$RUN/msprof-version.txt"
grep -F '884ac969494a186a9c63ac45c4c39ad7289b3215' "$RUN/msprof-version.txt"
sha256sum "$SRC/run.py" "$SRC/fixture.py" "$SRC/matmul_demo.py" > "$RUN/source-sha256.txt"
"$CANN_PY" -B "$SRC/fixture.py" "$RUN/fixture" > "$RUN/fixture-sha256.json"
g++ -std=c++17 -I"$CANN_ROOT/include" "$SITE/format_nd.cpp" -o "$RUN/format_nd"
"$RUN/format_nd" > "$RUN/format_nd.txt"
NDFMT=$(cat "$RUN/format_nd.txt")
```

在目标真实 CANN 头文件编译 `format_nd.cpp` 并保存命令、输出、头文件来源和 SHA，得到 ND 枚举值。若编译失败，或无法关联 `torch_npu.get_npu_format` 的枚举语义，停在格式不明，不能仅假设 ND 编号。生成 fixture 是纯 CPU 运算。

先执行两臂独立正确性。`--device 0` 对应单卡可见后的逻辑设备，`--pci` 由独立映射证据核对：

```bash
"$CANN_PY" -B "$SRC/run.py" cann "$RUN/fixture" "$RUN/cann/exact" --device 0 --pci "$BDF" > "$RUN/cann/exact.log" 2>&1
"$TRITON_PY" -B "$SRC/run.py" triton "$RUN/fixture" "$RUN/triton/exact" --device 0 --pci "$BDF" > "$RUN/triton/exact.log" 2>&1
```

再按同一合同逐臂执行普通 trace 和 BasicInfo。以下用 shell 函数给出完整参数，按 `collect_role cann "$CANN_PY"`、`collect_role triton "$TRITON_PY"` 串行调用，并保留日志及实际命令。每条现场 profiler 命令还须纳入已有进程组与竞争监控，失败立即终止本次，不自动重试。

```bash
collect_role() {
  role=$1
  py=$2
  msprof --output="$RUN/$role/trace" --task-time=on --runtime-api=on --ascendcl=on --msproftx=on \
    "$py" -B "$SITE/application.py" "$role" trace --source-dir "$SRC" --fixture "$RUN/fixture" --out "$RUN/$role/trace-app" \
    > "$RUN/$role/trace.log" 2>&1
  msprof op --output="$RUN/$role/basic" --aic-metrics=BasicInfo --replay-mode=kernel \
    --mstx=true --mstx-include=c1_exact_target --launch-count=1 --warm-up=5 \
    "$py" -B "$SITE/application.py" "$role" basic --source-dir "$SRC" --fixture "$RUN/fixture" --out "$RUN/$role/basic-app" \
    > "$RUN/$role/basic.log" 2>&1
}
collect_role cann "$CANN_PY"
collect_role triton "$TRITON_PY"
"$CANN_PY" -B "$SITE/gate.py" roles --root "$RUN" --fixture "$RUN/fixture" \
  --nd-format "$NDFMT" --physical-card 6 --cann-root "$CANN_ROOT" > "$RUN/roles.json"
```

必须先由主会话复核 `roles.json`、普通 trace、BasicInfo 和实机设备/格式/工具证据。两臂都通过后，分别从该报告取各自的 `basic_kernel` 作为 `CANN_KERNEL` / `TRITON_KERNEL`，然后每臂只采一次 Default。这里使用与 BasicInfo 相同的应用预热、kernel replay、MSTX、工具 warmup 和 launch 次数。工具默认 L2 行为需从实际日志单独记录，不能仅由命令行推断。

```bash
collect_default() {
  role=$1
  py=$2
  kernel=$3
  msprof op --output="$RUN/$role/default" --aic-metrics=Default --replay-mode=kernel \
    --mstx=true --mstx-include=c1_exact_target --kernel-name="$kernel" --launch-count=1 --warm-up=5 \
    "$py" -B "$SITE/application.py" "$role" default --source-dir "$SRC" --fixture "$RUN/fixture" --out "$RUN/$role/default-app" \
    > "$RUN/$role/default.log" 2>&1
}
collect_default cann "$CANN_PY" "$CANN_KERNEL"
collect_default triton "$TRITON_PY" "$TRITON_KERNEL"
"$CANN_PY" -B "$SITE/gate.py" defaults --root "$RUN" --fixture "$RUN/fixture" \
  --nd-format "$NDFMT" --physical-card 6 --cann-root "$CANN_ROOT" > "$RUN/defaults.json"
```

`gate.py defaults` 重新检查两个角色的所有前置证据，再检查 Default BasicInfo 的纯 Cube 类型、设备、block 数、名称，核对 `PipeUtilization.csv` 每个 Cube 行唯一、活动量有限且非负，并保留表格哈希和活动量总和。若无活动数据则失败。通过表示此固定例的导出字段可读，不能据此证明 event ID 和每项 PMU 事件有效性。

## 本地检查和待实机确认

```powershell
python -B -m unittest discover -s outputs/expert-rule-todo6-20261106/cube-activity-reference/c1-role-pilot -v
```

本地合成测试覆盖正确输出、错数据、非 ND、额外或混合任务、错误设备/类型/维度/名称、缺失/重复/异常活动行。测试使用合成 2 作为 ND 数字，现场值来自实际目标头文件，并不由测试决定。

尚待现场核验实际 NPU 格式、加载库、Triton 编译兼容、普通 trace 的完整任务列表、BasicInfo 到真实执行二进制的对应、Default 输出、设备竞争及 PMU 字段。源哈希、相同 block 数和相同目标名不能独立证明跨调用执行的设备 ELF 相同。保留实际 profiler 构建、原始日志、输出、maps、计数表和每次设备证据供主会话验收。
