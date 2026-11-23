"""Chronology and problem axes for the robot-value/reward overview."""
from draw_foundations import Fig, BLUE, PURPLE, GREEN, ORANGE, OUT
f=Fig('robot-values-timeline','机器人价值与奖励：按首次公开时间看问题怎样变化','时间表示公开顺序，不表示后一工作完全替代前一工作。',940)
rows=[('2022-04','SayCan','技能可行性：语言说得通，还要机器人做得到',BLUE),('2024-11','GVL','冻结 VLM：由视频内容生成任务进度',PURPLE),('2025-09','SARM','语义阶段：对齐快慢不同的长程示范',GREEN),('2025-12','Robo-Dopamine','相对 hop：从进度到折扣一致的奖励塑造',ORANGE),('2026-02','TOPReward','概率读出：绕过直接生成数字的瓶颈',PURPLE),('2026-03','Robometer','轨迹比较：让失败和次优数据也参与监督',GREEN),('2026-04','ARM','三态相对变化：保留退步、恢复与完成锚点',ORANGE),('2026-06','SARM2','共享动作基元：多任务评分接入改进循环',BLUE)]
f.line(230,155,230,830,width=3)
for i,(date,name,desc,c) in enumerate(rows):
 y=155+i*86;f.text(35,y+35,date,23,c);f.parts.append(f'<circle cx="230" cy="{y+26}" r="8" fill="{c}"/>')
 f.rect(265,y,895,70,stroke=c);f.text(285,y+29,name,23,c,bold=True);f.text(285,y+57,desc,20)
f.footer('原创时间线；日期依据 arXiv 首次提交记录，方法内容依据各概念文注明的版本核验。');f.save()
f=Fig('robot-values-problem-map','别只问哪个模型更强：先问需要它输出什么','模型名字中的 value / reward 不能替代输入输出与监督定义。',620)
for x,y,t,ls,c in [(30,140,'技能选择',['当前技能能否成功？','SayCan'],BLUE),(625,140,'无任务专门训练的读出',['能否用现有 VLM 给视频打分？','GVL / TOPReward'],PURPLE),(30,350,'监督式进度与失败识别',['阶段、比较、相对变化如何标注？','SARM / Robometer / ARM'],GREEN),(625,350,'把评分接到策略改进',['怎样塑造奖励、处理新分布？','Robo-Dopamine / SARM2 + SPIRAL'],ORANGE)]:f.box(x,y,545,175,t,ls,c)
f.footer('原创职责对照；同一方法可覆盖多个方向，方框用于建立阅读入口，不作为互斥分类或性能排序。');f.save()
if __name__=='__main__':
 from playwright.sync_api import sync_playwright
 import re
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True)
  for n in ['robot-values-timeline','robot-values-problem-map']:
   path=OUT/(n+'.svg');h=int(re.search(r'height="(\d+)"',path.read_text())[1]);page=b.new_page(viewport={'width':1200,'height':h},device_scale_factor=2)
   page.goto(path.resolve().as_uri());page.screenshot(path=str(path.with_suffix('.png')));page.close()
  b.close()
