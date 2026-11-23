"""Geometric mechanics and compliant-control figures with LaTeX labels."""
from draw_foundations import Fig, BLUE, PURPLE, GREEN, ORANGE, OUT
import math
NAMES=[]
def fig(n,t,s,h=560):NAMES.append(n);return Fig(n,t,s,h)
def arr(f,x,y,xx,yy,c=BLUE):f.line(x,y,xx,yy,c,True,width=3)
def spring(f,x,y,length=180):
 pts=[(x,y),(x+15,y)]+[(x+15+i*(length-30)/12,y+(15 if i%2 else -15)) for i in range(1,12)]+[(x+length-15,y),(x+length,y)]
 f.path('M'+' L'.join(f'{a} {b}' for a,b in pts),PURPLE,3)
f=fig('robot-mechanics-map','从位姿到接触控制：各层回答不同问题','几何描述 → 运动变化 → 力与运动的关系 → 主动设计接触响应。')
for x,t,ls,c in [(30,'位姿',['$R,\\ p,\\ T$','在哪里，朝向哪里'],BLUE),(330,'速度与加速度',['$v,\\omega,a,\\alpha$','怎样运动与变化'],GREEN),(630,'动力学',['$f,\\tau,m,I$','什么力引起这些变化'],PURPLE),(930,'接触控制',['$M_d,D_d,K_d$','受力时希望怎样运动'],ORANGE)]:f.box(x,155,240,235,t,ls,c)
for x in (275,575,875):arr(f,x,270,x+45,270)
f.footer('原创阅读路线；运动学不需要质量和力，动力学与接触控制在其上引入物理参数及目标行为。');f.save()

f=fig('rigid-acceleration','加速度并不总沿速度方向：切向与向心两部分','平面转动的瞬间：点在圆的最右侧，角速度和角加速度沿正 z 方向。')
f.parts.append('<circle cx="245" cy="300" r="120" fill="none" stroke="#b3c9d6" stroke-width="2" stroke-dasharray="6 5"/>')
f.text(220,330,'$O$',26);f.text(375,325,'$P$',26)
arr(f,245,300,365,300,PURPLE);f.text(290,335,'$r$',25,PURPLE)
arr(f,365,300,365,145,GREEN);f.text(380,185,'$a_{\\mathrm{tan}}$',24,GREEN)
arr(f,365,300,255,300,ORANGE);f.text(260,275,'$a_{\\mathrm{cen}}$',24,ORANGE)
f.box(570,140,590,290,'不同的运动变化，来自不同的项',[
 '$v=\\omega\\times r$',
 '$a_{\\mathrm{tan}}=\\alpha\\times r$',
 '$a_{\\mathrm{cen}}=\\omega\\times(\\omega\\times r)$',
 '恒定转速也有向心加速度',
 '原点平移时，再加上原点加速度'],BLUE)
f.footer('原创示意；位置与加速度箭头的比例尺独立。向心加速度来自运动学，不是额外的离心外力。');f.save()

f=fig('rigid-force-moment','同样的力，作用线不同，转动效果就不同','俯视转轴；力矩关于原点计算，正方向按右手定则。')
for x,vertical in [(170,True),(690,False)]:
 f.text(x-20,345,'$O$',25);f.line(x,320,x+230,320,PURPLE,width=7);f.text(x+110,355,'$r$',25,PURPLE)
 arr(f,x+230,320,x+230+(0 if vertical else 140),320-(150 if vertical else 0),GREEN)
 f.text(x+245,240 if vertical else 300,'$f$',27,GREEN)
f.text(310,420,'$\\tau_z=rf$',30,BLUE,'middle');f.text(850,420,'$\\tau_z=0$',30,ORANGE,'middle')
f.text(600,140,'$\\tau_O=r_{OP}\\times f$',29,PURPLE,'middle')
f.footer('原创力臂图；左侧力与杆垂直，右侧力的作用线通过转轴。合力相同，不代表关于某点的合力矩相同。');f.save()

f=fig('rigid-inertia','质量相同，离转轴越远，越难改变转速','两个理想点质量固连在无质量杆两端；只比较绕中心垂直图面的固定轴转动。')
for cx,r in [(290,65),(880,180)]:
 f.line(cx-r,280,cx+r,280,BLUE,width=7)
 for dx in [-r,r]:f.parts.append(f'<circle cx="{cx+dx}" cy="280" r="24" fill="{GREEN}"/>')
 f.text(cx-9,328,'$O$',24)
 for dx in [-r,r]:f.text(cx+dx,235,'$m$',24,GREEN,'middle')
 f.text(cx,400,'$I_z=2mr^2$' if r==65 else '$I_z^{\\prime}=2m(2r)^2=4I_z$',28,PURPLE,'middle')
f.footer('原创理想化比较；两图位置示意不按严格倍数绘制。转动惯量取决于质量分布、轴方向和参考点。');f.save()

