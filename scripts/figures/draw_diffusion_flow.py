"""Original didactic diagrams; analytic toy distributions, not robot experiments."""
from draw_foundations import Fig, OUT, BLUE, GREEN, PURPLE, ORANGE, MUTED
from playwright.sync_api import sync_playwright
import math
import random

SPECS=[]
def finish(f):
 f.save(); SPECS.append((f.name,f.h))
def circle(f,x,y,r,color):
 f.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')

f=Fig('df-two-routes','① 为什么“平均动作”可能是坏动作','同一个场景允许两种绕行策略；训练目标需要描述分布。',570)
f.rect(60,135,590,350)
f.rect(303,245,105,110,'#dce5eb',r=8);f.text(355,280,'障碍物',21,anchor='middle')
for x,t in [(110,'起点'),(595,'终点')]:circle(f,x,300,7,BLUE);f.text(x,335,t,21,anchor='middle')
f.path('M110 300 C200 130 480 130 595 300',BLUE,5)
f.path('M110 300 C200 470 480 470 595 300',GREEN,5)
f.line(110,300,595,300,ORANGE,dash=True,width=4)
f.text(350,155,'左侧绕行',22,BLUE,anchor='middle');f.text(350,470,'右侧绕行',22,GREEN,anchor='middle')
f.box(700,150,450,135,'直接回归',['两条演示取平均','可能穿过中间的障碍物'],ORANGE)
f.box(700,320,450,135,'条件生成',['在两种合理动作中采样一种','整段动作共同决定绕行方式'],PURPLE)
f.footer('原创几何例子；曲线为末端在桌面的物理路径，不是噪声到动作的生成路径。');finish(f)

f=Fig('df-noising','② 扩散的训练样本怎样构造','先拿到真实动作，再按指定噪声强度混入随机数。',540)
rng=random.Random(7)
for j,(a,b,label) in enumerate([(1,0,'干净动作'),(.8,.6,'部分被噪声淹没'),(0,1,'近似纯噪声')]):
 x=40+j*390;f.rect(x,140,350,245);f.text(x+175,178,label,23,BLUE,anchor='middle')
 pts=[]
 for i in range(25):
  y=a*.65*math.sin(i/24*math.pi*1.7)+b*rng.gauss(0,.55)
  pts.append((x+25+i*12.4,282-y*65))
 f.path('M'+' L'.join(f'{px:.1f} {py:.1f}' for px,py in pts),[BLUE,PURPLE,ORANGE][j],3)
 f.text(x+175,365,['$k=0$','$0<k<K$','$k=K$'][j],23,anchor='middle')
 if j<2:f.line(x+354,265,x+384,265,arrow=True)
f.text(600,435,r'$x_k=\sqrt{\bar\alpha_k}\,x_0+\sqrt{1-\bar\alpha_k}\,\epsilon$',30,anchor='middle')
f.footer('曲线只展示归一化动作向量的一维切片；训练无需逐步模拟整条加噪链。');finish(f)

f=Fig('df-training','③ 两种训练：已知答案，随机出一道中间题','每次选一个噪声等级或生成时刻；推理才需要反复调用网络。',690)
f.box(35,135,1130,95,'共同起点',['真实动作块、当前观测、随机噪声；真实动作只在训练时可见'],BLUE)
f.box(35,280,540,155,'DDPM：预测噪声',[r'$x_k=\sqrt{\bar\alpha_k}x_0+\sqrt{1-\bar\alpha_k}\epsilon$',r'监督：$\epsilon$；输入：$x_k,k,c$'],PURPLE)
f.box(625,280,540,155,'线性流匹配：预测速度',[r'$x_\tau=(1-\tau)\epsilon+\tau x_1$',r'监督：$x_1-\epsilon$；输入：$x_\tau,\tau,c$'],GREEN)
f.line(300,233,300,276,arrow=True);f.line(890,233,890,276,arrow=True)
f.box(35,490,540,100,'部署：从噪声开始',['用去噪更新公式或其他采样器多次更新'],PURPLE)
f.box(625,490,540,100,'部署：从噪声开始',['按预测速度积分，多次更新动作候选'],GREEN)
f.line(300,440,300,485,arrow=True);f.line(890,440,890,485,arrow=True)
f.footer('DDPM 只是扩散模型的一种参数化；流匹配也不限于线性插值。');finish(f)

f=Fig('df-flow-field','④ 直线监督，不等于生成轨迹一定是直线','解析双峰玩具分布：目标集中在两个动作附近，网络最优解是条件平均速度。',640)
# x horizontal = generation time; y vertical = action value
left,top,w,h=90,145,690,350
f.line(left,top+h,left+w+20,top+h,arrow=True);f.line(left,top+h,left,top-12,arrow=True)
def xy(t,x):return left+t*w,top+h/2-x*85
def vel(t,x):
 var=(1-t)**2+(t*.14)**2
 logs=[-(x-t*m)**2/(2*var) for m in [-1.,1.]]
 mmax=max(logs);p=[math.exp(z-mmax) for z in logs];tot=sum(p)
 return sum(q*(m+(t*.14**2-(1-t))/var*(x-t*m)) for q,m in zip(p,[-1.,1.]))/tot
