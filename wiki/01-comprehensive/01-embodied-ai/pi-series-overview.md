---
title: π 系列 VLA：从连续动作到可控通用策略
type: comprehensive
id: pi-series
created: 2026-11-06
last_updated: 2026-11-06
stage: budding
verified_date: 2026-11-06
institution: Physical Intelligence（系列综述）
tags: [具身智能, VLA, Physical-Intelligence]
---

# π 系列 VLA：从连续动作到可控通用策略

π 系列的文章容易被读成一串版本号，但它实际由两条交错的路线组成：模型主线不断扩大泛化和上下文能力，方法支线分别解决动作表示、训练梯度、异步执行、经验改进和数据迁移。理解它们的关系，比把每篇论文的公式压进一篇长文更重要。每个对象的输入、公式、流程和实现细节放在独立[概念文章](../../00-concepts/01-embodied-ai/pi-0-flow-vla.md)中，本篇只回答“先后关系、差异和选择”。

## 1. 时间线：每次迭代改变了什么

| 时间 | 对象 | 主要问题 | 关键改变 |
|---|---|---|---|
| 2024-10 | [π₀](../../00-concepts/01-embodied-ai/pi-0-flow-vla.md) | VLM只会输出离散 token，机器人需要高频连续控制 | VLM + 动作专家 + 流匹配动作块；跨多本体训练 |
| 2025-01 | [FAST](../../00-concepts/01-embodied-ai/pi-fast-action-tokenization.md) | 逐维量化难以表达高频灵巧动作 | DCT 频域压缩 + BPE；让自回归动作训练更高效 |
| 2025-04 | [π₀.₅](../../00-concepts/01-embodied-ai/pi-05-open-world.md) | 在新家庭和新物体中泛化不足 | 异构机器人、子任务和视觉语言数据共同训练；高层子任务 + 低层连续动作 |
| 2025-05 | [Knowledge Insulation](../../00-concepts/01-embodied-ai/pi-knowledge-insulation.md) | 连续专家的随机梯度干扰 VLM 表示 | stop-gradient 只阻断专家到主干的反向路径 |
| 2025-06 | [RTC](../../00-concepts/01-embodied-ai/pi-rtc-real-time-chunking.md) | 大模型异步推理造成动作块跳变或等待 | 将流模型推理时的切块视为 inpainting，冻结重叠前缀 |
| 2025-11 | [π₀.₆ / RECAP](../../00-concepts/01-embodied-ai/pi-06-recap.md) | 模仿策略会积累真实执行错误 | 价值函数 + 优势条件化 + 自主经验与人工纠正的迭代 |
| 2025-12 | [人类到机器人迁移](../../00-concepts/01-embodied-ai/pi-human-to-robot.md) | 机器人数据昂贵，视频中的动作空间不同 | 以相对末端表示和子任务标签共同微调，研究跨场景/物体/任务迁移 |
| 2026-03 | [MEM](../../00-concepts/01-embodied-ai/pi-mem-memory.md) | 单帧策略无法跟踪十几分钟任务 | 近期视频记忆 + 长期语言事件摘要 |
| 2026-03 | [RLT](../../00-concepts/01-embodied-ai/pi-rlt-token.md) | 全 VLA 在线 RL 太大，精细阶段仍需快速适应 | 冻结 VLA，提取 RL token，训练轻量 actor-critic 编辑动作块 |
| 2026-04 | [π₀.₇](../../00-concepts/01-embodied-ai/pi-07-steerable.md) | 多源数据的策略、质量和接口互相冲突 | 用子目标、速度、质量、错误和控制模式组成可控提示 |

