"""Redraw RL overview figures; mathematical labels are typeset from LaTeX."""
from draw_foundations import Fig, BLUE, PURPLE, GREEN, ORANGE, OUT
NAMES=[]
def fig(name,title,sub='',height=520):
 NAMES.append(name);return Fig(name,title,sub,height)
def finish(f,foot='原创教学示意；符号与正文对应。'):
 f.footer(foot);f.save()

f=fig('ml-three-paradigms','机器学习：三种不同的反馈方式','比较的是训练信号；真实系统也可以结合多种学习方式。')
for x,title,lines,c in [(30,'监督学习',['输入与标签成对出现','$\\{(x_i,y_i)\\}_{i=1}^{N}$','预测与答案比较','例：图像分类'],BLUE),(420,'非监督学习',['从未标注数据发现结构','$\\{x_i\\}_{i=1}^{N}$','用聚类或重构等目标学习','例：聚类与降维'],PURPLE),(810,'强化学习',['动作影响后续数据','$s_t \\to a_t \\to (r_{t+1},s_{t+1})$','优化长期累积回报','例：机器人序列控制'],GREEN)]:
 f.box(x,140,360,280,title,lines,c)
finish(f)

f=fig('rl-agent-env-loop','智能体与环境：一步交互如何闭环','以完全可观测 MDP 为例；策略根据当前状态选择动作。',520)
f.box(60,180,370,200,'智能体',['策略','$a_t \\sim \\pi(\\cdot\\mid s_t)$'],BLUE)
f.box(770,180,370,200,'环境',['执行动作、产生反馈','状态转移与奖励'],GREEN)
f.line(435,220,760,220,BLUE,True,width=3);f.text(590,193,'动作 $a_t$',24,BLUE,'middle')
f.line(770,325,440,325,GREEN,True,width=3);f.text(600,363,'$s_{t+1},\\ r_{t+1}$',25,GREEN,'middle')
f.text(600,445,'经验用于评估价值或更新策略；下一时间步再次选择动作',23,anchor='middle');finish(f)

f=fig('rl-elements-classification','强化学习要素：问题定义与求解对象','环境定义决策问题；智能体需要学习或使用其中一部分对象。',560)
f.box(35,135,545,330,'01  问题：MDP',[
 '状态与动作：$\\mathcal{S},\\ \\mathcal{A}$',
 '转移：$P(s^{\\prime}\\mid s,a)$',
 '期望奖励：$r(s,a)$',
 '折扣：$\\gamma \\in [0,1)$',
 '奖励可更一般地写成联合转移分布'],BLUE)
f.box(620,135,545,330,'02  求解：学什么、用什么',[
 '策略：$\\pi(a\\mid s)$',
 '状态价值：$V^\\pi(s)$',
 '动作价值：$Q^\\pi(s,a)$',
 '可选：学习转移与奖励模型',
 '模型用于预测、规划或生成经验'],PURPLE);finish(f)

f=fig('rl-algorithm-taxonomy','强化学习算法：按模型使用与更新对象理解','这是一种常见组织方式；Actor–Critic 同时使用策略和价值。',600)
f.box(30,135,340,345,'使用环境模型',['已知或学习模型','用预测进行规划','动态规划 / 模型预测控制'],BLUE)
f.box(410,135,760,110,'不显式用模型规划',['直接由经验更新价值或策略'],PURPLE)
for x,t,ls,c in [(410,'价值方法',['学习 $Q(s,a)$','Q-learning / DQN'],BLUE),(670,'策略方法',['直接优化 $\\pi_\\theta$','REINFORCE'],GREEN),(930,'Actor–Critic',['策略 + 价值','如 A2C / SAC'],ORANGE)]:
 f.box(x,285,240,195,t,ls,c)
finish(f,'原创分类示意；分类轴可交叉：基于模型的系统也可以包含 Actor–Critic。')

f=fig('rl-overview','强化学习学习路线：从问题到可训练算法','先理解价值递推，再区分已知模型与采样学习。',570)
for x,y,t,ls,c in [(30,135,'01  定义问题',['MDP、状态与动作','奖励、回报与策略'],BLUE),(420,135,'02  建立递推',['贝尔曼期望方程','贝尔曼最优方程'],PURPLE),(810,135,'03  已知模型',['策略评估与改进','值迭代、策略迭代'],GREEN),(30,340,'04  用采样替代期望',['Monte Carlo','Temporal Difference'],GREEN),(420,340,'05  函数逼近',['价值网络、策略网络','泛化与训练稳定性'],BLUE),(810,340,'06  优化决策',['策略梯度','Actor–Critic'],PURPLE)]:
 f.box(x,y,360,155,t,ls,c)