for val in [-1.6,-1.05,-.65,-.25,.25,.65,1.05,1.6]:
 pts=[];x=val
 for n in range(1001):
  t=n/1000;pts.append(xy(t,x))
  if n<1000:x+=.001*vel(t,x)
 f.path('M'+' L'.join(f'{px:.2f} {py:.2f}' for px,py in pts),BLUE if val<0 else GREEN,2.5)
for j,(a,b) in enumerate([(-1.5,1),(.9,-1)]):
 x1,y1=xy(0,a);x2,y2=xy(1,b);f.line(x1,y1,x2,y2,ORANGE,dash=True,width=2)
f.text(90,535,r'$\tau=0$：噪声',22);f.text(640,535,r'$\tau=1$：动作',22)
f.text(37,145,r'$x$',24);f.box(825,150,335,180,'橙色虚线',['随机配对的直线标签','不同配对可以交叉','只用于构造训练题'],ORANGE)
f.box(825,360,335,180,'蓝绿实线',['解析平均速度场的积分','逐步分成两个动作簇','并非逐条复原标签直线'],GREEN)
f.footer('原创可复算图：等权高斯双峰目标，标准差为 0.14；欧拉步长为 0.001。');finish(f)

f=Fig('df-relations','⑤ 先分清：路径、预测量、求解器','看见相同的迭代外观，不代表训练目标相同；换采样器也不必重训。',620)
f.box(40,145,350,310,'一：概率路径',['中间分布如何变化？','扩散加噪日程','线性插值路径','其他高斯条件路径'],BLUE)
f.box(425,145,350,310,'二：网络预测量',['每一步网络输出什么？','噪声 / 干净样本 / score','流匹配速度','转换依赖路径与缩放'],PURPLE)
f.box(810,145,350,310,'三：生成求解器',['怎样走到最终样本？','随机反向扩散','确定性 ODE / DDIM','步长、阶数、调用次数'],GREEN)
f.text(600,520,'扩散可以有确定性采样；流匹配可以使用扩散式概率路径。',25,anchor='middle')
f.footer('原创分类图；这三个维度应分开比较，不能用“随机 / 确定”直接区分两个训练家族。');finish(f)

f=Fig('df-two-clocks','⑥ 两个时间轴：先生成整段，再执行其中一段','生成步骤改的是整张动作表；控制步骤才让机器人实际运动。',690)
f.box(40,135,1120,135,'生成时间：一次控制决策内部的数值计算',[r'$X_0\ \longrightarrow\ X_{1/4}\ \longrightarrow\ X_{1/2}\ \longrightarrow\ X_1$','每个候选都是一整段动作；生成中的中间候选不直接下发'],PURPLE)
f.box(40,310,1120,135,'物理时间：动作块里的先后次序',[r'$A_n=[a_n,a_{n+1},\ldots,a_{n+H-1}]$','执行前面几步 → 获取新观测 → 再生成下一块'],GREEN)
f.line(600,274,600,305,arrow=True)
f.box(40,490,1120,100,'改变积分步数，改变的是生成计算量',['动作块长度、执行频率、执行前缀长度是另外几个参数'],BLUE)
f.footer('原创时序图；噪声中间态无需满足机器人轨迹约束，最终命令仍需经过接口与安全检查。');finish(f)

f=Fig('df-action-pipeline','⑦ 从生成向量到机器人动作','以基座坐标系下的末端位置增量和夹爪命令为教学接口。',650)
f.box(35,140,340,160,'当前条件',['相机图像、机器人状态','任务指令（若使用语言）','编码后作为每步生成的条件'],BLUE)
f.box(430,140,340,160,'条件生成器',['随机动作表作为起点','去噪 / 速度积分','输出归一化动作块'],PURPLE)
f.box(825,140,340,160,'接口转换',['反归一化与单位恢复','坐标系与旋转表示转换','约束检查、控制器跟踪'],GREEN)
f.line(380,220,425,220,arrow=True);f.line(775,220,820,220,arrow=True)
f.box(430,385,735,135,'只执行动作块的前缀',['机器人运动 → 相机与状态更新 → 下一次生成','分布上合理，不等于必然可达、无碰撞或满足力矩限制'],ORANGE)
f.path('M430 450L200 450L200 305',BLUE,3);f.line(200,330,200,305,BLUE,arrow=True)
f.footer('原创接口示意；Diffusion Policy 与 π₀ 的输入、骨干及动作表示以各自论文和代码为准。');finish(f)

if __name__=='__main__':
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  for name,height in SPECS:
   page=browser.new_page(viewport={'width':1200,'height':height},device_scale_factor=1.5)
   page.goto((OUT/(name+'.svg')).resolve().as_uri());page.screenshot(path=str(OUT/(name+'.png')));page.close()
  browser.close()
