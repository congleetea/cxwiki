"""Transformer teaching figures and offline MP4 animations. All math is LaTeX paths.
Run: python3 scripts/draw_transformer_series.py (requires Chromium, ffmpeg).
"""
from draw_foundations import Fig, BLUE, PURPLE, GREEN, ORANGE, MUTED, OUT
from pathlib import Path
import math, subprocess, tempfile
NAMES=[]; ANIMS={}
def new(name,title,sub='',h=570):
 NAMES.append(name);return Fig(name,title,sub,h)
def done(f):f.footer('原创教学示意；示例数值、颜色与头的分工不代表真实模型测量。');f.save()
def arrow(f,x,y,xx,yy,c=BLUE):f.line(x,y,xx,yy,c,True,width=3)
def flow(name,title,nodes,sub=''):
 f=new(name,title,sub,500)
 for i,(title,lines) in enumerate(nodes):
  x=30+395*i;f.box(x,150,350,235,title,lines,[BLUE,PURPLE,GREEN][i])
  if i<2 and name not in {'tf-qkv','tf-modal-tokens','tf-cross-attention'}:arrow(f,x+355,267,x+390,267)
 done(f)
def cell(f,x,y,label,active=True,w=130,c=BLUE):
 f.rect(x,y,w,56,'#dcecf6' if active else '#edf0f4',c if active else '#d6e1ea',6);f.text(x+w/2,y+36,label,24,c if active else MUTED,'middle')

flow('tf-token-lookup','01 · Token ID 怎样变成向量',[('分词与词表',['示意分词：我 / 爱 / 机器人','ID 只表示词表位置','同一词表必须配同一嵌入表']),('嵌入表查询',[r'$E\in\mathbb{R}^{v\times d}$',r'$e_i=E[\mathrm{id}_i,:]$','每个 ID 取一行，不是数值回归']),('加入位置信息',[r'经典结构：$X=\sqrt{d}E_{\mathrm{seq}}+P$',r'输出 $X\in\mathbb{R}^{n\times d}$','现代实现不一定沿用此缩放'])],'分词结果为教学设定；Token 不固定等于汉字或完整单词。')
f=new('tf-tensor-axes','三条轴：样本、位置、特征','把长度与特征维度分开看，后面所有矩阵乘法才不会混淆。')
f.text(55,150,r'一个样本的表示 $X\in\mathbb{R}^{4\times6}$',27,BLUE)
f.grid(80,195,[[f'${i+1}{j+1}$' for j in range(6)] for i in range(4)],58)
f.text(75,465,'每一行：一个位置的六维向量',23,GREEN)
f.box(585,175,555,240,'加入 batch 后',[r'$X\in\mathbb{R}^{b\times n\times d}$','$b$：独立样本，不互相做注意力','$n$：序列位置，可有 padding','$d$：每个位置的特征宽度'],PURPLE);done(f)
flow('tf-context-update','同一个 Token，进入上下文后可以有不同表示',[('相同词表条目',['“苹果很好吃”','“苹果发布了新设备”','假设“苹果”各为一个 Token']),('上下文混合',['自注意力读取句中其他位置','共享参数处理不同内容','表示随上下文与层数改变']),('输出上下文表示',['输入嵌入可以相同','隐藏状态通常不同','不能把单一维度硬解释成词义'])])

flow('tf-qkv','02 · 三种投影来自同一输入，但职责不同',[('Query：我想找什么',['$Q=XW_Q$','每个位置生成检索条件']),('Key：我有什么线索',['$K=XW_K$','与 Query 做点积匹配']),('Value：我要传递什么',['$V=XW_V$','按注意力权重混合内容'])],'自注意力的三者源头相同；交叉注意力的 Query 与 Key / Value 可来自不同序列。')
f=new('tf-attention-example','一行注意力：从三个分数算出二维输出','手算例子固定 Query 与 Keys，展示 softmax 与 Value 加权和。',600)
f.text(40,152,r'缩放后分数：$S=[0,\ln2,\ln3]$',27,BLUE)
f.text(40,206,r'$\mathrm{softmax}(S)=[1/6,2/6,3/6]$',28,PURPLE)
for i,(lab,h) in enumerate([('$1/6$',60),('$2/6$',120),('$3/6$',180)]):
 x=90+i*150;f.rect(x,435-h,75,h,fill=BLUE,stroke=BLUE);f.text(x+37,460,lab,23,BLUE,'middle')
