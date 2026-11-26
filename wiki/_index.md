# 知识库索引

> 阅读入口已经迁移到 [HTML 博客首页](../site/public/index.html)。本文件保留为编辑与检查索引，文章页由生成器输出为 HTML。

## 主题综述 · 具身智能

- [π 系列 VLA：从连续动作到可控通用策略](01-comprehensive/01-embodied-ai/pi-series-overview.md)：时间线、模型主线、方法支线、差异与阅读顺序。
- [NVIDIA GR00T 系列：从双系统 VLA 到世界动作模型](01-comprehensive/01-embodied-ai/nvidia-gr00t-series-overview.md)：GR00T N1–N1.7、GR00T 2 WAM、EgoScale、SONIC、RoboTTT 与智能体路线的关系。

- [机器人价值函数与奖励模型：从技能可行性到策略改进](01-comprehensive/01-embodied-ai/robot-value-reward-overview.md)：按首次公开时间整理八个方法，比较评分对象、监督、部署与策略改进接口。

## 概念 · 具身智能

- [π₀：连续动作流模型](00-concepts/01-embodied-ai/pi-0-flow-vla.md)
- [FAST：频域动作序列标记化](00-concepts/01-embodied-ai/pi-fast-action-tokenization.md)
- [π₀.₅：异构共训练与开放世界泛化](00-concepts/01-embodied-ai/pi-05-open-world.md)
- [Knowledge Insulation 知识绝缘](00-concepts/01-embodied-ai/pi-knowledge-insulation.md)
- [RTC 实时动作分块](00-concepts/01-embodied-ai/pi-rtc-real-time-chunking.md)
- [π₀.₆ 与 RECAP 经验学习](00-concepts/01-embodied-ai/pi-06-recap.md)
- [人类视频到机器人控制的迁移](00-concepts/01-embodied-ai/pi-human-to-robot.md)
- [MEM 多尺度具身记忆](00-concepts/01-embodied-ai/pi-mem-memory.md)：高低层接口、语言摘要监督、视频时空注意力、本体历史与训练边界。
- [RLT 强化学习 Token](00-concepts/01-embodied-ai/pi-rlt-token.md)
- [π₀.₇ 可控通用策略](00-concepts/01-embodied-ai/pi-07-steerable.md)
- [GR00T Action Cascade：VLM 与动作扩散系统如何协作](00-concepts/01-embodied-ai/nvidia-gr00t-action-cascade.md)
- [GR00T 2：联合预测未来视频与动作的世界动作模型](00-concepts/01-embodied-ai/nvidia-gr00t-2-world-action-model.md)
- [NVIDIA SONIC：规模化运动追踪与人形全身控制](00-concepts/01-embodied-ai/nvidia-sonic.md)
- [EgoScale：用自中心视角人类视频缩放灵巧操控](00-concepts/01-embodied-ai/nvidia-egoscale.md)
- [RoboTTT：上下文缩放机器人策略](00-concepts/01-embodied-ai/nvidia-robottt.md)
- [NVIDIA ARDY：交互式人体动作生成](00-concepts/01-embodied-ai/nvidia-ardy.md)
- [ASPIRE：面向机器人的智能体技能发现](00-concepts/01-embodied-ai/nvidia-aspire.md)

- [Spectral Skills：可组合全身运动技能（项目预览）](00-concepts/01-embodied-ai/spectral-skills-preview.md)

### 机器人价值与奖励

- [机器人价值函数基础](00-concepts/01-embodied-ai/robot-value-functions.md)
- 2022-04-04：[SayCan：用技能价值约束语言规划](00-concepts/01-embodied-ai/robot-value-2022-saycan.md)
- 2024-11-07：[GVL：让视觉语言模型从打乱的视频中判断任务进度](00-concepts/01-embodied-ai/robot-value-2024-gvl.md)
- 2025-09-29：[SARM：用任务阶段对齐长程操作进度](00-concepts/01-embodied-ai/robot-value-2025-09-sarm.md)
- 2025-12-29：[Robo-Dopamine：从相对进度到策略不变奖励塑造](00-concepts/01-embodied-ai/robot-value-2025-12-robo-dopamine.md)
- 2026-02-22：[TOPReward：读取 Token 概率估计机器人任务进度](00-concepts/01-embodied-ai/robot-value-2026-02-topreward.md)
- 2026-03-02：[Robometer：用轨迹比较学习可迁移的机器人奖励](00-concepts/01-embodied-ai/robot-value-2026-03-robometer.md)
- 2026-04-03：[ARM：从进步、退步与停滞学习操作反馈](00-concepts/01-embodied-ai/robot-value-2026-04-arm.md)
- 2026-06-09：[SARM2：可复用动作阶段与奖励驱动的策略改进](00-concepts/01-embodied-ai/robot-value-2026-06-sarm2.md)

