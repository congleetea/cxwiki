"""Original value/reward teaching diagrams; mathematical labels are LaTeX paths."""
from draw_foundations import Fig, BLUE, PURPLE, GREEN, ORANGE, OUT
NAMES=[]
def new(n,t,s,h=560):NAMES.append(n);return Fig(n,t,s,h)
def arr(f,x,y,xx,yy,c=BLUE):f.line(x,y,xx,yy,c,True,width=3)
def pipeline(name,title,nodes,sub):
 f=new(name,title,sub,520)
 for x,(t,ls),c in zip([30,435,840],nodes,[BLUE,PURPLE,GREEN]):f.box(x,145,330,245,t,ls,c)
 for x in [370,775]:arr(f,x,267,x+55,267)
 f.footer('原创机制示意，依据对应原论文重绘；省略网络层数等细节，非论文实验结果。');f.save()
def curve(name,title,ys,labels,sub):
 f=new(name,title,sub,530);arr(f,90,390,1110,390);arr(f,90,390,90,130)
 for values,label,c in zip(ys,labels,[BLUE,ORANGE,GREEN]):
  coords=[(110+i*920/(len(values)-1),390-v*220) for i,v in enumerate(values)]
  f.path('M'+' L'.join(f'{x:.1f} {y:.1f}' for x,y in coords),c,4)
  for (x,y),v in zip(coords,values):f.text(x,y-12,f'${v:g}$',20,c,'middle')
  f.text(850,445+labels.index(label)*28,label,20,c)
 f.text(60,130,'分数',22);f.text(1020,420,'输入位置' if name=='gvl-order-bias' else '时间',22)
 f.footer('原创教学曲线；所有数值为示意，不是模型实测或论文报告的性能。');f.save()

f=new('robot-value-quantities','奖励、进度、价值与优势：别把四个分数混成一个','同一个观测可以对应不同策略价值；进度也不是成功概率。',620)
for x,y,t,ls,c in [(30,135,'即时奖励',['$r_t$','这一步得到什么反馈'],BLUE),(625,135,'进度',['$P(o_t,g)$','已经完成了多少'],GREEN),(30,345,'价值',['$V^\\pi(s),\\ Q^\\pi(s,a)$','随后按指定策略行动的期望回报'],PURPLE),(625,345,'优势',['$A^\\pi(s,a)=Q^\\pi(s,a)-V^\\pi(s)$','当前动作比策略平均表现好多少'],ORANGE)]:f.box(x,y,545,175,t,ls,c)
f.footer('原创概念图；奖励模型若输出进度，需要另外说明如何把它转成逐步奖励或训练权重。');f.save()
pipeline('robot-value-use','价值分数怎样参与机器人决策',[('观测与目标',['相机、本体状态、语言','不一定可见完整真实状态']),('评估器',['预测价值、进度或成功','必须明确分数定义']),('决策或训练',['选择技能、筛选轨迹','重加权示范或构造 RL 奖励'])],'评估器负责打分，策略负责产生动作；有高分不等于已经完成动作。')

pipeline('gvl-method','GVL：保留起点，打乱其余帧，再恢复时间顺序',[('取帧与重排',['任务指令 + 视频帧','首帧作时间锚点','其余帧随机置换']),('冻结的 VLM',['按输入帧逐个生成进度','可加已标注示例','不更新模型权重']),('逆置换与应用',['分数对应回原始帧','形成进度曲线','筛选数据或学习权重'])],'依据 GVL §3：不是把首帧也无条件打乱；原论文实验统一采样三十帧。')
curve('gvl-order-bias','按输入位置递增，不等于真的识别进度',[[0,.8,.3,1],[0,.3,.7,1]],['内容对应的进度','只按输入位置猜数'],'原时间顺序为起点、抓起、移动、放好；打乱后输入为起点、移动、抓起、放好。')

