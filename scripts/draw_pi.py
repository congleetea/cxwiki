from pathlib import Path
from html import escape
from playwright.sync_api import sync_playwright
OUT=Path(__file__).resolve().parents[1]/'wiki/imgs'; OUT.mkdir(parents=True,exist_ok=True)
BLUE='#07569b'; CYAN='#087fca'; PURPLE='#7542c8'; GREEN='#099773'; RED='#df624d'; INK='#103858'; BG='#f3f7fc'; MUTED='#557087'
def fig(name,title,subtitle,panels,footer):
    W,H=1600,900
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}">', '<defs><linearGradient id="head"><stop stop-color="#063c76"/><stop offset="1" stop-color="#087eae"/></linearGradient><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="#397bad" stroke-width="1.5"/></marker></defs><style>text{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif}</style>',f'<rect width="{W}" height="{H}" fill="{BG}"/><rect x="16" y="16" width="1568" height="112" rx="15" fill="url(#head)"/><text x="45" y="66" font-size="35" fill="white" font-weight="700">{escape(title)}</text><text x="46" y="103" font-size="20" fill="#d8efff">{escape(subtitle)}</text>']
    for i,p in enumerate(panels):
        x,y,w,h,label,color,items=p
        parts += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="white" stroke="{color}" stroke-width="2"/>',f'<rect x="{x+1}" y="{y+1}" width="{w-2}" height="54" rx="13" fill="{color}"/><circle cx="{x+30}" cy="{y+28}" r="18" fill="white"/><text x="{x+30}" y="{y+36}" text-anchor="middle" font-size="22" font-weight="700" fill="{color}">{i+1}</text>',f'<text x="{x+60}" y="{y+36}" font-size="25" fill="white" font-weight="700">{escape(label)}</text>']
        yy=y+96
        for line in items:
            if isinstance(line,tuple):
                kind,*vals=line
                if kind=='box':
                    bx,by,bw,bh,tx,tc=vals; parts += [f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="#eef7ff" stroke="{tc}" stroke-width="2"/>',f'<text x="{bx+15}" y="{by+32}" font-size="23" fill="{tc}" font-weight="700">{escape(tx)}</text>']
                elif kind=='arrow':
                    x1,y1,x2,y2=vals; parts += [f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#397bad" stroke-width="3" fill="none" marker-end="url(#a)"/>']
                elif kind=='text':
                    tx,ty,txt,sz,col,bold=vals;parts += [f'<text x="{tx}" y="{ty}" font-size="{sz}" fill="{col}" font-weight="{700 if bold else 400}">{escape(txt)}</text>']
            else:
                parts.append(f'<text x="{x+20}" y="{yy}" font-size="22" fill="{INK}">{escape(line)}</text>'); yy+=39
    parts += [f'<rect x="16" y="{H-93}" width="1568" height="77" rx="12" fill="url(#head)"/><text x="42" y="{H-57}" font-size="24" fill="white" font-weight="700">{escape(footer)}</text><text x="42" y="{H-29}" font-size="17" fill="#d8efff">原创原理示意；数字、坐标和适用条件以正文来源为准。</text></svg>']
    (OUT/f'{name}.svg').write_text(''.join(parts))

def main():
    fig('pi-flow','π₀：从条件观测到连续动作块','主干提供视觉语言条件，动作专家在流场中生成一段可执行动作。',[
      (35,165,485,560,'输入与表示',CYAN,['图像 I¹…Iⁿ + 状态 q','语言指令 ℓ','动作块 A∈Rᴴ×ᵈᵃ','',('box',58,390,420,82,'同一接口内归一化',CYAN),('text',75,510,'不同机器人仍需适配器',22,MUTED,False)]),
      (555,165,490,560,'双专家与注意力',PURPLE,['预训练 VLM 主干','动作专家：噪声动作 + τ','动作 token 读取前缀表示','',('box',585,390,430,82,'前向信息流：主干 → 专家',PURPLE),('text',600,510,'后续知识绝缘会选择性阻断梯度',22,MUTED,False)]),
      (1070,165,495,560,'流匹配采样',GREEN,['噪声 X₀ ~ N(0,I)','重复：X←X+Δτ·vθ(X,o,ℓ,τ)','得到 X₁≈动作块 A','',('box',1100,390,435,82,'反归一化 → 控制器 → 执行',GREEN),('text',1118,510,'生成时间与控制时间是两条轴',22,MUTED,False)]),
    ],'核心链路：语义条件 → 连续生成 → 物理接口')
    fig('pi-fast','FAST：把时间信号压缩成动作 token','DCT集中平滑轨迹的低频信息，BPE把量化后的整数序列合并。',[
      (35,165,350,560,'动作块',CYAN,['A∈Rᴴ×ᵈ','每列是一个动作通道','先用训练集分位数归一化','',('box',60,390,300,82,'[关节角 / 位移 / 夹爪]',CYAN)]),
      (425,165,350,560,'DCT 频域',PURPLE,['每个通道沿时间变换','低频：慢变化与整体趋势','高频：快速变化与接触细节','',('box',450,390,300,82,'平滑信号 → 稀疏系数',PURPLE)]),
      (815,165,350,560,'量化与展开',RED,['Q=round(γC)','按约定顺序展开整数矩阵','γ越大，细节多、token可能更长','',('box',840,390,300,82,'有损步骤：量化',RED)]),
      (1205,165,350,560,'BPE 与解码',GREEN,['合并常见符号组合','输出 z₁…zᴸ','逆 BPE → 逆 DCT → 反归一化','',('box',1230,390,300,82,'动作重建 / VLA 标签',GREEN)]),
    ],'FAST解决的是动作表示效率，不替代控制器和机器人本体适配')
    fig('pi-co-training','π₀.₅：异构数据共同教“做什么”和“怎么做”','无动作数据贡献语义与位置监督；机器人数据贡献物理交互。',[
      (35,165,430,560,'数据混合',CYAN,['机器人动作：多本体、多环境','子任务文字：pick up…','Web：描述、VQA、定位','人类视频属于后续迁移研究','',('box',65,510,370,82,'标签不同，不能互造监督',CYAN)]),
      (585,165,430,560,'预训练阶段',PURPLE,['FAST动作 token + next-token','语言 / 子任务 / 视觉任务','α=0：不训练流匹配损失','得到广泛视觉—动作表示','',('box',615,510,370,82,'先学表示与语义泛化',PURPLE)]),
      (1135,165,430,560,'后训练与执行',GREEN,['加入连续动作专家','L=L_token+αL_FM','高层生成子任务文字','低层生成连续动作块','',('box',1165,510,370,82,'新环境中闭环重观察',GREEN)]),
    ],'核心判断：泛化来自监督和场景的组合，不是“数据越杂越好”')
    fig('pi-ki','Knowledge Insulation：信息能读，噪声梯度不写回','离散 token loss 训练主干；流匹配 loss 训练动作专家。',[
      (35,165,455,560,'两类损失',CYAN,['L_AR：下一个离散 token','L_FM：连续动作速度场','同一次前向可共享表示','',('box',65,420,395,82,'主干需要稳定的机器人表示',CYAN)]),
      (570,165,455,560,'梯度路径',RED,['AR loss ─────→ VLM 主干','FM loss ─────→ 动作专家','FM 到主干经过 stop-gradient','前向注意力仍读取主干特征','',('box',600,510,395,82,'信息流 ≠ 梯度流',RED)]),
      (1115,165,450,560,'为何有用',GREEN,['避免随机初始化专家污染预训练表征','主干仍可由离散动作继续适配','专家读取主干并学习连续控制','代价：需要额外 token 监督与实现细节','',('box',1145,510,390,82,'保护迁移，同时允许适配',GREEN)]),
    ],'知识绝缘的边界：它改变训练梯度，不是冻结 VLM，也不是切断前向信息')
    fig('pi-recap','RECAP：从示范、纠正和自主经验提取更好策略','价值函数估计进展，优势条件作为策略输入；全流程可迭代。',[
      (35,165,455,560,'收集数据',CYAN,['示范数据初始化策略','自主 rollout 产生成败轨迹','机器人犯错时可人工接管纠正','D ← D ∪ 新轨迹','',('box',65,510,395,82,'好与坏样本都保留',CYAN)]),
      (570,165,455,560,'训练价值函数',PURPLE,['回报：成功终止=0，失败=-C','中间步=-1（论文设置）','Vϕ(o,ℓ) 预测未来回报','优势 A≈动作后价值−当前价值','',('box',600,510,395,82,'信用分配：早期错误也有信号',PURPLE)]),
      (1115,165,450,560,'优势条件策略',GREEN,['I=1[A>εℓ]','πθ(a|o,ℓ,I) 同时看全部数据','更新策略后再次 rollout','任务阈值与数据分布决定改进幅度','',('box',1145,510,390,82,'迭代提升，而非复制失败',GREEN)]),
    ],'RECAP把流匹配 VLA 的策略提取改造成可扩展的监督条件学习')
    fig('pi-memory','MEM：短时视频 + 长时语言记忆','密集视觉保留局部细节，语言摘要跟踪跨分钟任务进度。',[
      (35,165,455,560,'当前与近期观察',CYAN,['最近 K 秒图像、状态','视频编码器交替空间/时间注意力','丢弃历史 token，控制主干输入量','处理遮挡、重抓与动作时序','',('box',65,510,395,82,'短时：精确但窗口有限',CYAN)]),
      (570,165,455,560,'高层语言记忆',PURPLE,['mₜ：已完成事件摘要','π_HL(子任务,mₜ₊₁ | 当前,mₜ)','失败与进度写入自然语言','压缩无关细节，保留可决策信息','',('box',600,510,395,82,'长时：抽象且可读',PURPLE)]),
      (1115,165,450,560,'低层执行',GREEN,['π_LL(A | 近期视频,子任务)','高层更新不必每个控制周期发生','两条时间尺度共同闭环','作者报告最长约 15 分钟任务','',('box',1145,510,390,82,'MEM 集成到 π₀.₆',GREEN)]),
    ],'MEM不是把完整历史塞进上下文，而是按时间尺度改变表示')
    fig('pi-pi07-prompt','π₀.₇：用多模态提示解释“同一动作”的差异','语言、子任务、子目标图像、速度/质量和控制模式共同规定行为。',[
      (35,165,430,560,'数据为何冲突',CYAN,['不同机器人、不同速度','成功与失败、专家与自主','同一句任务可有多条策略','不加条件会互相平均','',('box',65,510,370,82,'问题：数据异质性',CYAN)]),
      (585,165,430,560,'提示包含怎么做',PURPLE,['Task / Subtask','视觉 subgoal image','Episode metadata：速度、质量、错误','Control mode：joint / ee','',('box',615,510,370,82,'条件把轨迹分布拆开',PURPLE)]),
      (1135,165,430,560,'运行时组合',GREEN,['世界模型可生成子目标图像','dropout让部分提示可缺省','π₀.₇生成连续动作块','可通过 coaching 细化新任务','',('box',1165,510,370,82,'steerable generalist',GREEN)]),
    ],'π₀.₇的核心是可控条件化，不是单纯堆更多无标注数据')
    fig('pi-rtc','RTC：冻结旧块前缀，再补绘新动作','冻结已错过的时间步；软约束重叠区域；流模型生成未来动作。',[(35,165,450,560,'异步延迟',CYAN,['旧块继续执行','新观测到达但推理尚未完成','d=floor(δ/Δt)','',('box',65,500,390,82,'等待会产生停顿',CYAN)]),(575,165,450,560,'一致性约束',RED,['前 d 步：冻结为旧动作','中间区域：衰减权重','末端：自由生成','',('box',605,500,390,82,'连续性与反应性权衡',RED)]),(1115,165,450,560,'流模型补绘',GREEN,['噪声动作块 + 旧块目标','ΠGDM式速度校正','积分直到完整新块','',('box',1145,500,390,82,'只执行尚未过时的部分',GREEN)])],'核心链路：异步执行 → 重叠约束 → 无停顿切换')
    fig('pi-human','人类视频迁移：共享相对运动和子任务','人类数据补充场景与语义，机器人数据保留夹爪与本体执行。',[(35,165,450,560,'人类视频',CYAN,['头戴相机 SLAM：eₜ∈SE(3)','手部 3D 关键点','相对末端动作 Δp,ΔR','',('box',65,500,390,82,'没有可靠的夹爪开度',CYAN)]),(575,165,450,560,'共享 VLA 表示',PURPLE,['子任务文字标注','高层：预测下一子任务','低层：动作块预测','人类与机器人同一训练目标','',('box',605,500,390,82,'跨场景 / 物体 / 任务',PURPLE)]),(1115,165,450,560,'机器人接口',GREEN,['相对动作 → 本体适配器','夹爪与接触由机器人数据学习','控制器检查可达、碰撞和延迟','',('box',1145,500,390,82,'视频不是逐帧遥控',GREEN)])],'核心链路：人类情境 → 共享表示 → 机器人可执行接口')
    fig('pi-rlt','RLT：大 VLA 表示瓶颈，小 actor-critic 在线更新','冻结大模型，只在参考动作附近做局部策略编辑。',[(35,165,450,560,'VLA 表示',CYAN,['z₁…zₘ：多模态 token','encoder 输出 z_rl','decoder 重建原表示','训练后冻结','',('box',65,500,390,82,'压缩状态而非压缩动作接口',CYAN)]),(575,165,450,560,'参考动作',PURPLE,['VLA 采样 ā₁:C','actor 同时读取 z_rl 与 ā','动作块保持时间结构','参考动作 dropout 防复制','',('box',605,500,390,82,'从已有能力附近探索',PURPLE)]),(1115,165,450,560,'在线 RL',GREEN,['critic：TD 目标','actor：−Q + β‖a−ā‖²','replay buffer 持续更新','关键接触阶段优先','',('box',1145,500,390,82,'分钟级任务适应（作者报告）',GREEN)])],'核心链路：冻结知识 → 小模型学习 → 局部精细化')
    fig('pi-pi07-prompt','π₀.₇：用提示拆开不同策略','任务、子任务、子目标、速度、质量、错误和控制模式共同约束动作。',[(35,165,450,560,'异质轨迹',CYAN,['不同机器人与控制接口','不同速度和质量','成功、失败、自主和人类','',('box',65,500,390,82,'无条件混合会互相平均',CYAN)]),(575,165,450,560,'多模态条件',PURPLE,['语言任务/子任务','未来子目标图像','episode metadata','joint / ee 控制模式','',('box',605,500,390,82,'告诉模型“怎么做”',PURPLE)]),(1115,165,450,560,'可控执行',GREEN,['dropout 支持条件缺省','世界模型生成目标图像','连续专家生成动作块','coaching 可细化新任务','',('box',1145,500,390,82,'组合泛化与 steerability',GREEN)])],'核心链路：多源轨迹 → 条件化表示 → 按意图执行')
    with sync_playwright() as p:
      b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']); page=b.new_page(device_scale_factor=1.5)
      for svg in OUT.glob('pi-*.svg'):
        page.goto(svg.resolve().as_uri()); page.locator('svg').screenshot(path=str(svg.with_suffix('.png')))
      b.close()
if __name__=='__main__': main()
