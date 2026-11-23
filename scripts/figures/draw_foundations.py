"""Original readable SVG diagrams and Chromium PNG exports for foundation notes.
Run: python scripts/figures/draw_foundations.py [--png]
"""
from pathlib import Path
from html import escape
import math
import argparse
import io
import re
from functools import lru_cache
from xml.etree import ElementTree as ET
from matplotlib.mathtext import math_to_image, MathTextParser
from matplotlib.font_manager import FontProperties
from PIL import ImageFont

@lru_cache(maxsize=1024)
def latex_svg(formula, size, color):
 """LaTeX math layout as portable SVG paths; no browser font dependency."""
 formula = formula.replace(r'\boldsymbol\omega', r'\mathbf{\omega}')
 formula = re.sub(r'\\(mathbf|mathbb) ([A-Za-z])', r'\\\1{\2}', formula)
 prop = FontProperties(size=size, math_fontfamily='stix')
 metrics = MathTextParser('path').parse(formula, dpi=72, prop=prop)
 buf = io.BytesIO()
 math_to_image(formula, buf, prop=prop, dpi=72, format='svg', color=color)
 root = ET.fromstring(buf.getvalue())
 for parent in root.iter():
  for child in list(parent):
   if child.get('id') == 'patch_1':
    parent.remove(child)
 return metrics.width, metrics.height, metrics.depth, root

@lru_cache(maxsize=64)
def label_font(size):
 return ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', size)


OUT=Path(__file__).resolve().parents[2]/'wiki/imgs'
INK='#18364d'; BLUE='#2473a6'; PURPLE='#8061bb'; GREEN='#278977'; ORANGE='#cf7446'; MUTED='#607789'
COLORS=[BLUE,PURPLE,GREEN,ORANGE]
class Fig:
 def __init__(self,name,title,subtitle='',height=560):
  self.name=name;self.h=height
  self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-label="{escape(title)}">', '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0L9 4.5L0 9" fill="#647f93"/></marker></defs><style>text{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif}</style>', f'<rect width="1200" height="{height}" rx="18" fill="#f4f7fb"/>', '<rect width="1200" height="95" rx="18" fill="#153d5c"/><rect y="75" width="1200" height="20" fill="#153d5c"/>']
  self.text(30,40,title,29,'white',bold=True);self.text(30,76,subtitle,19,'#d1e4f1')
 def text(self,x,y,t,size=23,color=INK,anchor='start',bold=False):
  t = str(t)
  spans = re.split(r'(\$[^$]+\$)', t)
  if len(spans) == 1:
   self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{600 if bold else 400}">{escape(t)}</text>')
   return
  widths = [latex_svg(v,size,color)[0] if v.startswith('$') else label_font(size).getlength(v) for v in spans]
  cursor = x - (sum(widths)/2 if anchor == 'middle' else sum(widths) if anchor == 'end' else 0)
  for v,w in zip(spans,widths):
   if v.startswith('$'):
    _,h,depth,root = latex_svg(v,size,color)
    # Preserve the math source in the SVG for subsequent editing.
    inner = ''.join(ET.tostring(child,encoding='unicode') for child in root)
    self.parts.append(f'<svg x="{cursor}" y="{y-h+depth}" width="{w}" height="{h}" viewBox="{root.attrib["viewBox"]}" data-latex="{escape(v,quote=True)}">{inner}</svg>')
   elif v:
    self.parts.append(f'<text x="{cursor}" y="{y}" font-size="{size}" fill="{color}" font-weight="{600 if bold else 400}">{escape(v)}</text>')
   cursor += w
 def rect(self,x,y,w,h,fill='white',stroke='#d6e1ea',r=12):
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
 def line(self,x,y,x2,y2,color='#647f93',arrow=False,dash=False,width=2):
  self.parts.append(f'<path d="M{x} {y}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="7 5"' if dash else '')+'/>')
 def path(self,d,color=BLUE,width=3): self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')
 def box(self,x,y,w,h,title,lines=(),color=BLUE):
  self.rect(x,y,w,h,stroke=color);self.rect(x,y,5,h,color,color,0)
  self.text(x+18,y+34,title,24,color,bold=True)
  for i,t in enumerate(lines): self.text(x+18,y+72+i*40,t,21)
 def footer(self,t): self.text(30,self.h-24,t,19,MUTED)
 def save(self):
  OUT.mkdir(parents=True,exist_ok=True);(OUT/(self.name+'.svg')).write_text(''.join(self.parts)+'</svg>')
 def grid(self,x,y,values,cell=52,colors=None):
  for i,row in enumerate(values):
   for j,v in enumerate(row):
    self.rect(x+j*cell,y+i*cell,cell,cell,(colors[i][j] if colors else '#eef4fa'),'#bdd1df',0)
    self.text(x+(j+.5)*cell,y+(i+.65)*cell,v,22,anchor='middle')

