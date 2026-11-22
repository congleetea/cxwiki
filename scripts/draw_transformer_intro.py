"""Beginner-level Transformer whole-network maps; math is rendered as paths."""
from draw_foundations import Fig, BLUE, PURPLE, GREEN, ORANGE, OUT
from playwright.sync_api import sync_playwright

def arrow(f,x,y,xx,yy,c=BLUE):f.line(x,y,xx,yy,c,True,width=3)

f=Fig('tf-overview-translation','先看整件事：读懂源句，再根据前缀生成目标句','教学例子：把“机器人拿杯子”翻译为英文；每个模块承担不同职责。',710)
for x,title,lines,c in [
 (30,'① 输入表示',['源句：机器人拿杯子','分词 → 嵌入 + 位置信息'],BLUE),
 (435,'② Encoder',['源位置之间交流信息','输出一组上下文表示'],BLUE),
 (840,'③ 源记忆',['保留各源位置的表示','供目标侧反复读取'],GREEN)]:
 f.box(x,150,330,160,title,lines,c)
arrow(f,365,230,425,230);arrow(f,770,230,830,230)
for x,title,lines,c in [
 (30,'④ 目标前缀',['起始符 + 已知目标内容','嵌入 + 位置信息'],PURPLE),
 (435,'⑤ Decoder',['因果自注意力：读前缀','交叉注意力：读源记忆'],PURPLE),
 (840,'⑥ 输出与选择',['词表分布 → 选一个 Token','本例可依次生成英文句子'],ORANGE)]:
 f.box(x,435,330,160,title,lines,c)
arrow(f,365,515,425,515,PURPLE);arrow(f,770,515,830,515,PURPLE)
f.path('M1005 310L1005 370L600 370L600 430',GREEN,3);arrow(f,600,415,600,432,GREEN)
f.text(570,352,'源记忆为每个目标位置提供条件',22,GREEN)
f.path('M1005 595L1005 637L195 637L195 600',ORANGE,3);arrow(f,195,615,195,599,ORANGE)
f.text(600,628,'生成时把选出的 Token 追加到前缀，继续下一步',22,ORANGE,'middle')
f.footer('原创教学数据流；编码器源记忆只需建立一次，解码器每次生成都可继续读取它。');f.save()

f=Fig('tf-overview-block-roles','再看一层：信息交流、特征加工与稳定通路','展开编码器式 Post-LN Block；经典解码层还会在两者之间加入交叉注意力。',690)
for y,title,lines,c in [
 (150,'① Self-Attention：位置之间交流',['每个位置根据相关性，读取其他允许位置的内容'],BLUE),
 (265,'② Add & Norm：相加并归一化',['合入子层前的输入，再调整每个位置的特征尺度'],GREEN),
 (380,'③ FFN：每个位置加工自己的特征',['同一组非线性网络作用于各位置；本子层不跨位置读取'],PURPLE),
 (495,'④ Add & Norm：再次保留旁路',['合入 FFN 前的表示，形成这一层的输出'],GREEN)]:
 f.box(235,y,760,93,title,lines,c)
 if y<495:arrow(f,615,y+96,615,y+112)
arrow(f,615,110,615,147)
f.path('M615 128L155 128L155 310L230 310',GREEN,3);arrow(f,215,310,232,310,GREEN)
f.path('M615 368L1070 368L1070 540L1000 540',GREEN,3);arrow(f,1015,540,998,540,GREEN)
arrow(f,615,590,615,625)
f.text(90,220,'残差旁路',22,GREEN);f.text(1050,450,'残差',22,GREEN)
f.footer('原创职责图；图中为经典 Post-LN 顺序。Pre-LN 的归一化放在子层前，细节见系列第三篇。');f.save()

if __name__=='__main__':
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  for name,height in [('tf-overview-translation',710),('tf-overview-block-roles',690)]:
   page=browser.new_page(viewport={'width':1200,'height':height},device_scale_factor=2)
   page.goto((OUT/(name+'.svg')).resolve().as_uri());page.screenshot(path=str(OUT/(name+'.png')));page.close()
  browser.close()