## 主题综述 · 经典机器人

- [机器人动作重定向综述](01-comprehensive/02-classical-robotics/motion-retargeting-overview.md)：表示与形态差异 → 带约束微分 IK → GMR / PyRoki / FRAX → 物理执行与评估。

- [刚体运动学基础](01-comprehensive/02-classical-robotics/rigid-body-kinematics.md)：位姿、速度、加速度、动力学与接触控制的关系和阅读路线。

## 概念与工具 · 经典机器人

- [刚体位姿与坐标变换](00-concepts/02-classical-robotics/rigid-body-pose.md)
- [刚体速度与加速度](00-concepts/02-classical-robotics/rigid-body-velocity-acceleration.md)
- [刚体的力、力矩与动力学](00-concepts/02-classical-robotics/rigid-body-dynamics.md)
- [阻抗控制与导纳控制](00-concepts/02-classical-robotics/impedance-admittance-control.md)
- [FRAX 与微分 IK](00-concepts/02-classical-robotics/frax-differential-ik.md)

## 概念 · 人工智能基础

- [从扩散模型到流匹配：从噪声到机器人动作](00-concepts/03-ai-foundations/diffusion-flow-action-generation.md)：从双路线例子讲清加噪、score、速度场、概率流与动作块执行。

- [KL 散度](00-concepts/03-ai-foundations/kl-divergence.md)
- [交叉熵损失函数](00-concepts/03-ai-foundations/cross-entropy.md)
- [马尔可夫决策过程 MDP](00-concepts/03-ai-foundations/mdp.md)
- [CNN 卷积神经网络](00-concepts/03-ai-foundations/cnn.md)
- [RNN 循环神经网络](00-concepts/03-ai-foundations/rnn.md)
- [注意力机制及变体](00-concepts/03-ai-foundations/attention-mechanisms.md)
- [激活函数](00-concepts/03-ai-foundations/activation-functions.md)
- [PEFT 参数高效微调](00-concepts/03-ai-foundations/peft.md)：图解全量微调的参数更新，区分训练与多任务部署开销。
- [多卡训练原理](00-concepts/03-ai-foundations/multi-gpu-training.md)

- [Online Learning、Offline Learning、On-policy 与 Off-policy](00-concepts/03-ai-foundations/online-offline-learning.md)：交互数据与参数更新、两个分类维度、BC 与离线 RL 的区别。

- [VAE 与 CVAE：从重建数据到生成多种可能](00-concepts/03-ai-foundations/vae-cvae.md)：潜变量、ELBO、重参数化、条件生成与机器人应用。

### Transformer 图解系列

- [Transformer 00：整体框架与各模块的作用](00-concepts/03-ai-foundations/transformer-00-overview.md)：先看全貌，再逐模块深入。

- [Transformer 01：Token、嵌入与上下文表示](00-concepts/03-ai-foundations/transformer-01-tokens-embeddings.md)
- [Transformer 02：Self-Attention：从 QKV 到加权读取](00-concepts/03-ai-foundations/transformer-02-self-attention.md)
- [Transformer 03：Multi-Head Attention 与 Transformer Block](00-concepts/03-ai-foundations/transformer-03-multihead-block.md)
- [Transformer 04：经典 Encoder–Decoder 架构](00-concepts/03-ai-foundations/transformer-04-encoder-decoder.md)
- [Transformer 05：位置编码：从正弦信号到 RoPE](00-concepts/03-ai-foundations/transformer-05-position-encoding.md)
- [Transformer 06：训练与自回归生成](00-concepts/03-ai-foundations/transformer-06-training-generation.md)
- [Transformer 07：KV cache 与注意力计算效率](00-concepts/03-ai-foundations/transformer-07-kv-cache-efficiency.md)
- [Transformer 08：BERT、GPT、ViT 与多模态接口](00-concepts/03-ai-foundations/transformer-08-model-families.md)

## 主题综述 · 人工智能基础

- [强化学习基础](01-comprehensive/03-ai-foundations/reinforcement-learning-basics.md)：保留完整讲解与 LaTeX 公式推导，重绘八张学习路线、交互与数值算法示意图。

## 来源与维护

- [π 系列来源与证据](../raw/entries/2026-11-06-pi-series.md)
- [动作重定向来源与证据](../raw/entries/2026-11-05-motion-retargeting.md)
- [GR00T 2 来源与证据](../raw/entries/2026-11-10-nvidia-gr00t-2.md)
- [更新记录](logs/2026-11-10.md)

- [界面更新记录：纵向列表](logs/2026-11-20.md)

- [网页维护记录](../site/CHANGELOG.md)