日期与论文版本以 Physical Intelligence 研究页和 arXiv 条目为准：[研究目录](https://www.pi.website/research)、[π₀](../../../raw/papers/pi-series/pi0.pdf)（[在线原文](https://arxiv.org/abs/2410.24164)）、[π₀.₅](../../../raw/papers/pi-series/pi05.pdf)（[在线原文](https://arxiv.org/abs/2504.16054)）、[π*₀.₆](../../../raw/papers/pi-series/pi06.pdf)（[在线原文](https://arxiv.org/abs/2511.14759)）、[π₀.₇](../../../raw/papers/pi-series/pi07.pdf)（[在线原文](https://arxiv.org/abs/2604.15483)）。

## 2. 模型主线：输出形式没有被一次性决定

### π₀：连续动作优先

π₀把 VLM 的视觉语言表示接到连续动作专家，用流匹配生成相关的动作块。它适合高频灵巧控制，代价是训练和推理需要迭代速度场，而且动作块边界与实时延迟尚未解决。详细结构、噪声约定和代码对应见[π₀概念文](../../00-concepts/01-embodied-ai/pi-0-flow-vla.md)。

### π₀.₅：数据与时间尺度扩展

π₀.₅的主要变化不是“换一个更大的动作头”，而是把 Web、子任务、多环境和跨本体监督放进同一训练配方。高层语言动作决定做什么，连续专家决定怎么动。它解决的是新场景和新物体泛化，不能被概括为长期记忆或自主 RL。[π₀.₅概念文](../../00-concepts/01-embodied-ai/pi-05-open-world.md)。

### π₀.₆：让策略从失败中变好

π₀.₆是面向 RECAP 的基础 VLA；π*₀.₆是经过 RECAP 经验学习后的结果。这里的星号区分“基础模型”和“RL 后训练策略”。RECAP并没有把每个低层控制步都改成 PPO，而是训练价值函数，给数据附优势条件，再用可扩展的监督目标提取策略。[RECAP概念文](../../00-concepts/01-embodied-ai/pi-06-recap.md)。

### π₀.₇：让多种行为可以被指定

π₀.₇将不同数据源的差异显式放进 prompt。它关注的是组合泛化和 steerability：任务相同但速度、质量、控制模式或空间终点不同，模型应能按条件选择行为。这是条件化的扩展，不是简单将 π*₀.₆ 的经验学习结果换名。[π₀.₇概念文](../../00-concepts/01-embodied-ai/pi-07-steerable.md)。

## 3. 方法支线：它们解决的是不同瓶颈

| 方法 | 作用位置 | 主要收益 | 代价或边界 |
|---|---|---|---|
| FAST | 动作表示与训练标签 | 压缩时间冗余，兼容 next-token 训练 | 自回归生成仍有串行成本；量化会损失细节 |
| Knowledge Insulation | 训练梯度 | 保护 VLM 表示，又让主干继续学习 | 需正确实现 stop-gradient 和双损失 |
| RTC | 推理时动作块切换 | 减少等待和跨块跳变 | 依赖扩散/流生成；不能修正错误目标 |
| RECAP | 经验学习与策略提取 | 使用坏轨迹、人工纠正和自主经验 | 依赖价值估计、奖励/阈值和真实采集 |
| 人类迁移 | 数据来源与共享表示 | 降低部分场景/物体/任务的数据成本 | 人手、夹爪、接触和相机仍有域差异 |
| MEM | 上下文记忆 | 用两种时间尺度支持长程任务 | 摘要会丢低层细节，视频窗口仍有限 |
| RLT | 局部在线 RL | 小网络在分钟级数据上适应精细阶段 | 仍需安全探索和任务奖励 |

这种表格不能产生“谁更强”的总排名：RTC 是执行算法，FAST 是表示，MEM 是记忆，RECAP/RLT 是学习机制，比较它们的单项成功率会把不同层级混在一起。它们可以组合，例如 π₀.₇ 使用训练时 RTC，MEM 使用知识绝缘式的连续专家，RLT则在 VLA 上方做局部策略编辑。

## 4. 发展脉络：四个研究问题逐步显形

**第一，动作如何表示。** π₀用流匹配保留连续动作分布，FAST则用频域压缩把动作带回 Transformer 的 token 训练。前者更自然地表达多模态连续动作，后者训练与数据规模更高效；π₀.₅及后续同时保留两者，分别承担训练表示和快速连续执行。

**第二，通用知识如何进入控制。** π₀从 VLM 初始化，π₀.₅把 Web、子任务、多环境和跨本体任务共训练，Knowledge Insulation处理“连续专家如何不污染主干”。人类视频迁移进一步问：当动作不属于同一机器人时，VLA是否能共享高层和相对运动表示。

**第三，闭环是否可靠。** RTC处理推理等待和块边界；RECAP处理策略犯错后的经验改进；RLT把同一目标局部化，让在线 RL 不必更新整个 VLA。这三者分别在时间连续性、跨轨迹信用分配和参数效率上工作。

**第四，模型是否知道上下文。** MEM把近期视觉与长期语义分开；π₀.₇把行为方式也放进上下文。前者回答“之前发生了什么”，后者回答“这次希望怎样做”，都不是只增加网络层数。

## 5. 如何选择阅读顺序

- 想理解 VLA 如何输出连续控制：先读[π₀](../../00-concepts/01-embodied-ai/pi-0-flow-vla.md)，再读[FAST](../../00-concepts/01-embodied-ai/pi-fast-action-tokenization.md)。
- 想理解开放环境泛化：读[π₀.₅](../../00-concepts/01-embodied-ai/pi-05-open-world.md)，然后读[人类迁移](../../00-concepts/01-embodied-ai/pi-human-to-robot.md)和[π₀.₇](../../00-concepts/01-embodied-ai/pi-07-steerable.md)。
- 想理解可靠执行：按[RTC](../../00-concepts/01-embodied-ai/pi-rtc-real-time-chunking.md) → [RECAP](../../00-concepts/01-embodied-ai/pi-06-recap.md) → [RLT](../../00-concepts/01-embodied-ai/pi-rlt-token.md)阅读。
- 想理解长程任务：先读[MEM](../../00-concepts/01-embodied-ai/pi-mem-memory.md)，再回到 π₀.₇ 的多模态 prompt。

## 6. 证据范围

本文使用 Physical Intelligence 官方研究页、官方文章、论文 HTML/PDF 和固定 commit 的 OpenPI 代码。性能数字只在对应概念文章和原始来源中保留，并说明任务与硬件条件；本次没有运行训练、机器人评测或端到端延迟复测。来源清单见[证据记录](../../../raw/entries/2026-11-06-pi-series.md)。
