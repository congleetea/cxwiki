# 机器人价值与奖励模型：来源与核验

核验日期：2026-11-21。旧 cwiki 仅用于发现主题，事实回到原论文核验；未修改旧库。日期按 arXiv 首次提交记录，方法按下列版本阅读。

|方法|首次公开|核验版本|原始来源与本地副本|
|---|---|---|---|
|saycan|2022-04-04|v2，2022-08-16|[论文](https://arxiv.org/abs/2204.01691) · [PDF](../papers/robot-values/saycan.pdf)|
|gvl|2024-11-07|v1；本地 PDF 页眉另印 2024-11-08，不以排版日期替代 arXiv 首次公开日|[论文](https://arxiv.org/abs/2411.04549) · [PDF](../papers/robot-values/gvl.pdf)|
|sarm|2025-09-29|在线核验 v4，2026-04-27；本地副本 v3，2025-10-29|[论文](https://arxiv.org/abs/2509.25358) · [PDF](../papers/robot-values/sarm.pdf)|
|robo-dopamine|2025-12-29|v1|[论文](https://arxiv.org/abs/2512.23703) · [PDF](../papers/robot-values/robo-dopamine.pdf)|
|topreward|2026-02-22|v2，2026-07-22|[论文](https://arxiv.org/abs/2602.19313) · [PDF](../papers/robot-values/topreward.pdf)|
|robometer|2026-03-02|v2，2026-05-13|[论文](https://arxiv.org/abs/2603.02115) · [PDF](../papers/robot-values/robometer.pdf)|
|arm|2026-04-03|v2，2026-04-21|[论文](https://arxiv.org/abs/2604.03037) · [PDF](../papers/robot-values/arm.pdf)|
|sarm2|2026-06-09|v1|[论文](https://arxiv.org/abs/2606.10305) · [PDF](../papers/robot-values/sarm2.pdf)|

## 核对位置与重要修正

- SayCan §3、图 1、算法 1：有限技能选择、语言评分与可行性相乘；不是语言模型直接输出任意关节动作。
- GVL §3：首帧保留、其余帧打乱、逆置换；VOC 是顺序相关诊断，不能替代失败检测或真实机器人成功率。
- SARM §3：平均阶段占比、阶段内进度、示范筛选与 RA-BC；阶段和子任务估计器并非全部时序参数共享。
- Robo-Dopamine §3：分段相对 hop、三种估计视角、重构与奖励塑造；视角不是三台相机。
- TOPReward v2 §3：原始 log-probability 前缀分数因果；整段 min-max 进度用于可视化和 VOC，不能当作在线可用量。v2 行为克隆使用原始分数增量，区别于 v1 的归一化进度增量。
- Robometer v2 §3：progress、preference、success 三项损失，失败及倒放增强；固定取帧长度避免时长捷径。
- ARM v2 §3：进展／退步／停滞不是严格 RL 优势；完成锚点重建与局部因果预测分开；不保留旧文未经证实的会议标签、跨任务万能性能数字。
- SARM2 §3–4：负的归一化剩余步数、共享专家与动作基元；SPIRAL 是策略改进系统，不能与评分器本体混称。
- 奖励塑造边界：[Ng、Harada、Russell，1999](https://people.eecs.berkeley.edu/~russell/papers/icml99-shaping.pdf)。有限轨迹需要处理末端势函数，预测评分的阈值不自动保证真实任务成功。

## 存档与验证范围

GVL、SARM 的 PDF 从旧库来源目录读取后复制到新库，正文分别以原始在线版本复核；其余六篇从 arXiv 下载。副本不作为已复现实验的证明。所有二十张 SVG／PNG 为教学重绘，数值曲线为明确标注的示例；没有运行论文训练或真实机器人。

|副本|SHA-256|
|---|---|
|arm.pdf|`a80ed577ac490cd89b18bbfc1c700acabbedc7c35555ea5f37190758360198da`|
|gvl.pdf|`621819fea0df5069d035bacfb7b7cb717e40a3e1ea505c41a19ee7a3e8324704`|
|robo-dopamine.pdf|`e92751926cd437b725eea7a6b99577fd1e00c9f734b5bf22de9b3e58ba83e183`|
|robometer.pdf|`32d105fad4c505d68c0ca7c2d26417ba22024b1d78407d5368656ebb10814a8f`|
|sarm.pdf|`35a44bfa89919d589db846ffb062e45abbf4a4ebcdf5fbaeeb91bf61ce2a89fa`|
|sarm2.pdf|`5be9b078bb0604e56c348a38e1a74f9badb6cc3766eeca187b8fbb95d4ee4b8b`|
|saycan.pdf|`48c22d36a044bbbd34e640beb1db4fb4ba57e74d97fefa0fb121d55c31282312`|
|topreward.pdf|`464cac1b9fd014477fab3833ee626b448e98cb257b2941a8ccbf4c89bfa5f2e9`|
