---
title: GR00T Action Cascade：VLM 与动作扩散系统如何协作
id: nvidia-gr00t-action-cascade
type: concept
created: 2026-11-07
last_updated: 2026-11-07
stage: budding
verified_date: 2026-11-07
institution: NVIDIA Research
tags: [NVIDIA, GR00T, VLA, Flow Matching, Diffusion Transformer]
---

# GR00T Action Cascade：VLM 与动作扩散系统如何协作

[打开本地论文 PDF](../../../raw/papers/nvidia-series/nvidia-gr00t-n1-2503.14734.pdf)


GR00T N1 系列把机器人策略拆成两个时间尺度：System 2 负责理解图像和语言、形成高层条件；System 1 负责在机器人状态约束下生成连续动作。这种设计解决的是频率冲突：语义推理不必每个控制周期运行，动作控制又不能等待一整个视觉语言模型完成复杂推理。

## 1. 输入、接口和输出

在时刻 $t$，System 2 接收图像历史 $I_{t-T:t}$、语言指令 $ell$ 和可选机器人状态 $s_t$，产生条件 token $c_t$。System 1 接收 $c_t$、当前状态和带噪动作块 $x_\tau$，输出动作速度场或去噪方向：

$$
v_\theta(x_\tau,c_t,s_t,\tau)\approx a-\epsilon.
$$

这里 $a\in\mathbb R^{H\times d_a}$ 是未来 $H$ 步动作，$\epsilon$ 是噪声，$\tau$ 是生成过程的时间变量，不是机器人控制时间。不同 embodiment 的状态和动作维度由形态特定的 encoder/decoder 投影到共享隐空间，再还原为对应机器人的控制接口。

## 2. 为什么使用两个系统

System 2 的视觉语言模型适合回答“场景中有什么、指令要求什么、下一阶段做什么”，但直接让它高频输出每个关节动作会带来计算延迟和连续性问题。System 1 的 DiT 或流/扩散动作头可以专注于动作块内的相关性、状态条件和高频执行，但它不需要承担完整语言推理。

因此，策略可以近似写成：

$$
 p(a_{t:t+H}\mid I_{\le t},\ell,s_t)
 =\int p_\theta(a_{t:t+H}\mid c_t,s_t)\,p_\phi(c_t\mid I_{\le t},\ell)\,dc_t.
$$

这是解释系统分工的条件生成分解，不代表两个网络在物理上完全独立。System 2 的条件表示、动作头的状态编码和形态适配器仍共同决定最终控制质量。

## 3. GR00T N1 的训练数据如何进入同一动作头

N1 使用数据金字塔：真实机器人轨迹提供动作监督；仿真轨迹扩大环境和任务变化；视频生成轨迹提供反事实动作过程；人类视频通过 LAPA 产生潜在动作标签。对于没有显式关节动作的视频，LAPA 不是测得的真实机器人控制量，而是从当前帧和未来帧中学习到的隐变量：

$$
 z_t=E_\psi(x_t,x_{t+H}),\qquad
 \hat x_{t+H}=D_\psi(x_t,z_t).
$$

训练好的编码器可以为视频提供可预测的 latent action。它帮助 VLA 学习“怎样从当前状态走向未来状态”，但不能直接说明某台机器人应该发送哪一个关节角；真实机器人数据和形态适配器仍负责把隐动作接到具体控制接口。

## 4. 版本变化应怎样理解

- **N1** 建立 VLM + DiT、LAPA 和数据金字塔的组合。
- **N1.5** 冻结完整 VLM，并用 FLARE 对齐未来潜在表示，减少无动作视频训练对视觉语言骨干的破坏。
- **N1.6** 换用 Cosmos-2B、扩大动作头容量，引入相对状态动作和更多双臂、人形、全身数据。
- **N1.7** 使用 Cosmos-Reason2-2B，并将动作进一步统一为相对 EEF 增量，为 EgoScale 的人类视频迁移提供共同表示。

这些改动分别作用于骨干、动作头、数据监督和动作表示，不能笼统说成“模型变大所以更强”。

## 5. 相对 EEF 动作为什么关键

绝对关节角依赖机器人结构，人的手部视频无法直接提供；相对末端动作描述“末端相对于当前状态向哪里移动、怎样旋转”，更接近跨本体共享的任务关系。设末端位姿为 $T_t=(R_t,p_t)$，相对动作可写为：

$$
\Delta p_t=p_{t+1}-p_t,\qquad
\Delta R_t=R_t^\top R_{t+1}.
$$

这统一了人类视频与机器人轨迹的一部分语义，但不解决可达性、夹爪开合、碰撞和基座运动。N1.7 的统一表示仍需要本体适配、控制器和闭环观察共同完成执行。

## 6. 实现边界

真实部署还要处理动作块长度、生成步数、System 2 更新频率、System 1 控制频率、归一化统计量和机器人状态延迟。论文中的 2B/3B 参数、H100 训练时长、动作频率和任务成功率都属于各自实验设置，不能直接迁移到任意硬件。

本文依据 NVIDIA GR00T N1 论文、GR00T 系列材料和固定 PDF 记录整理；未复现训练和真机评测。版本关系见 [GR00T 系列综述](../../01-comprehensive/01-embodied-ai/nvidia-gr00t-series-overview.md)。
