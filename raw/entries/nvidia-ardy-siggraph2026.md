---
id: nvidia-ardy-siggraph2026
date: 2026-09-22
source_type: paper
source_path: raw/papers/nvidia-ardy-siggraph2026.pdf
title: "ARDY: Autoregressive Diffusion with Hybrid Representation for Interactive Human Motion Generation"
authors:
  - Kaifeng Zhao
  - Mathis Petrovich
  - Haotian Zhang
  - Tingwu Wang
  - Siyu Tang
  - Davis Rempe
year: 2026
venue: "ACM Transactions on Graphics (SIGGRAPH 2026), Vol. 45, No. 4, Article 86"
arxiv_id: ""
doi: "10.1145/3811284"
tags:
  - 人体动作生成
  - 扩散模型
  - 自回归生成
  - 交互式动作
  - 人形机器人
  - 运动规划
  - NVIDIA
absorbed: true
---

## 元数据

- 项目页面：https://research.nvidia.com/labs/sil/projects/ardy/
- 代码：https://github.com/nv-tlabs/ardy
- 模型：https://huggingface.co/collections/nvidia/ardy

## 摘要

ARDY 是一个流式人体动作生成框架，支持在线文本提示和灵活的运动学约束，同时保持实时响应。核心是混合动作表示（显式根运动 + 潜在身体嵌入）与两阶段自回归扩散去噪器的组合。在 RTX 4090 上，4 步扩散模型平均生成延迟 33ms。

## 关键内容

### 问题与动机

现有离线生成方法（Kimodo、MaskControl）可精确控制但推理太慢；现有在线方法（CAMDM、AMDM、DiP）实时但牺牲可控性，或历史上下文窗口过短（DiP 仅 1s 历史/2s 未来），无法处理复杂文本语义和长程运动学目标。

### 混合动作表示

每帧动作 x = (mroot, xbody)：
- mroot ∈ R⁵：全局根位置 p∈R³ + cos/sin 航向角。显式表示，支持直接覆写以实现根轨迹精确控制，避免局部速度积分的累积误差。
- xbody ∈ Rᴸ：从学习到的 tokenizer 编码得到的紧凑潜在向量。

### 动作 Tokenizer

- 补丁大小 P=4 帧，将连续帧拼接为一个向量
- 编码器 + 解码器均为 8 层因果 Transformer（latent dim 512）
- 解码器将全局根运动转换为局部表示（角速度、线速度、高度），显著减少脚部滑动
- 支持三种变体：连续 AE、VAE、FSQ（默认，64 个离散等级/维度，更稳定）
- 训练损失：重建损失 + 脚部滑动损失 Lskate（惩罚接触时足端速度）

### 两阶段自回归去噪器

在每个去噪步骤 k 内交错执行：
1. Root Transformer：预测干净的全局根运动 m̂root
2. Body Transformer：以 m̂root 为条件，预测干净的潜在身体 token x̂body

两个分支输出拼接 → 下一个去噪步骤的输入。设计动机：给定干净根运动，预测身体动作是更简单的任务。

总训练损失：L = Lhybrid + Ldec + Lgoal + Lconsist
- Lhybrid：混合 token 预测误差（smooth L1）
- Ldec：解码后显式身体运动误差
- Lgoal：约束命中误差（只惩罚约束区域）
- Lconsist：预测关节位置与前向运动学结果一致性

### 空间约束条件化

约束表示为 masked 显式动作序列（非约束位置填零），带二值掩码 v。
- 根运动约束：直接覆写噪声 token 中的根特征（高精度）
- 身体/末端执行器约束：与 noisy token 沿特征维度拼接
- 长程约束（超出当前预测窗口）：作为额外 token 输入，自然外推未来目标对当前窗口的影响，无需额外 RL 策略

### 模型规模与训练

- 去噪器：~156M 参数（8 层、8 头、latent 1024）
- 文本编码：LLM2Vec（基于 Llama-3-8B-Instruct）
- 最长上下文：8 秒（训练序列最长 10s，生成窗口 G 随机采样）
- 训练：4×A100-SXM4-80GB，batch 512，1M 步

## 关键证据定位

- Table 1：与 8 个方法的能力对比（实时/在线文本/约束类型/上下文长度）
- Table 2：消融——混合表示、全局转局部解码器、两阶段架构各自的贡献
- Table 3：超参数分析——生成窗口/扩散步数/tokenizer patch 大小/FSQ 配置
- Figure 2：Tokenizer 结构图
- Figure 3：两阶段去噪器结构图
- Figure 5：延迟感知重规划机制
- Figure 6：多种运动学约束定性结果

## 原始来源

- PDF：raw/papers/nvidia-ardy-siggraph2026.pdf
- 项目页面：https://research.nvidia.com/labs/sil/projects/ardy/
- DOI：https://doi.org/10.1145/3811284
