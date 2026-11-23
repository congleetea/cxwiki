"""Original VAE/CVAE diagrams. All mathematical labels use LaTeX paths."""
from draw_foundations import Fig, BLUE, PURPLE, GREEN, ORANGE, OUT
NAMES=[]
def new(n,t,s,h=560):
 NAMES.append(n);return Fig(n,t,s,h)
def arrow(f,x,y,x2,y2):f.line(x,y,x2,y2,arrow=True,width=3)
f=new('vae-training-generation','01  VAE：训练时重建，生成时从先验出发','编码器输出潜变量分布的参数；解码器输出数据分布的参数。',620)
for x,t,ls,c in [(30,'数据',['训练样本 $x$'],BLUE),(330,'编码器',['$q_\\phi(z\\mid x)$','$\\mu,\\ \\log\\sigma^2$'],PURPLE),(630,'采样',['$z=\\mu+\\sigma\\odot\\epsilon$','$\\epsilon\\sim\\mathcal{N}(0,I)$'],GREEN),(930,'解码器',['$p_\\theta(x\\mid z)$','重建分布'],BLUE)]:
 f.box(x,140,240,175,t,ls,c)
for x in (280,580,880):arrow(f,x,225,x+40,225)
f.text(600,365,'训练：重建负对数似然 + 近似后验与先验之间的 KL',24,anchor='middle')
f.box(70,405,310,135,'生成：不需要原始图片',['$z\\sim p(z)=\\mathcal{N}(0,I)$'],GREEN)
f.box(470,405,300,135,'训练好的解码器',['$p_\\theta(x\\mid z)$'],BLUE)
f.box(860,405,270,135,'输出新样本',['采样或取分布均值'],PURPLE)
arrow(f,390,470,460,470);arrow(f,780,470,850,470)
f.footer('原创流程；训练从近似后验采样，独立生成从先验采样，不能混为同一条路径。');f.save()

f=new('vae-reparameterization','02  重参数化：把随机性放在独立噪声里','采样分布不变；固定一次噪声后，参数到样本的计算是可微的。',520)
f.box(35,145,330,220,'网络输出',['$\\mu_\\phi(x)$','$\\ell_\\phi(x)=\\log\\sigma^2$','$\\sigma=\\exp(\\ell/2)$'],PURPLE)
f.box(435,145,330,220,'可微组合',['$\\epsilon\\sim\\mathcal{N}(0,I)$','$z=\\mu+\\sigma\\odot\\epsilon$','噪声分布不依赖参数'],GREEN)
f.box(835,145,330,220,'解码与损失',['解码器读取 $z$','重建损失反向传播','同时更新编码器与解码器'],BLUE)
arrow(f,370,255,425,255);arrow(f,770,255,825,255)
f.text(600,430,'$\\partial z/\\partial\\mu=I,\\qquad \\partial z_j/\\partial\\sigma_j=\\epsilon_j$',29,PURPLE,'middle')
f.footer('原创解释；对离散潜变量不能直接套用这个高斯重参数化公式。');f.save()

f=new('cvae-condition','03  CVAE：条件指定任务，潜变量表达剩余差异','统一符号：条件 c，待生成输出 x，潜变量 z。',620)
f.box(30,140,340,175,'训练：看到条件与答案',['$q_\\phi(z\\mid x,c)$','由真实输出辅助推断 $z$'],PURPLE)
f.box(430,140,340,175,'潜变量',['后验采样用于重建','KL 对齐条件先验'],GREEN)
f.box(830,140,340,175,'条件解码器',['$p_\\theta(x\\mid z,c)$','重建真实输出'],BLUE)
arrow(f,375,225,420,225);arrow(f,775,225,820,225)
f.box(30,390,340,150,'生成：只有条件',['$c$ 已知，真实 $x$ 未知'],PURPLE)
f.box(430,390,340,150,'从先验采样',['$z\\sim p_\\psi(z\\mid c)$'],GREEN)
f.box(830,390,340,150,'生成输出',['$x\\sim p_\\theta(x\\mid z,c)$'],BLUE)
arrow(f,375,465,420,465);arrow(f,775,465,820,465)
f.text(600,360,'条件 c 在两种模式下都输入解码器；它不是训练时才有的答案。',23,anchor='middle')
f.footer('原创简化流程；固定标准正态先验是特例，训练时看答案的后验网络不在生成时使用。');f.save()

f=new('cvae-multimodal-actions','04  为什么引入潜变量：同一条件下可能有多种合理动作','示意任务：绕开障碍到达目标；路径仅讲解多模态，不代表真实规划器输出。',580)
f.rect(40,130,560,340)
f.rect(270,240,100,100,fill='#e3e9ef');f.text(320,295,'障碍',23,anchor='middle')
f.text(80,310,'起点',23);f.text(515,310,'目标',23)
f.path('M140 290 L220 180 L430 180 L505 290',BLUE,4)
f.path('M140 290 L220 400 L430 400 L505 290',GREEN,4)
f.line(145,290,500,290,ORANGE,False,True,3)
f.text(280,165,'上侧模式',22,BLUE);f.text(280,435,'下侧模式',22,GREEN)
f.box(650,135,510,335,'相同条件，不止一个正确答案',[
 '条件：场景、起点与目标',
 '输出：一段动作或轨迹',
 '潜变量：区分不同执行模式',
 '橙色：两条对称路径的逐点均值',
 '均值可能穿过障碍，未必可执行',
 'CVAE 能建模多解，但不保证安全'],PURPLE)
f.footer('原创直觉示例；潜变量不会自动对应可解释技能，需用生成结果验证模型是否真的利用了 z。');f.save()

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
