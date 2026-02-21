# CUDA 13.0 Compatibility Analysis

## Hardware

- **GPU:** NVIDIA GB10 (Blackwell architecture, SM 12.1)
- **Driver:** 580.126.09
- **CUDA:** 13.0
- **VRAM:** ~128GB unified

## The Problem

Standard PyTorch releases (including `cu121` wheels from pytorch.org) do **not** include
CUDA 13.0 kernels for Blackwell SM 12.0/12.1. Installing `torch --index-url
https://download.pytorch.org/whl/cu121` on this machine produces a CPU-only PyTorch —
`torch.cuda.is_available()` returns `False`.

This is the critical flaw in prior implementations using `nvidia/cuda:12.1.1-*` base images.

## The Solution

Use **NVIDIA's official NGC PyTorch container** as the Docker base image:

```
FROM nvcr.io/nvidia/pytorch:25.05-py3
```

This container ships PyTorch 2.9.x built directly against CUDA 13.0 with native SM 12.0/12.1
support. It is validated on GB10 hardware (e.g., the `vllm/Dockerfile.blackwell` uses the same
base).

Set the following env var to inform any CUDA extension compilations:

```
ENV TORCH_CUDA_ARCH_LIST="12.0 12.1"
```

## Images to AVOID

| Image | Reason |
|---|---|
| `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` | Max CUDA 12.1, no SM 12.1 kernels |
| `nvidia/cuda:12.x.x-*` | All 12.x images lack CUDA 13.0 |
| PyTorch cu121/cu124 wheels from pytorch.org | No CUDA 13.0 wheels as of 2026-02 |

## Do NOT Downgrade CUDA

Downgrading CUDA would require using an older driver (580.x supports CUDA 13.0; older drivers
would not fully support the GB10 GPU). **Do not downgrade without explicit user instruction.**

## Verification

Inside the running container:

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"
# Expected: True  13.0
```