f.box(625,160,530,290,'混合二维 Value',['$v_1=[6,0]$，$v_2=[0,3]$','$v_3=[2,2]$',r'$z=\frac{1}{6}v_1+\frac{2}{6}v_2+\frac{3}{6}v_3$','$z=[2,2]$'],GREEN);done(f)
f=new('tf-attention-shapes','矩阵路径：先算位置之间的关系，再聚合特征','这里省略 batch 与 head 轴，Query 长度可与 Key 长度不同。',520)
for x,t,ls,c in [(30,'Query × Key 转置',[r'$Q:n_q\times d_k$',r'$K^\mathsf{T}:d_k\times n_k$'],BLUE),(430,'逐行 softmax',[r'$S,A:n_q\times n_k$','每行表示一个 Query 的读取权重'],PURPLE),(830,'权重 × Value',[r'$V:n_k\times d_v$',r'$Z:n_q\times d_v$'],GREEN)]:f.box(x,155,340,225,t,ls,c)
arrow(f,375,265,422,265);arrow(f,775,265,822,265);done(f)

f=new('tf-multihead','03 · 多头不是反复计算同一份注意力','每个头有自己的投影；各头输出沿特征轴拼接，再做输出投影。',610)
f.box(30,235,210,120,'共同输入',[r'$X:n\times d$'],BLUE)
for i,c in enumerate([BLUE,PURPLE,GREEN]):
 y=130+i*135;f.box(360,y,390,106,f'头 {i+1}',['独立投影 → 注意力 → $Z_i$'],c);arrow(f,245,295,352,y+53,c);arrow(f,755,y+53,900,295,c)
f.box(910,220,260,170,'拼接后投影',['Concat 后乘 $W_O$',r'输出仍是 $n\times d$'],ORANGE);done(f)
f=new('tf-block','一个 Block：位置混合与特征变换轮流进行','以 Pre-LN 为例；原始 Transformer 使用 Post-LN。',640)
for i,(lab,col) in enumerate([('输入 $X$',BLUE),('LN → 注意力',PURPLE),('残差相加',GREEN),('LN → FFN',PURPLE),('残差相加',GREEN)]):
 y=125+i*82;f.rect(380,y,420,58,stroke=col);f.text(590,y+38,lab,25,col,'middle')
 if i<4:arrow(f,590,y+60,590,y+80)
f.path('M590 195L270 195L270 318L380 318',GREEN,3);arrow(f,365,318,385,318,GREEN);f.path('M590 359L900 359L900 482L800 482',GREEN,3);arrow(f,815,482,795,482,GREEN)
f.text(70,245,'原输入绕过子层',23,GREEN);f.text(915,400,'残差路径',23,GREEN);done(f)
f=new('tf-ffn','FFN：每个位置独立经过同一个非线性网络','自注意力沿位置聚合；FFN 在每个位置的特征通道内变换。')
for i in range(3):
 y=155+i*105;cell(f,50,y,f'$x_{i+1}$',w=135);arrow(f,193,y+28,300,y+28)
 f.rect(310,y,530,56,stroke=PURPLE);f.text(575,y+36,'线性扩展 → 非线性 → 线性投回',24,PURPLE,'middle');arrow(f,848,y+28,950,y+28);cell(f,960,y,f'$u_{i+1}$',w=170,c=GREEN)
f.text(600,510,'各行共享权重，但这一子层本身不在不同位置之间传递信息。',23,anchor='middle');done(f)

f=new('tf-encoder-decoder','04 · 经典 Transformer：两条序列，三种注意力','据 Vaswani 等，2017，Figure 1 的模块与数据流重绘；箭头自下而上。',990)
# tall, wide readable split architecture
for x,c,title in [(90,BLUE,'Encoder：源序列'),(680,PURPLE,'Decoder：目标前缀')]:
 f.rect(x,190,430,610,'#edf4f9',c);f.text(x+215,945,title,20,c,'middle')
f.box(95,835,420,85,'源 Token 嵌入 + 位置',[],BLUE);f.box(685,835,420,85,'右移目标嵌入 + 位置',[],PURPLE)
for y,lab in [(650,'多头自注意力'),(510,'Add & Norm'),(370,'逐位置 FFN'),(250,'Add & Norm')]:
 f.rect(140,y,330,65,stroke=BLUE);f.text(305,y+42,lab,24,BLUE,'middle')
