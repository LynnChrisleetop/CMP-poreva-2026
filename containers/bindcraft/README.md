# BindCraft 修复版运行镜像

本次修复使用独立 Python 3.10 环境，固定 Python 路径 `/opt/bindcraft-env/bin/python`。镜像内含 BindCraft 固定源码、ColabDesign、PyRosetta、10 份 AlphaFold2 权重，以及 JAX 0.4.35 / jaxlib 0.4.34 / CUDA 12 插件。具体依赖见 requirements-cuda.txt 和验证报告。

## 验证边界

完整 CPU 自检已通过，包括 BindCraft functions 导入、JAX CPU 运算、PyRosetta 读取三聚体、权重 SHA256、JAX 插件依赖版本及 ptxas 启动。没有申请 GPU，没有运行设计。GPU/CUDA/驱动实机兼容性未验证，不能将 CPU 自检视为 GPU 已跑通。

默认入口为 CPU 自检：

```bash
docker run --rm IMAGE cpu-check
```

实际输入检查也不使用 GPU（挂载原始数据集目录）：

```bash
docker run --rm -v /path/to/tnfa_dataset:/trisol/input/datasets/ds-0:ro IMAGE validate-input
```

以后在明确恢复 GPU 任务时，Trisol 的容器命令使用 `/bin/bash /opt/poreva/bin/entrypoint.sh design`。不再传递内嵌 base64 或长 Python 单行代码。输出在 `/trisol/output`，默认设计限时 3600 秒，失败不自动重试。`design` 会先做完整预检并要求 JAX 发现 GPU，否则退出。

## 构建文件和二进制产物

Git 仓库只保存 Dockerfile、入口脚本、依赖版本和验证报告。环境、权重、安装包、镜像归档不提交 Git。

本次 CPU 构建上下文位于：
`/opt/poreva-cpu-cache/image-build-20261113/context/`

Dockerfile 使用明确的本地输入：
- `bindcraft-env.tar`：已验证的 CPU 环境通过 conda-pack 重定位到 /opt/bindcraft-env。
- `cuda-cache.tar`：对已有 NVIDIA 包按 RECORD 校验后提取的库；来源见 cuda-cache-provenance.json。
- `cuda-wheels/`：从 PyPI/镜像下载、与 PyPI SHA256 一致的补充 wheel；见 cuda-wheel-manifest.json。
- `BindCraft/`：固定源码，不含用户主目录。
- `params/`：10 份已校验权重。
- `app/`：本目录的入口、检查脚本、配置和公开结构测试样本。

具备 Docker 构建环境时，可在上述完整上下文中执行：

```bash
docker build -t poreva-bindcraft:20261113-cuda12 .
```

本机使用 Buildah 在 CPU 上完成构建。构建过程未复制 SSH、Vouch、Trisol 登录信息或其他用户主目录。验证日志见本机 `/opt/poreva-cpu-cache/image-build-20261113/reports/`。

## GitHub 与 Trisol 的区别

`https://github.com/LynnChrisleetop/CMP-poreva-2026` 是代码仓库，不是容器镜像拉取地址。修复镜像尚未推送或注册到 Trisol 的镜像目录。使用前需要将镜像发布到团队可访问的容器仓库，并按平台要求注册镜像引用。不要把 `.oci.tar` 等大文件通过 git add -f 提交到代码仓库。

## 本次镜像产物

OCI 镜像目录：`/opt/poreva-cpu-cache/image-build-20261113/poreva-bindcraft-oci`，标签 `20261113-cuda12`，约 7.52 GiB。所有 OCI blob 的 SHA256 已核验，skopeo inspect 已通过。镜像摘要：`sha256:f5f22e3cd9872f0da98299e7cbdd6b560405a3e8d6bba84faac92fb12e93850e`。采用目录格式以避免归档时额外磁盘占用。尚未发布到任何镜像仓库。