f=fig('compliance-virtual-spring','接触时希望末端像什么：虚拟质量、弹簧与阻尼','一维平移；这是一种目标交互行为，并不要求在机械臂上真的安装弹簧。',580)
f.line(110,160,110,370,BLUE,width=7);spring(f,110,235,310)
f.text(240,195,'$K_d$',28,PURPLE)
f.line(110,325,230,325,GREEN,width=3);f.path('M230 305 L230 345 L315 345 L315 305 M275 325 L420 325',GREEN,3);f.text(270,385,'$D_d$',28,GREEN)
f.rect(420,205,170,145,fill='#e6eff7');f.text(505,280,'$M_d$',32,BLUE,'middle')
arr(f,590,280,770,280,ORANGE);f.text(670,250,'$f_{\\mathrm{ext}}$',28,ORANGE)
f.text(505,405,'$e=x-x_d$',27,BLUE,'middle')
f.box(835,145,325,290,'三个参数各管什么',[
 '质量：起步有多难',
 '阻尼：运动有多受抑制',
 '刚度：偏离后拉回多强',
 '接触关系不只是一条轨迹'],PURPLE)
f.text(600,490,'$M_d\\ddot e+D_d\\dot e+K_de=f_{\\mathrm{ext}}$',32,BLUE,'middle')
f.footer('原创单轴等效模型；图中没有画真实机器人动力学、内环、延迟及饱和，不能据此直接保证闭环稳定。');f.save()

f=fig('impedance-admittance-loops','同一柔顺目标，两种控制信号流','对比常见实现：力矩接口上的阻抗控制，与位置／速度接口上的导纳控制。',660)
for y,labels in [(150,[('运动反馈',['$x,\\dot x$、参考运动']),('阻抗控制器',['误差 → 恢复力／力矩']),('力矩内环 + 机器人',['接受 $\\tau_{\\mathrm{cmd}}$','真实外力作用于机器人'])]),(410,[('外力测量',['$f_{\\mathrm{ext}}$','去偏置与工具重力']),('虚拟导纳模型',['力 → 运动修正','数值积分得到 $x_c$']),('位置／速度内环',['跟踪运动指令','机器人与环境接触'])])]:
 for x,(title,ls),c in zip([30,435,840],labels,[GREEN,PURPLE,BLUE]):f.box(x,y,330,170,title,ls,c)
 arr(f,370,y+85,425,y+85);arr(f,775,y+85,830,y+85)
 f.path(f'M1005 {y+175} L1005 {y+195} L195 {y+195} L195 {y+175}',GREEN,2)
 arr(f,195,y+190,195,y+172,GREEN)
f.text(600,382,'上排：机器人运动反馈闭环；下排：机器人接触力反馈闭环。',24,anchor='middle')
f.footer('原创控制框架；两种方案都需要反馈。信号因果方向不等于机器人与环境之间只有单向物理作用。');f.save()

f=fig('compliance-step-response','同样的外力，刚度决定最终让开多少','理想单轴模型；静止参考、零初值、恒定外力为 10 N，质量为 1 kg，阻尼均取临界值。',570)
arr(f,90,430,1120,430);arr(f,90,430,90,140)
f.text(1140,470,'$t\\;(s)$',23);f.text(105,130,'$e\\;(m)$',25)
for t in [0,0.5,1]:
 x=90+1000*t;f.line(x,430,x,437);f.text(x,465,f'${t}$',19,anchor='middle')
for value in [0.025,0.05,0.1]:
 y=430-2400*value;f.line(84,y,90,y);f.text(76,y+6,f'${value}$',18,anchor='end')
for k,c in [(100,BLUE),(400,GREEN)]:
 w=math.sqrt(k);pts=[]
 for i in range(201):
  t=i/200;value=10/k*(1-(1+w*t)*math.exp(-w*t));pts.append((90+1000*t,430-2400*value))
 f.path('M'+' L'.join(f'{x:.2f} {y:.2f}' for x,y in pts),c,4)
 f.text(700,180 if k==100 else 330,f'$K_d={k}\\;\\mathrm{{N/m}},\\quad e_{{\\infty}}={10/k}\\;\\mathrm{{m}}$',24,c)
f.text(600,510,'$e_{\\infty}=f_0/K_d,\\qquad D_d=2\\sqrt{M_dK_d}$',28,PURPLE,'middle')
f.footer('原创解析曲线，非机械臂实测；不包含内环误差、接触切换、测量噪声、采样延迟或执行器饱和。');f.save()

if __name__=='__main__':
 from playwright.sync_api import sync_playwright
 import re
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True)
  for n in NAMES:
   path=OUT/(n+'.svg');h=int(re.search(r'height="(\d+)"',path.read_text())[1])
   page=b.new_page(viewport={'width':1200,'height':h},device_scale_factor=2);page.goto(path.resolve().as_uri());page.screenshot(path=str(path.with_suffix('.png')));page.close()
  b.close()