for y,lab in [(700,'因果自注意力'),(605,'Add & Norm'),(510,'交叉注意力'),(415,'Add & Norm'),(320,'逐位置 FFN'),(240,'Add & Norm')]:
 f.rect(730,y,330,58,stroke=PURPLE);f.text(895,y+38,lab,24,PURPLE,'middle')
for y,yy in [(835,720),(650,580),(510,435),(370,320)]:arrow(f,305,y,305,yy)
for y,yy in [(835,765),(700,670),(605,570),(510,475),(415,380),(320,300)]:arrow(f,895,y,895,yy,PURPLE)
# residual loops with connecting arrowheads
for lower,upper in [(760,542),(480,282)]:
 f.path(f'M305 {lower}L115 {lower}L115 {upper}L135 {upper}',GREEN,3);arrow(f,135,upper,145,upper,GREEN)
for lower,upper in [(790,634),(590,444),(395,269)]:
 f.path(f'M895 {lower}L1085 {lower}L1085 {upper}L1065 {upper}',GREEN,3);arrow(f,1065,upper,1058,upper,GREEN)
f.path('M305 250L305 155L580 155L580 540L725 540',GREEN,3);arrow(f,710,540,726,540,GREEN)
f.text(580,440,'编码器输出',21,GREEN,'middle');f.text(580,474,'提供 $K,V$',23,GREEN,'middle')
f.box(730,112,330,75,'线性投影 → Softmax',[],ORANGE);arrow(f,895,240,895,190,ORANGE)
f.text(50,175,'重复堆叠编码层',20,BLUE);f.text(60,818,'绿色旁路：残差；每个子层均配残差与归一化。',19,GREEN)
done(f)
flow('tf-cross-attention','交叉注意力：目标提问，源表示提供证据',[('目标隐藏状态',[r'$H\in\mathbb{R}^{m\times d}$','$Q=HW_Q$','每个目标位置一个 Query']),('编码器记忆',[r'$M\in\mathbb{R}^{n\times d}$',r'$K=MW_K,\ V=MW_V$','源长度不要求等于目标长度']),('读取源信息',[r'$A\in\mathbb{R}^{m\times n}$',r'$Z=AV\in\mathbb{R}^{m\times d_v}$','输出位置数跟随 Query'])])
f=new('tf-shift-right','右移目标：当前位置的输入不是当前位置的答案','教学翻译目标为“我 爱 机器人 EOS”；起始符和终止符由模型配置决定。',470)
for i,t in enumerate(['BOS','我','爱','机器人']):cell(f,210+i*220,175,t,w=185)
for i,t in enumerate(['我','爱','机器人','EOS']):cell(f,210+i*220,310,t,w=185,c=GREEN);arrow(f,302+i*220,235,302+i*220,300)
f.text(35,210,'解码器输入',23,BLUE);f.text(35,347,'监督目标',23,GREEN);done(f)

f=new('tf-position-waves','05 · 正弦位置编码：不同通道提供不同频率','每个位置取得一整行频率特征，再与 Token 嵌入相加。')
for i,c in enumerate([BLUE,PURPLE,GREEN]):
 y=210+i*100;f.line(80,y,1100,y,'#c8d8e5');pts=[(80+j*3.4,y-35*math.sin(j/(10*2**i))) for j in range(300)]
 f.path('M'+'L'.join(f'{x:.1f},{yy:.1f}' for x,yy in pts),c,3);f.text(85,y-49,f'频率通道 {i+1}',22,c)
f.text(1080,520,'位置',22);done(f)
f=new('tf-rope','RoPE：旋转 Query 与 Key 的二维分量','仅画一个二维通道对；不同通道对通常使用不同角频率。',590)
cx,cy=330,325;r=160
f.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="white" stroke="#c8d8e5"/>')
f.line(105,cy,550,cy);f.line(cx,535,cx,115)
for a,c,lab in [(.25,BLUE,'原向量'),(1.15,PURPLE,'位置旋转后的向量')]:
 x=cx+r*math.cos(a);y=cy-r*math.sin(a);arrow(f,cx,cy,x,y,c);f.text(x+10,y-12,lab,22,c)
f.box(655,170,510,280,'保留相对位置关系',[r'$q_i^\prime=R(i\theta)q_i$',r'$k_j^\prime=R(j\theta)k_j$',r'$(q_i^\prime)^\mathsf{T}k_j^\prime$',r'$=q_i^\mathsf{T}R((j-i)\theta)k_j$'],GREEN);done(f)
f=new('tf-position-order','为什么纯双向自注意力需要顺序信息','无位置信号且无其他顺序线索时，交换输入行会交换输出行。',500)
for i,t in enumerate(['狗','咬','人']):cell(f,55+i*180,165,t,w=145)
for i,t in enumerate(['人','咬','狗']):cell(f,55+i*180,300,t,w=145,c=PURPLE)
f.box(680,155,470,230,'相同词集合，不同意思',['纯内容注意力具有置换等变性','位置编码打破这种对称','因果遮罩本身也带来顺序线索'],GREEN);done(f)