def flow(name,title,nodes,subtitle='',foot='原创原理示意；箭头表示数据或计算流。'):
 f=Fig(name,title,subtitle,440);n=len(nodes);gap=28;width=(1140-gap*(n-1))/n
 for i,(t,lines) in enumerate(nodes):
  x=30+i*(width+gap);f.box(x,145,width,200,t,lines,COLORS[i%4])
  if i<n-1:f.line(x+width+4,244,x+width+gap-5,244,arrow=True)
 f.footer(foot);f.save()

def curves(name,title,kind):
 f=Fig(name,title,'实线为函数值；坐标单位为无量纲，横轴为输入 x。',510)
 x0,y0,w,h=110,135,740,290
 funcs={'relu':(lambda x:max(0,x),'$\\operatorname{ReLU}(x)=\\max(0,x)$',(-1,4)), 'leaky':(lambda x:x if x>=0 else .1*x,'Leaky ReLU：负半轴斜率 $\\alpha=0.1$',(-1,4)), 'tanh':(math.tanh,'$\\tanh(x)$：输出范围 (−1, 1)',(-1.3,1.3)), 'sigmoid':(lambda x:1/(1+math.exp(-x)),'$\\sigma(x)=\\frac{1}{1+e^{-x}}$',(-.2,1.2))}
 fun,desc,(lo,hi)=funcs[kind]
 def px(x):return x0+(x+4)*w/8
 def py(y):return y0+(hi-y)*h/(hi-lo)
 for x in [-4,-2,0,2,4]:
  f.line(px(x),y0,px(x),y0+h,'#dee7ed');f.text(px(x),y0+h+28,x,19,MUTED,'middle')
 for y in ([0,.5,1] if kind=='sigmoid' else [-1,0,1] if kind=='tanh' else [0,2,4]):
  f.line(x0,py(y),x0+w,py(y),'#dee7ed');f.text(x0-15,py(y)+7,y,19,MUTED,'end')
 f.line(x0,py(0),x0+w+15,py(0),arrow=True);f.line(px(0),y0+h,px(0),y0-10,arrow=True)
 pts=[(px(x),py(fun(x))) for x in [i/40 for i in range(-160,161)]]
 f.path('M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in pts),BLUE,4)
 f.text(895,190,'函数性质',25,BLUE,bold=True)
 notes={'relu':['负区输出为 0','正区斜率为 1','在 $x=0$ 处不可导'],'leaky':['负区保留小梯度','正区斜率为 1','图示 $\\alpha=0.1$'],'tanh':['零中心输出','两侧逐渐饱和','并非分段直线'],'sigmoid':['$\\sigma(0)=0.5$','两侧逐渐饱和','输出可解释为概率']}
 for i,n in enumerate(notes[kind]): f.text(895,240+i*40,n,21)
 f.footer(desc);f.save()

def rnn(name='foundations-rnn-unrolled',words=None,many=True):
 words=words or ['$x_1$','$x_2$','$x_3$','$x_4$'];n=len(words)
 f=Fig(name,'RNN：时间展开与共享参数','隐藏状态沿时间传递；每个时间步使用同一组权重。',530)
 gap=1060/n;cy=240
 f.text(18,cy+6,'$h_0$',22,GREEN)
 for i,word in enumerate(words):
  x=80+i*gap;f.box(x,180,gap-40,120,f'循环单元 {i+1}',[],BLUE)
  f.text(x+(gap-40)/2,260,'共享 $W,U,b$',20,anchor='middle')
  f.text(x+(gap-40)/2,145,word,25,PURPLE,'middle');f.line(x+(gap-40)/2,153,x+(gap-40)/2,177,arrow=True)
  f.line(x-36,cy,x-3,cy,arrow=True)
  if many:
   f.line(x+(gap-40)/2,302,x+(gap-40)/2,350,arrow=True);f.text(x+(gap-40)/2,382,f'$y_{{{i+1}}}$',24,ORANGE,'middle')
  elif i==n-1:
   f.line(x+(gap-40)/2,302,x+(gap-40)/2,350,arrow=True);f.text(x+(gap-40)/2,382,'整段序列的输出 y',22,ORANGE,'middle')
  if i<n-1:f.text(x+gap-15,222,f'$h_{{{i+1}}}$',20,GREEN,'middle')
 f.text(600,449,'$h_t=\\tanh(W_{xh}x_t+W_{hh}h_{t-1}+b_h)$',26,anchor='middle');f.footer('$h_0$ 为初始状态；$y_t$ 的含义取决于具体任务，不一定是下一个词。');f.save()

def rnn_cell():
 f=Fig('foundations-rnn-cell','RNN 单元：输入与历史如何汇合','每次更新同时使用当前输入 $x_t$ 和上一隐藏状态 $h_{t-1}$。',580)
 f.box(40,155,255,110,'当前输入 $x_t$',['维度 $d_x$'],PURPLE);f.box(40,320,255,110,'历史 $h_{t-1}$',['维度 $d_h$'],GREEN)
 f.box(405,205,345,180,'加权求和 → tanh',['$W_{xh}x_t+W_{hh}h_{t-1}+b_h$','输出新状态 $h_t$，维度 $d_h$'],BLUE)
 f.line(300,210,400,270,arrow=True);f.line(300,365,400,320,arrow=True)
 f.box(855,150,300,125,'输出层',['$y_t=g(W_{hy}h_t+b_y)$'],ORANGE);f.box(855,340,300,110,'下一个时间步',['$h_t$ 作为新的历史状态'],GREEN)
 f.line(755,270,850,210,arrow=True);f.line(755,320,850,390,arrow=True)
 f.footer('权重在时间上共享；隐藏维度不必等于输入维度或输出维度。');f.save()

def lstm():
 f=Fig('foundations-lstm','LSTM：细胞状态与三个门','门值在 0–1 之间，逐元素控制遗忘、写入和输出。',660)
 f.text(35,160,'$C_{t-1}$',25,GREEN);f.text(1100,160,'$C_t$',25,GREEN)
 f.line(110,153,1080,153,GREEN,arrow=True,width=4)
 f.rect(365,124,60,60,'#e4f1ed',GREEN,30);f.text(395,164,'×',30,GREEN,'middle')
 f.rect(745,124,60,60,'#e4f1ed',GREEN,30);f.text(775,164,'+',30,GREEN,'middle')
 f.box(270,300,230,125,'遗忘门 $f_t$',['保留多少旧记忆'],BLUE);f.line(395,298,395,188,arrow=True)
 f.box(550,300,240,125,'输入门 $i_t$ × 候选',['决定写入内容'],PURPLE);f.line(670,298,775,188,arrow=True)
 f.box(880,300,275,125,'输出门 $o_t$',['筛选 tanh($C_t$)'],ORANGE)
 f.line(970,157,1015,298,arrow=True);f.line(1015,430,1015,485,arrow=True)
 f.text(1015,520,'$h_t$',27,ORANGE,'middle')
 f.text(38,480,'各门与候选共同读取：$x_t$、$h_{t-1}$',23)
 f.text(40,548,'$C_t=f_t\\odot C_{t-1}+i_t\\odot\\widetilde C_t$',26,GREEN)
 f.footer('$h_t=o_t\\odot\\tanh(C_t)$；$C_t$ 与 $h_t$ 都会传给下一时间步。');f.save()

def cnn_patch():
 f=Fig('foundations-cnn-patch','CNN 局部计算：逐元素相乘，再求和','深度学习中的 Conv2d 通常实现互相关，不翻转卷积核。',530)
 f.text(45,145,'输入局部区域',25,BLUE);f.grid(45,170,[[1,2,3],[4,5,6],[7,8,9]],65)
 f.text(320,268,'⊙',38,PURPLE,'middle');f.text(410,145,'卷积核',25,PURPLE);f.grid(410,170,[[1,0,-1]]*3,65)
 f.line(640,266,750,266,arrow=True);f.box(790,175,350,185,'单个输出位置',['$(1-3)+(4-6)$','$+(7-9)=-6$','此处偏置 $b=0$'],GREEN)
 f.footer('核沿输入滑动，重复这一步形成特征图；此示例原字符图的 −5 已纠正为 −6。');f.save()

def pooling():
 f=Fig('foundations-cnn-pooling','最大池化：每个局部区域只保留最大值','窗口 $2\\times2$，步长 2；没有可训练的卷积核。',550)
 vals=[list(range(i*4+1,i*4+5)) for i in range(4)];palette=['#dcecf6','#e9e1f5','#dcefe8','#f6e7dc']
 colors=[[palette[(i//2)*2+j//2] for j in range(4)] for i in range(4)]
 f.grid(75,155,vals,65,colors);f.line(390,285,690,285,arrow=True)
 f.text(530,240,'取各区域最大值',23,anchor='middle');f.grid(780,205,[[6,8],[14,16]],85)
 f.text(210,460,'输入：$4\\times4$',25,BLUE,'middle');f.text(865,460,'输出：$2\\times2$',25,GREEN,'middle');f.footer('保留局部强响应，降低空间分辨率；池化不会自动保证所有平移下的输出不变。');f.save()

def dilation():
 f=Fig('foundations-cnn-dilation','空洞卷积：采样点变稀，覆盖范围变大','单输入、单输出通道的空间核示意；两边都只有 9 个采样权重。',590)
 f.text(230,145,'普通 $3\\times3$，$d=1$',25,BLUE,'middle');f.grid(125,195,[['●']*3]*3,68)
 a=[['●' if i%2==0 and j%2==0 else '' for j in range(5)] for i in range(5)]
 f.text(825,145,'空洞 $3\\times3$，$d=2$',25,PURPLE,'middle');f.grid(650,175,a,65)
 f.text(230,465,'有效覆盖：$3\\times3$',24,BLUE,'middle');f.text(815,540,'有效覆盖：$5\\times5$',24,PURPLE,'middle');f.footer('有效核大小 = 1 + (核大小 − 1) × dilation；空隙不增加权重数量。');f.save()

def kl():
 f=Fig('foundations-kl','KL 散度：用 Q 编码来自 P 的样本','离散分布示例；使用自然对数，单位为 nat。',570)
 p=[.7,.2,.1];q=[.2,.3,.5];x0=75;base=390;scale=270
 for i,(a,b) in enumerate(zip(p,q)):
  x=x0+i*190;f.rect(x,base-a*scale,52,a*scale,BLUE,BLUE,3);f.rect(x+60,base-b*scale,52,b*scale,PURPLE,PURPLE,3)
  f.text(x+26,base-a*scale-12,a,22,BLUE,'middle');f.text(x+86,base-b*scale-12,b,22,PURPLE,'middle');f.text(x+56,425,chr(65+i),23,anchor='middle')
 f.line(55,base,650,base);f.text(75,148,'■ P（真实分布）',22,BLUE);f.text(320,148,'■ Q（模型分布）',22,PURPLE)
 f.box(710,170,445,250,'按 P 加权的额外代价',['$D_{\\mathrm{KL}}(P\\Vert Q)=\\sum_i P_i\\log\\frac{P_i}{Q_i}$','本例约为 0.635 nat','$D_{\\mathrm{KL}}(Q\\Vert P)$ 约为 0.676 nat','交换 P、Q，结果通常不同'],GREEN)
 f.footer('$D_{\\mathrm{KL}}\\geq0$；若 $P>0$ 而 $Q=0$，对应 KL 发散。它不是对称距离。');f.save()

def mdp():
 f=Fig('foundations-mdp','MDP：状态、动作、奖励与下一状态','以时刻 t 的一次交互为单位，明确每条箭头携带什么。',540)
 f.box(80,175,360,190,'智能体 / 策略 π',['读取当前状态 $S_t$','选择 $A_t\\sim\\pi(\\cdot\\mid S_t)$'],BLUE)
 f.box(760,175,360,190,'环境 / 转移模型',['接收动作 $A_t$','采样下一状态与奖励'],GREEN)
 f.line(445,220,755,220,arrow=True);f.text(600,200,'动作 $A_t$',24,PURPLE,'middle')
 f.line(755,325,445,325,arrow=True);f.text(600,305,'$S_{t+1},\\ R_{t+1}$',24,ORANGE,'middle')
 f.text(600,435,'状态 $S_t$ 是对决策相关历史的充分摘要；奖励不等于动作标签。',23,anchor='middle')
 f.footer('一般可写联合转移 $p(s^{\\prime},r\\mid s,a)$；机器人部分可观测场景还需要观测与记忆。');f.save()

def peft_taxonomy():
 f=Fig('foundations-peft-taxonomy','PEFT：只更新少量参数的三条路线','按主要机制组织，不把所有变体塞进一张小字树状图。',530)
 for i,(title,ls) in enumerate([('添加参数',['冻结主干，插入小模块','Adapter / Prefix / Prompt','保留独立的任务参数']),('选择参数',['只训练已有权重的一部分','示例：只更新 bias 的 BitFit','其余参数保持冻结']),('重参数化更新',['用低秩因子表示 $\\Delta W$','LoRA：$\\Delta W=BA$','可与量化主干等组合'])]):
  f.box(30+i*390,155,360,270,title,ls,COLORS[i])
 f.footer('分类帮助理解训练方式，不代表后一个类别在所有任务上优于前一个。');f.save()

def peft_routes():
 flow('foundations-peft-routes','PEFT：从完整副本到轻量任务增量',[('全量微调',['每个任务更新 W','存整套模型参数']),('冻结主干',['共享预训练 $W_0$','只改变小量参数']),('LoRA 增量',['$\\Delta W=BA$','任务切换只换增量']),('量化组合',['例如 QLoRA','量化 $W_0$ + LoRA'])],'这是一张设计路线图，不是历史年份或性能排名。','训练参数变少不等于所有显存都消失；激活、优化器和量化状态仍需考虑。')

def lora():
 f=Fig('foundations-lora','LoRA：冻结主支路，训练低秩增量支路','输入列向量 $x\\in\\mathbb R^k$，输出 $h\\in\\mathbb R^d$；秩 r 远小于 k、d。',600)
 f.box(40,240,150,100,'输入 x',[],BLUE)
 f.box(345,140,350,115,'冻结 $W_0$',['原始映射：$W_0x$'],BLUE)
 f.box(300,345,225,125,'训练 A',['$k\\to r$','$A\\in\\mathbb{R}^{r\\times k}$'],PURPLE)
 f.box(590,345,225,125,'训练 B',['$r\\to d$','$B\\in\\mathbb{R}^{d\\times r}$'],GREEN)
 f.line(195,280,330,200,arrow=True);f.line(195,305,285,402,arrow=True);f.line(530,402,580,402,arrow=True)
 f.rect(930,245,65,65,'#e5f1ec',GREEN,32);f.text(962,290,'+',32,GREEN,'middle')
 f.line(700,200,930,265,arrow=True);f.line(820,400,945,317,arrow=True);f.line(1000,277,1125,277,arrow=True);f.text(1100,250,'输出 h',23,anchor='middle')
 f.text(600,530,'$h=W_0x+\\frac{\\alpha}{r}BAx$',28,anchor='middle');f.footer('典型初始化 A 随机、B 为零，使初始增量为零；可训练参数量 $r(k+d)$。');f.save()

def taxonomy():
 f=Fig('foundations-attention-map','注意力变体：五个可以交叉组合的维度','同一个层可以同时是“多头、自注意力、因果、局部或稀疏”。',610)
 entries=[('信息来源','自注意力 / 交叉注意力'),('可见范围','全局 / 局部 / 块'),('连接密度','稠密 / 稀疏'),('头的组织','单头 / 多头'),('计算与掩码','因果 / 双向 / 滑窗 / 线性')]
 for i,(a,b) in enumerate(entries):
  y=125+i*78;f.box(35,y,265,64,a,[],COLORS[i%4]);f.line(307,y+33,350,y+33,arrow=True);f.rect(365,y,800,64);f.text(390,y+41,b,24)
 f.footer('这些分类并非互斥；线性注意力改变计算形式，FlashAttention 优化精确注意力的 IO。');f.save()

def attention():
 flow('foundations-attention-qkv','注意力：从相关性分数到信息聚合',[('投影',['输入 → Q、K、V','Q 查询，K 索引']),('打分',['$S=\\frac{QK^{\\mathsf{T}}}{\\sqrt{d_k}}$','行：query；列：key']),('归一化',['加可见性掩码','$A=\\operatorname{softmax}(S)$']),('聚合',['$\\mathrm{output}=AV$','每行加权汇总 V'])],'自注意力：Q、K、V 来自同一序列；交叉注意力：Q 与 K/V 来自不同序列。')

def communication(name,kind):
 f=Fig(name,kind+'：两张 GPU 的数据如何变化','示例用两个元素的向量，展示通信前后每张 GPU 持有的数据。',500)
 data={'Broadcast':(['[a, b]','未初始化'],['[a, b]','[a, b]'],'源 GPU 0 复制给所有卡'), 'AllReduce':(['[1, 2]','[3, 4]'],['[4, 6]','[4, 6]'],'逐元素相加，所有卡得到完整结果'), 'Reduce-Scatter':(['[1, 2]','[3, 4]'],['[4]','[6]'],'先逐元素求和，再按分片分发'), 'AllGather':(['[4]','[6]'],['[4, 6]','[4, 6]'],'收集各卡分片，每卡得到拼接结果')}
 before,after,desc=data[kind]
 for i in range(2):
  y=145+i*125;f.box(40,y,320,95,'GPU '+str(i)+'：'+before[i],[],COLORS[i]);f.box(820,y,340,95,'GPU '+str(i)+'：'+after[i],[],COLORS[i]);f.line(370,y+48,810,y+48,arrow=True)
 f.rect(440,177,300,150,'#ecf2f8');f.text(590,228,kind,24,BLUE,'middle');f.text(590,272,'集体通信',22,MUTED,'middle')
 f.footer(desc+'；图示为语义，不代表实际网络拓扑或通信算法。');f.save()

def pipeline():
 f=Fig('foundations-pipeline-parallel','流水线并行：层分到不同 GPU，微批次依次经过','只示意前向调度；真实训练还需要反向、激活传递和具体调度。',550)
 for i in range(4):
  f.text(35,175+i*70,'GPU '+str(i),22,BLUE)
  for j in range(3):
   x=165+(i+j)*155;f.rect(x,140+i*70,140,55,['#dcecf6','#e9e1f5','#dcefe8'][j]);f.text(x+70,176+i*70,'微批次 '+str(j+1),21,anchor='middle')
 f.text(170,465,'时间步  →',23);f.footer('斜向错开让相邻设备处理不同微批次；空白为流水线启动或排空的气泡。');f.save()

def overlap():
 f=Fig('foundations-ddp-overlap','DDP：梯度桶就绪后，让通信与反向计算重叠','一条时间线上的示意；实际桶顺序和重叠程度取决于运行时。',460)
 f.text(35,185,'反向计算',23,BLUE);f.text(35,300,'梯度归约',23,GREEN)
 for i in range(3):
  x=205+i*245;f.box(x,135,220,85,'梯度桶 '+str(i+1),[],BLUE)
  f.box(x+90,255,220,85,'AllReduce '+str(i+1),[],GREEN)
  f.line(x+180,225,x+180,250,arrow=True)
 f.footer('不是等所有层反向完成才启动全部通信；但也不意味着通信一定能完全隐藏。');f.save()

def rigid_frames():
 f=Fig('foundations-rigid-frames','坐标变换：点没有动，表达它的坐标系变了','B 系相对 A 系绕 z 轴转 +90°；平移 $\\mathbf t=(1,2,0)$ 米。',620)
 # Top view, one meter = 90 SVG units.
 ox,oy=115,485;bx,by=205,305;px,py=205,215
 f.line(ox,oy,ox+390,oy,BLUE,arrow=True);f.line(ox,oy,ox,oy-330,BLUE,arrow=True)
 f.text(510,492,'$x_A$',22,BLUE);f.text(95,135,'$y_A$',22,BLUE);f.text(75,520,'$O_A$',22,BLUE)
 f.line(bx,by,bx,by-145,GREEN,arrow=True);f.line(bx,by,bx-145,by,GREEN,arrow=True)
 f.text(bx+10,150,'$x_B$',23,GREEN);f.text(40,290,'$y_B$',23,GREEN)
 f.line(ox,oy,bx,by,PURPLE,arrow=True);f.text(230,400,r'$\mathbf{t}$',27,PURPLE)
 f.line(bx,by,px,py,ORANGE,arrow=True,width=4);f.rect(px-6,py-6,12,12,ORANGE,ORANGE,6)
 f.text(px+22,py,'点 P',25,ORANGE)
 f.line(ox,oy,px,py,'#9eb2c2',dash=True)
 f.box(605,155,550,160,'同一个点的两套坐标',['B 中：${}^B\\!p=(1,0,0)\\,\\mathrm{m}$','A 中：${}^A\\!p=(1,3,0)\\,\\mathrm{m}$'],BLUE)
 f.box(605,355,550,150,'先换基，再加原点偏移',['${}^A\\!p={}^A\\!R_B\\,{}^B\\!p+{}^A\\!t_B$','方向向量只乘 R，不加平移'],GREEN)
 f.footer('俯视图；z 轴垂直图面向外，所有坐标轴右手定向。');f.save()

def rigid_omega():
 f=Fig('foundations-rigid-omega','角速度与线速度：r 径向，v 沿切线','从 +z 方向俯视：$\\omega$ 指向观察者（⊙），按右手定则逆时针旋转。',600)
 cx,cy,rad=275,320,140
 f.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="white" stroke="#bbccda" stroke-width="2" stroke-dasharray="8 6"/>')
 f.text(cx,cy+10,'⊙',37,GREEN,'middle');f.text(cx-8,cy+50,'O，$\\omega$',23,GREEN)
 f.line(cx+12,cy,cx+rad,cy,BLUE,arrow=True,width=4);f.text(cx+65,cy+34,r'$\mathbf{r}$',27,BLUE)
 f.rect(cx+rad-6,cy-6,12,12,ORANGE,ORANGE,6);f.text(cx+rad+15,cy+34,'P',25,ORANGE)
 f.line(cx+rad,cy,cx+rad,cy-115,ORANGE,arrow=True,width=4);f.text(cx+rad+15,cy-95,r'$\mathbf{v}$',27,ORANGE)
 f.line(cx+rad,cy,cx+rad-95,cy,PURPLE,arrow=True,width=3);f.text(cx+rad-80,cy-22,'$\\mathbf a_c$',23,PURPLE)
 f.box(620,160,530,165,'固定 O、固连点 P',['$\\mathbf v=\\boldsymbol\\omega\\times\\mathbf r$','$\\omega$ 沿 +z，r 沿 +x，此刻 v 沿 +y'],BLUE)
 f.box(620,370,530,130,'匀速圆周运动',['向心加速度：$\\mathbf a_c=\\boldsymbol\\omega\\times(\\boldsymbol\\omega\\times\\mathbf r)$','指向转轴，不是向外的真实加速度'],PURPLE)
 f.footer('若 O 也在移动：$\\mathbf v_P=\\mathbf v_O+\\boldsymbol\\omega\\times\\mathbf r_{OP}$；图示为固定原点的特例。');f.save()


def main():
 rigid_frames();rigid_omega();kl();mdp();rnn();rnn_cell();lstm();cnn_patch();pooling();dilation();lora();peft_taxonomy();peft_routes();taxonomy();attention();pipeline();overlap()
 for k,t in [('relu','ReLU：负区截断，正区保留'),('leaky','Leaky ReLU：负区保留小斜率'),('tanh','Tanh：零中心的平滑压缩'),('sigmoid','Sigmoid：平滑映射到 0–1')]:curves('foundations-'+k,t,k)
 for k in ['Broadcast','AllReduce','Reduce-Scatter','AllGather']:communication('foundations-'+k.lower(),k)
 flow('foundations-cnn-architecture','CNN 分类网络：空间特征逐层汇聚',[('输入',['$H\\times W\\times C$','图像或网格信号']),('特征提取',['卷积 + 激活','可选池化 / 下采样']),('特征汇聚',['全局平均池化','或 Flatten']),('任务输出',['线性分类器','类别分数 / 概率'])],'示意架构；卷积层数、通道数及分类头由任务决定。')
 flow('foundations-cnn-features','CNN 层次表征：局部响应逐步组合',[('像素',['原始强度 / 颜色']),('浅层',['边缘与局部纹理']),('中层',['形状与部件组合']),('深层',['更大范围的模式','任务相关表征'])],'帮助理解的定性示意；不意味着每个通道都能被唯一命名。')
 flow('foundations-cnn-channels','卷积输出通道：一个滤波器产生一张响应图',[('输入张量',['$32\\times32\\times3$','3 个颜色通道']),('64 个滤波器',['每个 $3\\times3\\times3$','每核跨全部输入通道']),('输出张量',['$32\\times32\\times64$','64 张响应图'])],'示例假设 stride = 1、padding = 1、$d=1$。')
 flow('foundations-cnn-head','分类头：Flatten 与全连接映射',[('特征张量',['例如 $8\\times8\\times48$']),('Flatten',['保留数值、重排形状','3072 维向量']),('全连接',['$W\\in\\mathbb{R}^{64\\times3072}$','产生 64 维输出'])],'Flatten 不学习参数；每个线性输出可读取全部输入分量。')
 flow('foundations-cnn-logits','隐层与输出层：非线性特征和类别概率',[('输入特征',['向量 x']),('隐层',['$h=\\operatorname{ReLU}(Wx+b)$']),('输出分数',['$z=W_oh+b_o$']),('概率',['$\\operatorname{softmax}(z)$','各类别概率和为 1'])],'交叉熵实现常直接接收 logits，不要无条件在损失前再加 softmax。')
 flow('foundations-cnn-transfer','CNN 迁移学习：复用表征，适配任务',[('预训练骨干',['加载已有权重']),('选择冻结范围',['可先冻结早期层','按数据量逐步解冻']),('替换任务头',['匹配目标类别数']),('微调与验证',['监控泛化与过拟合'])],'浅层通常更通用，但冻结策略不是由层深唯一决定的规则。')
 flow('foundations-cnn-receptive','感受野递增：逐层看到更大输入区域',[('第 1 层',['$3\\times3$ 核','感受野 $3\\times3$']),('第 2 层',['$3\\times3$ 核','感受野 $5\\times5$']),('第 3 层',['$3\\times3$ 核','感受野 $7\\times7$'])],'假设所有 stride = 1、$d=1$，描述理论感受野。')
 flow('foundations-cnn-edge','用固定核理解边缘响应',[('图像局部',['比较相邻列的强度']),('水平差分核',['每行权重 [−1, 0, 1]']),('响应图',['左右强度变化大','对竖直边界响应更强'])],'这里展示固定核的直觉；真实 CNN 的核通常由训练学习。')
 rnn('foundations-rnn-language',['我','爱','猫'],True)
 rnn('foundations-rnn-classification',['我','爱','这部','电影'],False)
 flow('foundations-rnn-generation','图像描述：初始条件引导序列生成',[('图片编码',['图像 → 特征向量']),('初始化 RNN',['特征作初始状态','或额外输入条件']),('逐步生成',['预测：一 / 只 / 猫','前一步输出参与后续']),('停止',['生成结束标记'])],'简化接口示意；图片条件注入方式由模型实现决定。')
 flow('foundations-single-gpu','单 GPU：一个优化步骤',[('取样',['读取一个 batch']),('前向',['预测并计算 loss']),('反向',['计算参数梯度']),('更新',['optimizer.step()'])])
 flow('foundations-ddp','DDP：不同数据，相同模型更新',[('分配数据',['每卡取不同子集','起始模型一致']),('本地计算',['各自前向与反向','得到本地梯度']),('梯度同步',['AllReduce','按约定求平均']),('各卡更新',['同样优化器状态','获得相同参数'])],'梯度等价全局 batch 平均需要各卡样本数和损失归约方式匹配。')
 flow('foundations-fsdp','FSDP：按模块临时聚合，长期分片持有',[('本地分片',['参数 / 梯度','优化器状态分片']),('前向按需聚合',['AllGather 参数','计算后可重新分片']),('反向与归约',['按需再次聚合参数','Reduce-Scatter 梯度']),('分片更新',['各卡更新自己的分片'])],'FULL_SHARD 式流程示意；释放、预取时机与实际配置有关。')
 # A cross-entropy illustration with actual one-hot probabilities.
 f=Fig('foundations-cross-entropy','交叉熵：真实类别的概率越低，损失越大','单样本三分类；真实标签为类别 A，使用自然对数。',480)
 f.box(30,145,350,220,'真实标签 P',['$P=[1,0,0]$','只对类别 A 的 log Q 加权'],BLUE)
 f.box(420,145,350,220,'模型预测 Q',['$Q=[0.7,0.2,0.1]$','真实类别概率 $Q(A)=0.7$'],PURPLE)
 f.box(810,145,360,220,'损失 $H(P,Q)$',['$-\\sum_i P_i\\log Q_i=-\\log 0.7$','约为 0.357 nat'],GREEN)
 f.footer('若 Q(A) 降到 0.1，损失升为约 2.303；一般软标签需要对所有类别求和。');f.save()
 # Learning-rate schedule replaces a text-only pseudo diagram.
 f=Fig('foundations-lr-schedule','学习率日程：先预热，再余弦衰减','示意曲线；横轴为优化步，纵轴为学习率。',460)
 f.line(90,350,1110,350,arrow=True);f.line(90,350,90,120,arrow=True)
 pts=[(90+1020*t,(350-200*(t/.15 if t<.15 else .5*(1+math.cos(math.pi*(t-.15)/.85))))) for t in [i/100 for i in range(101)]]
 f.path('M'+'L'.join(f'{x:.1f} {y:.1f}' for x,y in pts),BLUE,4)
 f.text(165,395,'warmup',23,PURPLE,'middle');f.text(690,395,'cosine decay',23,GREEN,'middle');f.footer('学习率缩放与 warmup 长度需要验证，不能仅按 GPU 数机械设置。');f.save()

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--png',action='store_true');args=parser.parse_args();main()
 if args.png:
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
   browser=p.chromium.launch(headless=True)
   for path in sorted(OUT.glob('foundations-*.svg')):
    import re
    height=int(re.search(r'height="(\d+)"',path.read_text())[1])
    page=browser.new_page(viewport={'width':1200,'height':height},device_scale_factor=2)
    page.goto(path.resolve().as_uri());page.screenshot(path=str(path.with_suffix('.png')));page.close()
   browser.close()
 print('Generated original foundation diagrams in',OUT)
