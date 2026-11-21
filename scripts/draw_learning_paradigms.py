"""Original diagrams for data collection and policy roles."""
from draw_foundations import Fig, BLUE, PURPLE, GREEN, OUT
f=Fig('learning-online-offline','在线与离线：训练期间是否继续采集环境经验','两条流程都输出策略；区别在训练数据能否随交互扩充。',560)
f.box(30,135,330,150,'在线：运行环境',['执行当前采集策略','得到新转移'],GREEN)
f.box(435,135,330,150,'追加数据',['新经验进入缓冲区','也可按轨迹批次组织'],PURPLE)
f.box(840,135,330,150,'训练策略',['更新价值或策略','随后继续采集'],BLUE)
f.line(365,210,425,210,arrow=True);f.line(770,210,830,210,arrow=True)
f.path('M1005 290 L1005 315 L195 315 L195 290',GREEN,3)
f.box(30,350,330,145,'离线：已有日志',['训练期固定数据集'],PURPLE)
f.box(435,350,330,145,'反复抽样训练',['不追加环境转移'],BLUE)
f.box(840,350,330,145,'得到策略',['之后可独立部署评估'],GREEN)
f.line(365,420,425,420,arrow=True);f.line(770,420,830,420,arrow=True)
f.footer('原创教学流程；在线不等于必须逐样本更新，离线不等于没有网络连接。');f.save()
f=Fig('learning-policy-roles','On-policy 与 Off-policy：谁采集，学谁','同一机器人也能产生 off-policy 数据；关键是策略及其分布的对应。',560)
f.box(35,140,330,260,'01  行为策略采集',['$a_t \\sim b(\\cdot\\mid s_t)$','环境生成转移','保存状态、动作、奖励'],BLUE)
f.box(435,140,330,260,'02  数据与更新',['on-policy：分布对应','off-policy：允许不同','必须处理覆盖与估计问题'],GREEN)
f.box(835,140,330,260,'03  目标策略',['评估或改进 $\\pi$','不一定直接模仿 $b$','并非任意数据都可用'],PURPLE)
f.line(370,265,425,265,arrow=True);f.line(770,265,825,265,arrow=True)
f.text(600,465,'一步重要性比率：$\\rho(a\\mid s)=\\pi(a\\mid s)/b(a\\mid s)$',28,BLUE,'middle')
f.footer('原创教学示意；概率比要求目标策略支持集被行为策略覆盖，多步估计还涉及轨迹分布。');f.save()
if __name__=='__main__':
 from playwright.sync_api import sync_playwright
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True)
  for name in ['learning-online-offline','learning-policy-roles']:
   page=b.new_page(viewport={'width':1200,'height':560},device_scale_factor=2)
   page.goto((OUT/(name+'.svg')).resolve().as_uri());page.screenshot(path=str(OUT/(name+'.png')));page.close()
  b.close()