flow('tf-train-generate','06 · 训练能并行算损失，生成依赖已生成前缀',[('Teacher forcing',['输入真实目标的右移序列','因果遮罩阻止未来信息','所有有效位置一起算损失']),('反向传播',['对目标 Token 计算交叉熵','梯度更新模型参数','不是逐个 Token 调优化器']),('自回归生成',['只给提示与已有输出','每步选出下一个 Token','采样结果再作为下步输入'])])
f=new('tf-probabilities','从隐藏状态到词表概率，再决定输出 Token','下面概率为教学设定；贪心与采样是不同解码规则。')
for i,(t,p) in enumerate([('机器人',.55),('你',.25),('学习',.15),('EOS',.05)]):
 y=160+i*75;f.text(50,y+29,t,25,BLUE);f.rect(200,y,650*p,40,BLUE,BLUE);f.text(230+650*p,y+30,f'${p:.2f}$',23,PURPLE)
f.box(785,170,365,235,'选择规则',['贪心：取概率最大的项','采样：按分布抽取','温度作用于 logits','EOS / 长度限制可终止'],GREEN);done(f)
f=new('tf-causal-grid','因果遮罩：每一行是一个 Query 的可见范围','允许读取本位置及更早位置；右移输入避免把正确答案直接放在当前格。',600)
for i in range(5):
 for j in range(5):
  x=105+j*63;y=155+i*63;f.rect(x,y,60,60,'#dcecf6' if j<=i else '#ebe9ef',r=0)
  f.text(x+30,y+40,'$0$' if j<=i else r'$-\infty$',22,BLUE if j<=i else PURPLE,'middle')
f.box(560,185,590,245,'先加遮罩，再逐行 softmax',[r'$A=\mathrm{softmax}(QK^\mathsf{T}/\sqrt{d_k}+M)$','被屏蔽项的权重为零','padding 遮罩与因果遮罩解决不同问题','不能让一整行都只剩负无穷'],GREEN);done(f)

f=new('tf-kv-cache','07 · KV cache：每层保存过去的 Key 与 Value','只适用于因果结构且已缓存前缀不变等条件；图中仅展开一个头、一层。',600)
for i in range(4):
 cell(f,45+i*170,170,f'$k_{i+1},v_{i+1}$',w=150,c=GREEN if i<3 else ORANGE)
f.text(290,145,'已缓存前缀',23,GREEN,'middle');f.text(640,145,'本步追加',23,ORANGE,'middle')
f.box(820,155,330,140,'当前 Query',['$q_t$ 读取全部缓存'],PURPLE)
for i in range(4):arrow(f,120+i*170,230,940,325)
f.box(725,335,430,135,'当前步输出',['读取所有历史，不重算历史 K / V'],BLUE)
f.text(45,430,'参数：学到的权重，不随解码步数增长',23,BLUE);f.text(45,477,'缓存：本次请求的中间值，长度随上下文增长',23,GREEN);done(f)
f=new('tf-cache-memory','KV cache 的容量：长上下文与并发都会放大它','以下仅为理论张量大小，不含模型参数、临时工作区与内存碎片。',510)
f.text(600,175,r'$\mathrm{bytes}=2bn\ell h_{kv}d_hs$',34,BLUE,'middle')
f.box(35,225,540,190,'各符号的含义',[r'$b$：batch；$n$：缓存长度；$\ell$：层数','$h_{kv}$：KV 头数；$d_h$：每头宽度','$s$：每个元素的字节数；系数 2 表示 K 与 V'],PURPLE)
f.box(625,225,540,190,'示例：仅一个请求',[r'$n=4096,\ \ell=32,\ h_{kv}=8$',r'$d_h=128,\ s=2$，$b=1$','合计 512 MiB；换成 32 个 KV 头为 2 GiB'],GREEN);done(f)
f=new('tf-flash-tiles','FlashAttention：改变计算与存取方式','精确注意力的分块计算；不是把每行注意力随意截断。',540)
for i in range(4):
 for j in range(4):f.rect(65+j*66,155+i*66,62,62,'#dcecf6' if (i+j)%2 else '#c0daeb',BLUE,0)