pipeline('saycan-method','SayCan：语言判断有用，价值判断能做，再执行技能',[('任务与技能库',['高层要求 + 已执行步骤','枚举已有技能文字描述']),('双路评分',['Say：语言相关性','Can：当前状态下技能可行性','乘积排序']),('执行并重新观察',['调用已有低层技能','更新实际场景','重新评分，直到结束'])],'依据 SayCan 图 1 与算法 1 的数据流重绘；不是直接让语言模型输出关节动作。')
f=new('saycan-scores','SayCan：最符合语言的技能，也可能现在做不了','原创例子：清理洒出的水；分数为教学设定，不是校准后的真实概率。')
for y,label,l,v in [(160,'拿毛巾（当前够不到）',.9,.01),(260,'拿纸巾',.7,.8),(360,'拿杯子',.2,.9)]:
 f.text(35,y+25,label,22);f.rect(360,y,300*l,22,fill=BLUE,stroke=BLUE,r=0);f.rect(360,y+30,300*v,22,fill=GREEN,stroke=GREEN,r=0)
 f.text(710,y+38,f'${l}\\times {v}={l*v:.3f}$',27,PURPLE)
f.text(360,130,'蓝：语言分数；绿：可行性',22);f.text(710,440,'选择乘积最大的“拿纸巾”',24,PURPLE)
f.footer('原创评分对照；只在给定候选库内选技能，乘积不会自动产生新的机器人能力。');f.save()

pipeline('topreward-method','TOPReward：不让模型报百分比，读取肯定答案的概率',[('只取当前视频前缀',['视频从起点到当前时刻','任务文字 + 完成判断语境']),('计算候选答案概率',['读取 True 答案的对数概率','不依赖生成数字是否准确']),('形成曲线与权重',['轨迹内归一化','观察分数增量','用于检测和 BC 加权'])],'依据 TOPReward §3；完整轨迹归一化是离线步骤，不自动成为无未来信息的在线校准。')
curve('topreward-normalization','归一化到满分，不代表失败轨迹真的成功',[[0,.5,1]],['归一化后的轨迹内分数'],'原始对数分数为 −10、−9、−8；虽然末尾仍低，也会映射到轨迹内最高分。')

pipeline('robometer-method','Robometer：轨迹内看进度，轨迹间比质量',[('两类训练监督',['专家帧级进度与成功','专家、失败及增强轨迹对']),('视频语言模型',['progress token：因果读历史','preference token：读两条轨迹']),('三项损失',['分桶进度交叉熵','成功分类损失','轨迹偏好分类损失'])],'依据 Robometer §III；两个监督来源，训练目标实际上还包含成功预测项。')
curve('robometer-failures','时间在前进，任务却可能退步',[[0,.3,.7,.2,.1],[0,.25,.5,.75,1]],['掉落后的实际进度示意','只按时间标注的伪进度'],'仅用成功轨迹的时间标签不足以刻画失败；偏好与回退增强提供补充监督。')

pipeline('sarm-method','SARM：先判断任务阶段，再估计阶段内进度',[('人工阶段标注',['完整示范分段','每段起止时间','计算跨示范阶段占比']),('双模型顺序预测',['冻结视觉特征 + 本体历史','阶段预测 → 子任务估计器']),('进度与 RA-BC',['阶段累计量 + 段内进度','动作块进度增量','筛选与重加权示范'])],'依据 SARM §3，任务特定阶段边界提供语义锚点；仍有阶段内线性时间假设。')
f=new('sarm-stage-labels','SARM：快慢演示，按阶段边界对齐进度','原创三阶段例子：阶段权重为 0.1、0.3、0.6；不是固定任务的官方配方。')
for y,title,widths in [(165,'较快示范',[45,135,270]),(300,'较慢示范',[90,270,540])]:
 f.text(35,y+35,title,23);x=250
 for w,label,c in zip(widths,['抓取','展平','折叠'],[BLUE,GREEN,PURPLE]):f.rect(x,y,w,70,fill=c,stroke=c,r=0);f.text(x+w/2,y+43,label,22,'white','middle');x+=w
