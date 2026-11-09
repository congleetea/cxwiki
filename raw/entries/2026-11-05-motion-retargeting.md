---
id: sources-motion-retargeting-20261105
title: 动作重定向综述来源与证据
date: 2026-11-05
source_type: mixed
status: absorbed
tags: [retargeting, FRAX, GMR, PyRoki]
---

# 来源与证据记录

用于[动作重定向综述](../../wiki/01-comprehensive/02-classical-robotics/motion-retargeting-overview.md)。核验日期为 2026-11-05（Asia/Shanghai）。正文为综合解释和独立推导，不是任一原文的译文。

## 一手来源与关键定位

| 来源 | 版本或定位 | 核验用途 |
|---|---|---|
| [FRAX 首页](https://stanfordasl.github.io/frax/) | Usage tips、Performance tips；页面介绍 0.2.0 IK | 状态顺序、浮动基座速度约定、积分、JIT 与性能口径 |
| [FRAX IK 指南](https://stanfordasl.github.io/frax/ik/) | Humanoid Retargeting、LAFAN1 | ElastiQP、作者 CPU 吞吐报告、可选自碰撞、当前示例机器人 |
| [FRAX 源码](https://github.com/StanfordASL/frax/tree/f5e87ab59a0b82ba43095e882c1b88c9b0dacf07) | commit `f5e87ab59a0b82ba43095e882c1b88c9b0dacf07` | 逐文件阅读，见下一节 |
| [ElastiQP 论文](https://arxiv.org/html/2609.19080v1) | §II 弹性 QP、精确罚条件；§III 松弛消元 | 不等式允许松弛，硬等式需相容；始终可行不等于全部约束满足 |
| [GMR 论文](https://arxiv.org/html/2510.02252v1) | §III 评估设置；§IV 方法；§V 结果 | 局部缩放、两阶段 IK、下游追踪与实验边界 |
| [GMR 源码](https://github.com/YanjieZe/GMR/tree/25f56db79ac411258b377b6d4ccba0c8ff3372ac) | `general_motion_retargeting/motion_retarget.py`，commit `25f56db79ac411258b377b6d4ccba0c8ff3372ac` | 根相对位置缩放、局部偏置、两个任务集合与迭代 |
| [Mink 文档](https://kevinzakka.github.io/mink/) | 首页与基本问题定义 | 微分 IK / QP 的工具定位 |
| [PyRoki 论文](https://arxiv.org/html/2505.03728v1) | §III 建模；§IV-B 重定向 | 可组合变量、残差、非线性最小二乘与应用 |
| [PyRoki 项目](https://pyroki-toolkit.github.io/) | 官方项目页；[代码](https://github.com/chungmin99/pyroki/tree/388e43e1fc0d0ee382968d3dd72970fd62a0450c) | 项目定位；代码取到本地，综述的求解范式论述主要依据论文 |
| [SONIC](https://nvlabs.github.io/GEAR-SONIC/) | Method、Abstract、Teleoperation | 统一潜在控制接口与物理追踪定位 |
| [ExtremControl](https://arxiv.org/html/2602.11321v1) | §II–IV 与附录 A | 笛卡尔空间映射、控制与显式关节重定向差异 |
| [HuRo](https://arxiv.org/html/2609.10706v1) | §3.1.2、附录 G.2；[项目页](https://3587jjh.github.io/HuRo/) | 动作转换、工作空间对齐、观测与动作共同机器人化 |
| [EgoScale](https://research.nvidia.com/labs/gear/egoscale/) | Human-to-Robot Learning Framework、Model Architecture | 人体动作监督与少量对齐数据的迁移路线 |

## 保存的关键实现快照

只保存 FRAX 与关键判断有关的原始文件，未修改内容；**不是完整可运行仓库**。代码采用其 MIT LICENSE，许可证随快照保存。逐文件 SHA-256 见 [snapshot.json](../codes/frax-f5e87ab/snapshot.json)。

- [LAFAN1 配置](../codes/frax-f5e87ab/examples/ik/lafan1/lafan1_g1.py)：14 个框架映射、脚框架、分区缩放、骨盆和地板偏置、肩腕正则、默认地板/可选自碰撞。
- [计时入口](../codes/frax-f5e87ab/examples/ik/lafan1/retarget.py)：读取和平滑、离线重定向、编译统计、结果保存分别处理。
- [任务](../codes/frax-f5e87ab/frax/ik/tasks.py)：几何雅可比、朝向反馈、残差行权重。
- [求解器](../codes/frax-f5e87ab/frax/ik/solver.py)：QP 二次项、热启动、流形积分。
- [约束](../codes/frax-f5e87ab/frax/ik/constraints.py)：CBF 形式、有限罚系数、球形几何与最近约束筛选。
- [重定向包装](../codes/frax-f5e87ab/frax/ik/retargeter.py)：首帧收敛，片段内 `scan`，跨片段并行，长度桶与编译缓存。
- [旋转工具](../codes/frax-f5e87ab/frax/utils/rotation_utils.py)：`orientation_error_quat` 使用相对四元数向量部分，区别于通用旋转对数残差。

## 旧库阅读线索

以下文件从 `/home/xuancong/gitlab/cwiki/wiki/` 阅读，未修改、未整篇迁移。它们用于发现主题关系；正文技术主张回到上表一手来源核验。

- `01-comprehensive/02-classical-robotics/逆运动学求解方法与开源库.md`
- `00-concepts/02-classical-robotics/PyRoki运动学优化工具包.md`
- `01-comprehensive/01-embodied-ai/全身遥操作与数据采集系统.md`，尤其 GMR / TWIST2 章节。
- `00-concepts/01-embodied-ai/SONIC规模化运动追踪人形全身控制.md`
- `00-concepts/01-embodied-ai/ExtremControl低延迟人形遥操作.md`
- `00-concepts/01-embodied-ai/HuRo机器人化人类视频VLA预训练.md`
- `00-concepts/01-embodied-ai/EgoScale自中心视角人类数据缩放灵巧操控.md`

参考了 `/home/xuancong/.claude/skills/wiki/SKILL.md` 的 raw/wiki 分层、主题组织、主张证据区分和索引维护。Codex 版本按用户偏好重新编写，不继承 Excalidraw 工作流或依赖缺失的 Claude 专用命令。

## 核验边界

已做：官方网页与相关论文段落阅读、FRAX 关键代码逐文件检查、GMR 缩放与阶段实现交叉检查、原创公式和技术图审阅。

概念页扩写时补充核对：`JointLimits` 不限制浮动基座；`EETask` / `JointTask` 与官方 `examples/ik/panda_interactive.py` 的调用约定；`SolverInfo.cost` 对应积分前状态；QP 矩阵与 `regularization` / `damping` 的具体公式。教程中的两连杆与一维数值例子为本文独立计算，Panda 代码仅做语法与接口静态检查，未执行 FRAX 求解。

未做：LAFAN1 数据集下载与性能复测、FRAX/GMR/PyRoki 同条件 benchmark、RL 训练、真机实验。作者数据只按报告引用；不把演示、可计算动力学或求解成功解释成真实执行保证。
