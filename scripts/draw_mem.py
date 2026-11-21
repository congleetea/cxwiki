"""MEM explanatory figures; equations rendered as LaTeX vector paths."""
from draw_foundations import Fig, BLUE, PURPLE, GREEN, ORANGE, OUT
NAMES=[]
def new(n,t,s,h=620):
 NAMES.append(n);return Fig(n,t,s,h)
def arrow(f,x,y,xx,yy):f.line(x,y,xx,yy,arrow=True,width=3)
f=new('pi-mem-architecture','MEM：长期记住做过什么，短期看清刚才发生什么','核心两种记忆：语言摘要与近期观测；本体历史是近期观测的一部分。',660)
f.box(30,140,350,185,'高层：更新语义进度',['目标 $g$、当前观测 $o_t$','读取旧摘要 $m_t$','输出子任务与新摘要'],PURPLE)
f.box(30,405,350,160,'递归语言记忆',['$m_t\\to m_{t+1}$','保留未来还需要的事实'],PURPLE)
arrow(f,205,330,205,395)
f.box(440,140,340,185,'近期观测历史',['多相机图像序列','时间对齐的机器人状态','只保留有界历史窗口'],GREEN)
f.box(440,405,340,160,'压缩与嵌入',['视频 → 当前时刻视觉特征','状态 → 连续状态 token'],GREEN)
arrow(f,610,330,610,395)
f.box(840,140,330,185,'低层：连续动作控制',['接收高层子任务','读取压缩后的近期观测','输出动作块'],BLUE)
f.box(840,405,330,160,'执行与新观测',['执行动作、获得反馈','更新历史，再次决策'],BLUE)
arrow(f,1005,330,1005,395)
f.text(600,110,'子任务指令',18,PURPLE,'middle')
# Clarify the high-level-to-low-level link without crossing the centre box.
f.path('M205 132 L205 120 L1005 120',PURPLE,2);arrow(f,1005,120,1005,135)
f.path('M785 485 L810 485 L810 225',GREEN,3);arrow(f,810,225,835,225)
f.path('M30 485 L15 485 L15 225',PURPLE,2);arrow(f,15,225,28,225)
f.footer('原创结构示意，依据论文 §III；方框区分信息职责，不代表独立新网络或固定执行频率。');f.save()

f=new('pi-mem-video','视频记忆：空间内看关系，时间上看变化，再压缩输出','按一个相机流展示；同一空间 patch 跨时间的注意力不等于跟踪同一物体。',650)
for i in range(3):
 x=50+i*160;f.rect(x,145,135,110,stroke=GREEN)
 f.text(x+68,182,f'$I_{{t-{2-i}}}$' if i<2 else '$I_t$',25,GREEN,'middle')
 for j in range(3):f.rect(x+15+j*35,205,25,25,fill='#dceee5',r=0)
f.box(590,140,570,160,'① 每帧空间注意力',['每个时刻的所有 patch 交换信息','空间索引变化，时间索引固定'],BLUE)
f.box(590,335,570,160,'② 每隔四层加入因果时间注意力',['同一 patch 位置访问当前与过去时刻','随后继续空间融合；投影权重复用'],PURPLE)
arrow(f,520,205,575,205);arrow(f,875,305,875,325)
f.box(40,335,480,160,'③ 只输出当前时刻的视觉表示',['历史特征已融合进当前特征','主干不再接收全部历史视觉 token'],GREEN)
arrow(f,580,420,530,420)
f.text(600,555,'$\\mathcal{O}(F^2N^2)\\quad\\to\\quad\\mathcal{O}(FN^2+NF^2)$',30,BLUE,'middle')
f.footer('原创简化图；复杂度只比较注意力交互，忽略通道维、层数与缓存，不表示总耗时不随历史增长。');f.save()

f=new('pi-mem-language','语言记忆：更新事实摘要，而不是不断追加操作日志','教学任务：清洗盘子；文字为原创例子，不是论文训练样本。',620)
f.box(30,140,345,240,'旧记忆 + 当前证据',['旧记忆：盘子正面已洗净','当前观测：正在清洗背面','目标：洗净后放入沥水架'],PURPLE)
f.box(430,140,345,240,'高层作出更新',['成功完成背面清洗？','若完成：压缩为两面已洗净','若证据不足：不能臆记完成'],GREEN)
f.box(830,140,340,240,'新子任务 + 新记忆',['子任务：把盘子放入沥水架','记忆：盘子两面已洗净','下一次高层再读取这份摘要'],BLUE)
arrow(f,380,260,420,260);arrow(f,780,260,820,260)
f.text(600,445,'训练标签：子任务序列 + 成败标记 → 离线 LLM 总结 → 监督高层预测',24,anchor='middle')
f.text(600,500,'$m_{j+1},\\ell_{j+1}\\sim\\pi_{\\mathrm{HL}}(\\cdot\\mid o_{t_j},m_j,g)$',29,PURPLE,'middle')
f.footer('原创教学流程；失败尝试可不写入，保留什么取决于未来需要，语言记忆也可能遗漏或出错。');f.save()

f=new('pi-mem-state','本体历史：一个时刻的整组状态，投影成一个连续 token','关节角等状态必须先按机器人定义组织、归一化，并与图像时间对齐。',540)
f.box(35,145,330,230,'输入：历史状态矩阵',['$Q\\in\\mathbb{R}^{F\\times d_s}$','每行：一个时刻的状态','每列：一个状态分量'],GREEN)
f.box(435,145,330,230,'共享线性投影',['$e_i=W_s s_i+b_s$','$W_s\\in\\mathbb{R}^{d_m\\times d_s}$','$e_i\\in\\mathbb{R}^{d_m}$'],PURPLE)
f.box(835,145,330,230,'输出：状态 token 序列',['$E\\in\\mathbb{R}^{F\\times d_m}$','共 $F$ 个连续 token','不是把每个数写成文本'],BLUE)
arrow(f,370,260,425,260);arrow(f,770,260,825,260)
f.text(600,445,'$F=6\\quad\\Rightarrow\\quad6\\ \\mathrm{state\\ tokens}$',28,BLUE,'middle')
f.footer('原创维度解释；线性式为对论文 §III-D 的统一记号，不指定官方未披露的状态维数或归一化配方。');f.save()
if __name__=='__main__':
 from playwright.sync_api import sync_playwright
 import re
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True)
  for n in NAMES:
   path=OUT/(n+'.svg');h=int(re.search(r'height="(\d+)"',path.read_text())[1])
   page=b.new_page(viewport={'width':1200,'height':h},device_scale_factor=2)
   page.goto(path.resolve().as_uri());page.screenshot(path=str(path.with_suffix('.png')));page.close()
  b.close()
