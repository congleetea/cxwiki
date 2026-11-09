---
title: FAST：频域动作序列标记化
id: fast-action-tokenization
type: concept
created: 2026-11-06
last_updated: 2026-11-06
stage: budding
verified_date: 2026-11-06
institution: Physical Intelligence × UC Berkeley × Stanford University
tags: [具身智能, VLA, 动作表示, Physical-Intelligence]
---

# FAST：为什么先压缩动作，再让模型预测 token

[打开本地论文 PDF](../../../raw/papers/pi-series/fast.pdf)


一只手臂以很高频率平滑移动，相邻两步的关节目标通常只差一点。如果把每个时刻、每个维度都分别量化成一个 token，大量训练目标只是“再次输出近似相同的数”。FAST利用整段动作的时间结构，让 token 代表压缩后的变化信息。[论文 §IV–V](../../../raw/papers/pi-series/fast.pdf)（[在线原文](https://arxiv.org/abs/2501.09747)）

FAST 的全名是 **Frequency-space Action Sequence Tokenization**。它是动作编码器，不是另一个机器人控制器，也不是旧文所写的 Fast Actor Skill Transformer。FAST+ 是作者训练并发布的通用标记器版本，不能与一个完整 VLA 策略等同。

## 1. 输入输出是什么

输入是一段连续动作 $A\in\mathbb R^{H\times d}$，$H$ 为时间步数，$d$ 为动作通道数。输出是变长离散序列 $z_{1:L}$。编码用于给自回归模型提供训练标签；解码则将模型预测的 token 转回近似动作 $\hat A$。

同一个通道必须保持同一种物理语义，例如某个关节角或某个坐标系下的位置增量。FAST处理数列的冗余，不会替你统一米和毫米、关节控制和末端控制，也不会自动进行人手到机器人运动学的映射。

![FAST的编码与解码](../../imgs/pi-fast.png)

*原创流程图：DCT和量化处理时间信号，BPE进一步压缩符号序列。[SVG](../../imgs/pi-fast.svg)。*

## 2. 第一步：按通道归一化

论文用训练数据的第 1 和第 99 百分位数将每个通道映射到约 $[-1,1]$。为便于理解，写作

$$
\tilde A_{h,j}=2\frac{A_{h,j}-q_{.01,j}}{q_{.99,j}-q_{.01,j}}-1.
$$

$q_{p,j}$ 是通道 $j$ 的训练集分位数。它们属于标记器和数据配方的一部分；推理时应复用，不能拿当前动作块重新计算。截断、零跨度与边界处理应按具体实现检查，上式只解释线性映射。[论文 §V](../../../raw/papers/pi-series/fast.pdf)（[在线原文](https://arxiv.org/abs/2501.09747)）

归一化使不同量纲的数值具有可比的量化精度。它不会消除通道意义的差别，反归一化仍要使用各自的统计量。

## 3. 第二步：沿时间轴做 DCT

对每个动作通道独立做离散余弦变换。用正交 DCT-II 的统一记号表示：

$$
C_{k,j}=\alpha_k\sum_{h=0}^{H-1}\tilde A_{h,j}
\cos\!\left[\frac\pi H\left(h+\frac12\right)k\right],
$$

其中 $k=0,\ldots,H-1$ 为频率索引，$\alpha_0=1/\sqrt H$，其余 $\alpha_k=\sqrt{2/H}$。$C\in\mathbb R^{H\times d}$ 与输入维度相同：**DCT本身不减少元素数**，而是让平滑轨迹的信息集中到较少的低频系数上。

例如归一化通道 $[0.5,0.5,0.5,0.5]$，正交 DCT 为 $[1,0,0,0]$。原来四个重复值，现在表现为一个直流系数和三个零；后续量化与符号编码更容易压缩。若动作包含冲击或快速变化，高频系数就不一定稀疏，不能沿用同样的压缩直觉。

## 4. 第三步：量化、展开、BPE

先把系数缩放并舍入：

$$
Q_{k,j}=\operatorname{round}(\gamma C_{k,j}),
$$

$\gamma>0$ 控制精度。若解码除以同一个 $\gamma$，单系数量化误差不超过 $1/(2\gamma)$；这是一条基于四舍五入的解释性误差界，不是闭环任务成功的保证。增大 $\gamma$ 通常保留更多细节，也使符号更难压缩。

随后按约定次序展开整数矩阵，再用字节对编码 BPE 合并常见符号组合。论文采用先遍历同一频率的各动作通道、再推进到下一频率的顺序，让低频信息优先出现。BPE词表要从动作数据学习，其编号并无“第几个关节”的固定语义。[论文 §V、Algorithm 1](../../../raw/papers/pi-series/fast.pdf)（[在线原文](https://arxiv.org/abs/2501.09747)）

解码依次执行 BPE 的逆变换、恢复矩阵、除以 $\gamma$、逆 DCT、反归一化。BPE在有效编码上可以逆转；主要的有损步骤是量化，以及实现中若采用的截断。模型生成了不合法或不完整序列时，还需要标记器自己的错误处理，不能假设任意 token 都能还原合法动作。

## 5. 它如何进入 VLA 训练

将动作块编码为 $z_{1:L}$ 后，VLA可用标准自回归目标训练：

$$
\mathcal L_{\rm AR}
=-\sum_{i=1}^L\log p_\theta(z_i\mid o,\ell,z_{<i}).
$$

训练使用真实前缀，可以并行计算多个位置的预测损失；推理一般要按顺序生成 token，所以**训练更快不等于部署推理同样提速**。FAST减少所需的动作 token 数，但仍有自回归依赖。[官方解释](https://www.pi.website/research/fast)

由此有两种用途：π₀-FAST直接生成 FAST token 再解码；π₀.₅的第一阶段用 FAST 学机器人表示，部署时改用连续流匹配动作专家。不能将两者写成“π₀.₅只用 FAST 输出动作”。

## 6. 怎样判断标记器适合自己的机器人

先看离线重建：平滑移动、开合夹爪、快速接触三个片段是否都保留关键时机；误差应在反归一化后的物理单位上检查。再看编码长度分布，而不只看平均压缩比。最后看模型训练后的闭环任务质量，编码误差小并不表示策略预测误差小。

论文报告相对于其流匹配基线，达到相近任务表现所需训练时间最多减少约五倍，条件是论文中的数据、架构与训练设置。这不是通用 GPU 基准，也不是任何控制频率上的五倍推理加速。[论文实验；官方说明](https://www.pi.website/research/fast)

FAST的优势是利用时间冗余、适配已有 token 训练管线；限制是量化取舍、动作语义需要事先规范，以及自回归推理成本。连续高精度控制与离散表示学习如何结合，见[π₀.₅](pi-05-open-world.md)和[知识绝缘](pi-knowledge-insulation.md)。系列关系见[综述](../../01-comprehensive/01-embodied-ai/pi-series-overview.md)。
