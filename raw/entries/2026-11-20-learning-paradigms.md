# 在线／离线与 On-policy／Off-policy：迁移核验

核验日期：2026-11-20。旧库仅用于定位问题，未修改旧库。

## 旧文线索

- `/home/xuancong/gitlab/cwiki/wiki/01-comprehensive/03-ai-foundations/在线离线学习.md`
- `/home/xuancong/gitlab/cwiki/raw/articles/06-网页文章/online-learning, offline-learning, on-policy, off-policy概念.md`

## 原始来源与定位

- Shalev-Shwartz，[Online Learning and Online Convex Optimization](https://www.cs.huji.ac.il/~shais/papers/OLsurvey.pdf)，§1–2：顺序预测、反馈、遗憾与梯度更新。
- Levine 等，[Offline Reinforcement Learning，v3](https://arxiv.org/html/2005.01643v3)，§2：固定数据定义与分布偏移；§3：重要性采样；§4：动态规划式离线学习。
- Schulman 等，[PPO，arXiv:1707.06347](https://arxiv.org/abs/1707.06347)：摘要明确支持同批数据多轮小批量更新。
- OpenAI Spinning Up：[PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html)、[SAC](https://spinningup.openai.com/en/latest/algorithms/sac.html)、[算法分类](https://spinningup.openai.com/en/latest/user/algorithms.html)：策略目标、采集流程与回放使用。
- Stanford CS221，[MDP / RL 课程讲义](https://web.stanford.edu/class/archive/cs/cs221/cs221.1186/lectures/mdp2-6pp.pdf)：SARSA 与 Q-learning 更新目标。
- [π₀ 原论文页面](https://arxiv.org/abs/2410.24164)：模型与动作流建模背景；细节链接本库已有概念文章。
- Sutton–Barto 教材作者 PDF 地址本次网页读取返回 502，未将本次访问描述为已成功读取；Stanford 讲义全文抓取也失败，搜索索引可见 SARSA 定义；TD 更新另以本库已有综述逐式比对，并核验官方 Q-learning 说明。正文保留教材参考链接。

## 重要修正

1. 区分一般在线优化与在线强化学习，删除“在线必然样本低效”。
2. 删除“VLA 本质是离线 off-policy RL”，区分 BC、动作建模与奖励优化。
3. 将“off-policy 数据必须不是当前策略产生”改成允许行为策略与目标策略不同。
4. 删除“on-policy 每条样本只能用一次”，解释 PPO 有限多轮更新。
5. 删除“offline + on-policy 不可能”，区分固定策略评估与持续策略优化。
6. 删除“其他机器人数据都可以直接用”，补充动作、观测和动力学兼容条件。
7. 重要性采样例子、TD 目标数值、流程图为本文原创教学推导，不是实验结果。

补充核验：[Spinning Up DDPG：The Q-Learning Side](https://spinningup.openai.com/en/latest/algorithms/ddpg.html)，已读取 Bellman 最优目标、终止 mask、回放和目标网络的公式及说明。
