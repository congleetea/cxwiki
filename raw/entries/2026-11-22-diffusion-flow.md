---
title: 扩散模型、流匹配与动作生成来源核验
id: source-diffusion-flow-2026-11-22
type: source
created: 2026-11-22
last_updated: 2026-11-22
---

# 扩散模型、流匹配与动作生成来源核验

获取与核验日期：2026-11-22。正文为教学综合与统一推导，未做机器人实验。PDF 从 arXiv 下载，使用 pdftotext 阅读相关章节；网页核验了论文标题、版本入口和官方项目页。

| 来源 | 原始入口与保存文件 | 核验位置 |
|---|---|---|
| Ho 等，DDPM | https://arxiv.org/abs/2006.11239 ，[PDF](../papers/diffusion-flow/ddpm.pdf) | §2–3，式 (2)、(4)、(12)，Algorithm 1–2；正向边缘与噪声预测 |
| Song 等，Score SDE | https://arxiv.org/abs/2011.13456 ，[PDF](../papers/diffusion-flow/score-sde.pdf) | §3.2 式 (6)，§4.3 式 (13)；反向时间符号、同边缘密度而非同轨迹 |
| Song、Meng、Ermon，DDIM | https://arxiv.org/abs/2010.02502 ，[PDF](../papers/diffusion-flow/ddim.pdf) | §3–4；非马尔可夫生成过程、确定性采样与子序列 |
| Lipman 等，Flow Matching | https://arxiv.org/abs/2210.02747 ，[PDF](../papers/diffusion-flow/flow-matching.pdf) | §3 Theorem 1–2；§4 Gaussian conditional paths；有限数据端噪声与教学零噪声极限区别 |
| Liu、Gong、Liu，Rectified Flow | https://arxiv.org/abs/2209.03003 ，[PDF](../papers/diffusion-flow/rectified-flow.pdf) | §2–3；线性参考、条件速度、reflow；不把随机配对称为已解全局最优传输 |
| Chi 等，Diffusion Policy | https://diffusion-policy.cs.columbia.edu/ ，https://arxiv.org/abs/2303.04137v4 ，[RSS PDF](../papers/diffusion-flow/diffusion-policy.pdf) | §III–IV；动作扩散、条件网络、预测与执行时域、DDIM 实验采样 |
| Physical Intelligence，π₀ | https://arxiv.org/html/2410.24164v4 ，[已有 PDF](../papers/pi-series/pi0.pdf) | §IV；视觉语言主干与动作专家 |
| OpenPI 固定代码 | https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/src/openpi/models/pi0.py ，[本地](../codes/openpi-215abfb/src/openpi/models/pi0.py) | compute_loss、sample_actions；噪声端为一、负步长、Beta 时间采样 |

## 原创推导与图示

- 统一高斯路径推导以数据和独立高斯噪声作线性组合；噪声预测、score 和速度互换只在相应非零系数及内部时间使用，不抹平时间权重差异。
- 绕行、单标量加噪和线性插值例子均为教学构造，不引用论文性能数字。
- 图稿脚本：`scripts/figures/draw_diffusion_flow.py`；七对 SVG 与 PNG 以 `df-` 为前缀。
- 双峰图：噪声为标准高斯，目标为等权混合的两个高斯，均值为 $-1$ 与 $+1$，标准差为 $0.14$。端点独立配对。
- 对分量均值 $m$，中间均值为 $\tau m$，方差为 $V=(1-\tau)^2+\tau^2\sigma^2$，条件平均速度为 $m+[\tau\sigma^2-(1-\tau)](x-\tau m)/V$。用后验分量概率混合，得到解析边缘速度场；欧拉法步长为 $0.001$。无需训练神经网络。
- 正文完整限定：图中的生成轨迹不是物理末端路线，直线标签不保证 ODE 一步生成；局部 Lipschitz 场的不交叉结论只讨论解唯一的内部时间。
