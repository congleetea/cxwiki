# 刚体运动、动力学与柔顺控制：来源和整理记录

核验日期：2026-11-20。未运行真实机械臂，未把理想控制方程当作整机稳定保证。

## 内容拆分

- 原刚体运动学文章的 ID 保留在综述目录；几何和朝向表示细节移到独立位姿概念文。
- 速度和加速度独立解释；力、力矩、惯量与多连杆动力学独立解释。
- 阻抗与导纳合写，便于在同一符号、同一接触任务下对比。
- 旧库未改；不是批量迁移旧内容。

## 原始来源

- Modern Robotics 作者视频教材：[§3.2.2 Angular Velocities](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-2-angular-velocities/)，旋转矩阵导数、角速度坐标表达。
- [§3.4 Wrenches](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/)，力矩参考点、力系、功率对偶与变换。
- [§5.1.1 Space Jacobian](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-1-1-space-jacobian/)，关节速度与空间 twist；正文单独区分点速度雅可比。
- [§8.2 Dynamics of a Single Rigid Body](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-2-dynamics-of-a-single-rigid-body-part-1-of-2/)，质心、惯量、刚体系欧拉方程。
- [§8.3 Newton–Euler Inverse Dynamics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-3-newton-euler-inverse-dynamics/)，前向运动递推与反向力系递推。教材外载符号可能采用机器人对外作用力，正文明确用环境对机器人力，不混用两者符号。
- Ott、Mukherjee、Nakamura，Unified Impedance and Admittance Control，ICRA 2010，[来源 PDF](https://fileadmin.cs.lth.se/ai/Proceedings/ICRA2010/MainConference/data/papers/1462.pdf)，[本地文件](../papers/ott-unified-impedance-admittance-2010.pdf)。已下载并读 §I–II，单轴模型、两种因果实现和非理想交互；后续混合控制仅作可能方向，不声称实现。
- Hogan，Impedance Control: An Approach to Manipulation，Part I—Theory，1985，[原始工作 PDF 检索入口](https://summerschool.stiff-project.org/fileadmin/pdf/Hog1985.pdf)。检索可见标题、摘要与引言，全文网页打开超时；正文历史来源注明它，实际实现说明以已读 Ott 论文核验。不声称本次已下载或逐页阅读 Hogan 全文。

## 原创推导与符号

- 加速度两次求导、单杆雅可比、力臂和惯量数值例子为原创教学推导。
- wrench 采用力在前、力矩在后；速度采用同点线速度在前、角速度在后。和 Modern Robotics 的排列不同，已在正文注明。
- 阻抗单轴 PD 例子的惯量为真实质量，不冒充任意惯量整形；导纳虚拟状态与实际末端状态分开。
- 导纳积分是半隐式离散示意，不带任意采样／参数稳定保证。
- 步响应为临界阻尼解析曲线，非实验；两条曲线同时改变刚度与对应阻尼，已写明。
- 新图七组 SVG / PNG，数学由 LaTeX 渲染；既有三组刚体示意标签也改成 LaTeX。没有以生成式图片绘制公式。