for x in (395,785):f.line(x,210,x+20,210,arrow=True)
for x in (395,785):f.line(x,410,x+20,410,arrow=True)
finish(f,'原创阅读路线；下排继续展开采样学习，不表示所有方法必须依次执行。')

f=fig('rl-bellman-equation-four-grid-example','贝尔曼方程：沿固定策略递推价值','持续任务；目标状态仍可获得奖励，并非到达即终止。',570)
for x,y,t,c in [(70,150,'$s_1$',BLUE),(260,150,'$s_2$',ORANGE),(70,320,'$s_3$',BLUE),(260,320,'$s_4$',GREEN)]:
 f.rect(x,y,150,120,stroke=c);f.text(x+75,y+65,t,30,c,'middle')
f.line(145,275,145,315,BLUE,True,width=3);f.text(60,302,'$r=0$',19)
f.line(335,275,335,315,GREEN,True,width=3);f.text(350,302,'$r=1$',19)
f.line(225,380,255,380,GREEN,True,width=3)
f.text(230,465,'$s_4 \\to s_4,\\ r=1$',22,GREEN,'middle')
f.box(510,140,650,330,'固定策略：下、下、右、停留',[
 '$V(s_4)=1+\\gamma V(s_4)$',
 '$V(s_2)=V(s_3)=1+\\gamma V(s_4)$',
 '$V(s_1)=\\gamma V(s_3)$',
 '$\\gamma=0.9:\\quad V=(9,10,10,10)^T$',
 '价值由当前奖励与后续价值共同决定'],PURPLE)
finish(f,'原创数值示意；只绘出当前策略选中的转移，未绘制其余动作。')

f=fig('rl-value-iteration-example','值迭代：每轮只做一次最优性备份','正文 2×2 网格；同步更新，初值为零，折扣系数为 0.9。',590)
values=[('初值',('0','0','0','0')),('第 1 轮',('0','1','1','1')),('第 2 轮',('0.9','1.9','1.9','1.9'))]
for x,(title,vs) in zip((45,435,825),values):
 f.text(x,150,title,25,BLUE)
 for i,v in enumerate(vs):
  xx=x+(i%2)*150;yy=180+(i//2)*110
  f.rect(xx,yy,145,105,fill='#edf6f1' if i==3 else 'white')
  f.text(xx+15,yy+30,f'$s_{i+1}$',20)
  f.text(xx+75,yy+78,f'${v}$',30,PURPLE,'middle')
f.text(600,470,'$V_{k+1}(s)=\\max_a\\,[r(s,a)+\\gamma V_k(s^{\\prime})]$',29,BLUE,'middle')
f.text(600,520,'确定性转移示例：奖励先传播到邻近状态，再向更远处传播。',23,anchor='middle');finish(f)

f=fig('rl-policy-iteration-example','策略迭代：完整评估，再贪心改进','正文两状态例子；撞边界奖励 −1，进入或停留目标奖励 +1。',600)
f.box(35,140,350,310,'01  初始策略：都停留',[
 '$\\pi_0=(a_0,a_0)$',
 '$V^{\\pi_0}(s_1)=0$',
 '$V^{\\pi_0}(s_2)=1+0.9V^{\\pi_0}(s_2)$',
 '$V^{\\pi_0}=(0,10)^T$'],BLUE)
f.box(425,140,350,310,'02  对已评估价值改进',[
 '$Q^{\\pi_0}(s_1,a_r)=1+0.9(10)$',
 '$Q^{\\pi_0}(s_1,a_r)=10$',
 '第一状态改为向右',
 '第二状态继续停留'],PURPLE)
f.box(815,140,350,310,'03  重新评估',[
 '$\\pi_1=(a_r,a_0)$',
 '$V^{\\pi_1}=(10,10)^T$',
 '再次贪心改进，策略不变',
 '停止：已经达到最优策略'],GREEN)
f.text(600,520,'$\\pi_k \\longrightarrow V^{\\pi_k} \\longrightarrow \\pi_{k+1}$',30,PURPLE,'middle');finish(f)

if __name__=='__main__':
 from playwright.sync_api import sync_playwright
 import re
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  for name in NAMES:
   path=OUT/(name+'.svg');height=int(re.search(r'height="(\d+)"',path.read_text())[1])
   page=browser.new_page(viewport={'width':1200,'height':height},device_scale_factor=2)
   page.goto(path.resolve().as_uri());page.screenshot(path=str(path.with_suffix('.png')));page.close()
  browser.close()