f.text(190,460,'分块处理分数',23,BLUE,'middle')
f.box(490,155,660,270,'边读块，边更新稳定 softmax',['每行维护当前最大值、指数和与加权输出','新最大值出现时，旧累加器重新缩放','不必把完整注意力矩阵写回显存','普通 dense 情况算术量仍随长度平方增长'],GREEN);done(f)

f=new('tf-family-masks','08 · 三种结构：先看谁能读取谁','蓝色表示允许的信息流；这是结构规则示意，不是注意力强度。',550)
for k,(title,col) in enumerate([('BERT：双向编码',BLUE),('GPT：因果解码',PURPLE),('Seq2Seq：交叉读取',GREEN)]):
 x=45+k*395;f.text(x,150,title,23,col)
 for i in range(4):
  for j in range(4):f.rect(x+j*68,185+i*68,64,64,'#dcecf6' if k!=1 or j<=i else '#e9e9ef',col if k!=1 or j<=i else '#d5d9df',0)
 f.text(x,495,['行和列均为文本位置','行和列均为目标位置','行是目标，列是源位置'][k],21,col)
done(f)
f=new('tf-vit-patches','ViT：把图片切成 Patch，再送入编码器','示意四乘四图像块；实际 Patch 大小由模型配置决定。',600)
for i in range(4):
 for j in range(4):
  x=45+j*67;y=160+i*67;f.rect(x,y,63,63,['#dcecf6','#e9e1f5','#dcefe8','#f6e7dc'][(i+j)%4],r=0);f.text(x+31,y+40,str(i*4+j+1),22,BLUE,'middle')
arrow(f,345,290,450,290)
f.box(465,160,300,250,'块向量与位置',['每块展平 → 线性投影','加入位置嵌入','可加入分类 Token','不需要先做词表查找'],PURPLE);arrow(f,775,290,830,290)
f.box(845,160,320,250,'Transformer Encoder',['块之间双向读取','FFN 与残差处理','分类头输出类别','其他任务可读空间表示'],GREEN);done(f)
flow('tf-modal-tokens','同一骨架能处理不同模态，但表示与目标不同',[('文本',['离散 Token → 嵌入','GPT：预测下个 Token','BERT：预测遮盖位置']),('图像',['Patch → 线性投影','ViT：分类或视觉表示','Patch 不是离散单词']),('机器人动作',['状态、图像与动作表示','可做回归、扩散或 flow','不能看到 Transformer 就认定是 GPT'])])