f.text(600,450,'展平阶段的中点：$y=0.1+0.3\\times0.5=0.25$',28,PURPLE,'middle')
f.footer('原创对齐示意；相同阶段位置标签一致，但不同实际物理状态仍可能被线性插值赋予近似进度。');f.save()

pipeline('arm-method','ARM：学进步／退步／停滞，再重建进度',[('三态相对标注',['相邻观测与动作结果','进步、退步、停滞']),('因果 MIMO Transformer',['图像 + 状态 + 任务','区间分类头','任务完成头提供锚点']),('进度重建与 AW-BC',['相对变化结合完成锚点','长度归一化动作块增益','统计权重指导策略学习'])],'依据 ARM §3；相对进步分类不等同于精确估计 RL 的策略优势函数。')
curve('arm-regress-recover','退步与恢复都要看见，而不只看视频播放到了哪里',[[0,.4,.7,.3,.6,1]],['相对变化重建的进度示意'],'抓住、搬动、滑落、重新抓取、放好；退步不是应当被强制平滑掉的噪声。')

pipeline('dopamine-method','Robo-Dopamine：相对 hop、锚点融合与奖励塑造',[('带锚点的多视角状态',['起点、目标、前后状态','分阶段采样与 hop 标签']),('GRM 与进度融合',['增量、起点锚、终点锚','三种估计视角','可选一致性检查']),('Dopamine-RL',['适配新任务','用进度作势函数','按折扣构造 shaping'])],'依据 Robo-Dopamine §3；三种估计视角不是三台相机，多相机观测与估计方式是两个概念。')
f=new('dopamine-hops','Hop：前进按剩余距离算，后退按已走距离算','原创数值例子；起点进度为零，目标进度为一。')
f.line(130,260,1060,260,width=4)
for v in [0,.2,.4,.7,1]:
 x=130+930*v;f.line(x,250,x,270);f.text(x,305,f'${v}$',24,anchor='middle')
arr(f,502,230,781,230,GREEN);arr(f,502,340,316,340,ORANGE)
f.text(780,180,'前进：$(0.7-0.4)/(1-0.4)=0.5$',25,GREEN,'middle')
f.text(510,405,'后退：$(0.2-0.4)/(0.4-0)=-0.5$',25,ORANGE,'middle')
f.footer('原创 hop 几何解释；相同绝对进度差可能对应不同 hop，端点退化情况要按有效样本定义处理。');f.save()

pipeline('sarm2-method','SARM2：共享动作基元，让阶段条件跨任务复用',[('共享视觉特征',['三路相机 + 本体状态','首帧与近期帧','冻结 SigLIP-2']),('阶段与价值分别训练',['基元分类器','基元组选择 gate','共享专家池的 MMoE']),('输出与使用',['归一化剩余步数分数','适配策略 rollout','给 SPIRAL 提供监督'])],'依据 SARM2 §3.1；不是与 SARM v1 完全相同的单任务阶段头。')
pipeline('sarm2-spiral','SPIRAL：奖励模型是反馈环的一部分，不是动作策略',[('初始化与一次适配',['示范 BC 初始化 VLA','少量 rollout 人工标注','适配奖励模型']),('自主采样与重标注',['策略运行真实环境','奖励模型标注密集分数']),('残差 RL 与重复',['基础动作 + 残差修正','更新策略，再采集','持续监测奖励失真'])],'依据 SARM2 §3.2；一次性标注不代表没有前期人工成本或永远不需检查新分布。')

if __name__=='__main__':
 from playwright.sync_api import sync_playwright
 import re
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True)
  for n in NAMES:
   path=OUT/(n+'.svg');h=int(re.search(r'height="(\d+)"',path.read_text())[1])
   page=b.new_page(viewport={'width':1200,'height':h},device_scale_factor=2);page.goto(path.resolve().as_uri());page.screenshot(path=str(path.with_suffix('.png')));page.close()
  b.close()
