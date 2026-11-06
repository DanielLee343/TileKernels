# hidev 的 TileKernels 环境

环境已部署在`/workspace/tilekernels-env-20261101`。已在 hidev 的 Ascend 950PR 上跑通一个原生 SwiGLU smoke。

## 使用

在 hidev 的 shell 中执行：

```bash
source /workspace/tilekernels-env-20261101/activate.sh
python -B /workspace/tilekernels-env-20261101/smoke_swiglu.py
```

默认 shell 原来的 CANN 9.1 和 Python 3.11 保留。使用这个环境前，需要执行上面的`source`。没有修改默认 CANN 链接或驱动。

## 安装版本

| 组件 | 实际版本 |
|---|---|
| Python | 3.12.3 |
| CANN toolkit / 950 ops | 9.2.1，安装在本项目目录下 |
| PyTorch | 2.13.0+cpu |
| torch_npu | 2.13.0 |
| TileLang | 0.1.15，官方 wheel 的 Ascend 后端 |
| TileKernels | main 的`c1cf914a82e6901c679445f872051ce44ac2cc63`，源码无修改 |
| NumPy / ml-dtypes | 1.26.4 / 0.5.4，满足该 SDK 和 TileLang 的共同要求 |

`pip check`通过。完整版本清单见本地备份`experiments/hidev-setup-20261101/backup/requirements-frozen.txt`。

不需要 CUDA。本次没有安装 CUDA Toolkit 或 NVIDIA Python 包，`torch.version.cuda`为`None`。使用方式与[官方 Ascend 后端说明](https://github.com/tile-ai/tilelang/blob/v0.1.15/tilelang/ascend/README.md)一致。本次直接安装 TileLang wheel；smoke 执行时由 TileLang 调用 CANN 编译 NPU kernel。

## smoke 的实际范围

- 算子：普通 SwiGLU，无量化、clamp 或路由权重。
- BF16 输入`[128,4096]`，输出`[128,2048]`。
- 固定种子20261101。本次262,144个输出与CPU参考完全一致，最大绝对误差为0。
- 设备为`Ascend950PR_9579`；已生成`kernel.aibin`与原生主机调用库`executable.so`，并记录其SHA256。
- 本次只完成这一个case的编译、设备执行和有限数值核对；未跑此前100条case或性能计时。

## 记录与备份

hidev 保留`smoke-result.json`、`environment-verified.json`、`requirements-frozen.txt`、`logs/`及编译缓存。PC备份在`D:/puma_v2/experiments/hidev-setup-20261101/backup/`，另有压缩证据包`hidev-evidence.tar.gz`。

安装过程遇到的Python路径问题已记入项目`错题本.md`。共享资源实际位于`/workspace/shared_assets`，没有用于本次环境的软件包，未修改该目录。