# Animation keyframes are vector diagrams too; no bitmap-generated equations.
def animation(name,kind):
 frames=[]
 steps={'attention':4,'mask':5,'generate':5,'rope':12,'cache':5,'patch':5}[kind]
 for step in range(steps):
  f=Fig(name,{'attention':'动画 · 一次移动一个 Query，读取不同上下文','mask':'动画 · 因果遮罩逐行开放历史','generate':'动画 · 下一个 Token 成为下一步的输入','rope':'动画 · 位置变化使 Query / Key 发生旋转','cache':'动画 · 历史缓存保持不变，本步只追加新项','patch':'动画 · 图像块依次变成序列位置'}[kind],'可暂停、拖动进度条与重播；所有步骤均为教学示意。',570)
  if kind=='attention':
   words=['我','爱','机器','人'];weights=[[.4,.1,.2,.3],[.1,.2,.5,.2],[.05,.15,.6,.2],[.1,.1,.3,.5]][step]
   for j,t in enumerate(words):
    cell(f,60+j*270,155,t,w=235,c=PURPLE if j==step else BLUE)
    f.rect(60+j*270,270,235,160,fill='#e4eef6',stroke=BLUE);f.rect(70+j*270,420-weights[j]*220,215,weights[j]*220,BLUE,BLUE)
    f.text(177+j*270,465,f'$a_{{{step+1},{j+1}}}={weights[j]:g}$',24,PURPLE,'middle')
   f.text(600,525,f'当前 Query：位置 {step+1}；每次 softmax 沿 Key 轴归一化。',23,anchor='middle')
  elif kind=='mask':
   for i in range(5):
    for j in range(5):
     allowed=i==step and j<=i;f.rect(90+j*62,160+i*62,58,58,'#aed8e8' if allowed else '#e9edf2',BLUE if allowed else '#ccd7e2',0)
     if i==step:f.text(119+j*62,199+i*62,'$0$' if j<=i else r'$-\infty$',22,BLUE,'middle')
   f.box(560,180,590,230,f'正在计算第 {step+1} 行',[f'只允许读取前 {step+1} 个位置','遮住未来的分数 → 权重为零','所有行在训练时仍可并行计算'],PURPLE)
  elif kind=='generate':
   tokens=['BOS','我','爱','机器人','EOS']
   for j,t in enumerate(tokens):cell(f,40+j*230,185,t,j<=step,w=205,c=GREEN)
   f.box(175,320,850,150,'前缀 → 模型 → 下一 Token',[f'当前已经给出 {step+1} 个 Token；下一步继续或在 EOS 停止','模型参数保持不变；改变的是前缀与本次计算状态。'],BLUE)
  elif kind=='rope':
   cx,cy=350,330;a=step*math.pi/9
   f.parts.append('<circle cx="350" cy="330" r="160" fill="white" stroke="#c8d8e5"/>');f.line(140,330,560,330);f.line(350,520,350,120)
   arrow(f,cx,cy,cx+150*math.cos(a),cy-150*math.sin(a),PURPLE)
   f.box(660,180,500,255,'旋转的是特征通道对',[f'位置示意：${step}$',r'$q_i^\prime=R(i\theta)q_i$','旋转不改变该向量的模长','原理不是让 Token 在句子里转圈'],GREEN)
  elif kind=='cache':
   for j in range(5):cell(f,35+j*230,175,f'$K_{{{j+1}}},V_{{{j+1}}}$',j<=step,w=210,c=ORANGE if j==step else GREEN)
   f.box(220,325,760,150,f'步骤 {step+1}：追加当前层的新 Key / Value',[f'新 Query 可读取 {step+1} 组 Key / Value','每层各有自己的缓存；已缓存内容在此前缀不变时保留。'],BLUE)
  elif kind=='patch':
   for j in range(4):
    f.rect(60+(j%2)*130,170+(j//2)*130,120,120,['#dcecf6','#e9e1f5','#dcefe8','#f6e7dc'][j],BLUE if j==min(step,3) else '#c8d8e5');f.text(120+(j%2)*130,245+(j//2)*130,str(j+1),28,BLUE,'middle')
    cell(f,460+j*175,240,f'块 {j+1}',j<step,w=150,c=PURPLE)
   f.text(800,395,'块顺序需与位置编码一致',24,GREEN,'middle')
  f.footer('原创可视化；慢速逐步显示便于学习，不代表真实硬件的执行时序。')
  frames.append(''.join(f.parts)+'</svg>')
 ANIMS[name]=frames
for name,kind in [('tf-attention-animated','attention'),('tf-mask-animated','mask'),('tf-generation-animated','generate'),('tf-rope-animated','rope'),('tf-cache-animated','cache'),('tf-patch-animated','patch')]:animation(name,kind)

if __name__=='__main__':
 from playwright.sync_api import sync_playwright
 import re
 with tempfile.TemporaryDirectory(prefix='cxwiki-transformer-') as work, sync_playwright() as p:
  browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1200,'height':1000},device_scale_factor=1.5)
  for name in NAMES:
   svg=OUT/(name+'.svg');h=int(re.search(r'height="(\d+)"',svg.read_text())[1]);page.set_viewport_size({'width':1200,'height':h});page.goto(svg.resolve().as_uri());page.screenshot(path=str(svg.with_suffix('.png')))
  page.set_viewport_size({'width':1200,'height':570})
  for name,frames in ANIMS.items():
   folder=Path(work)/name;folder.mkdir()
   for i,svg in enumerate(frames):
    source=folder/f'{i:03}.svg';source.write_text(svg);page.goto(source.resolve().as_uri());page.screenshot(path=str(source.with_suffix('.png')))
   # 1.25s per readable stage, 24fps MP4, portable YUV420p H.264.
   subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','0.8','-i',str(folder/'%03d.png'),'-vf','fps=24,scale=1200:570','-c:v','libx264','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(OUT/(name+'.mp4'))],check=True)
   # Source of all animation stages retained as editable SVGs in one script;
   # first frame is a normal SVG + PNG for fallback and structural checking.
   (OUT/(name+'.svg')).write_text(frames[0]);page.goto((OUT/(name+'.svg')).resolve().as_uri());page.screenshot(path=str(OUT/(name+'.png')))
  browser.close()
 print(f'Rendered {len(NAMES)} diagrams and {len(ANIMS)} animations.')
