"""Generate editable SVG technical figures. PNG export: --png (Playwright + Chrome)."""
from pathlib import Path
from html import escape
import argparse

OUT = Path(__file__).resolve().parents[1] / 'wiki' / 'imgs'
BLUE, CYAN, PURPLE, GREEN, RED = '#07569b', '#087fca', '#7542c8', '#099773', '#e06450'
INK, MUTED = '#103858', '#4f6980'


class Figure:
    def __init__(self, name, title, subtitle, height=900):
        self.name, self.height = name, height
        self.s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}" role="img" aria-label="{escape(title)}">',
                  '<defs><linearGradient id="header"><stop stop-color="#063c76"/><stop offset="1" stop-color="#087eae"/></linearGradient>'
                  '<marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="#397bad" stroke-width="1.6"/></marker></defs>',
                  '<style>text{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif} .label{font-weight:700}</style>']
        self.rect(0, 0, 1600, height, '#f3f7fc', r=0)
        self.rect(16, 16, 1568, 110, 'url(#header)', r=15)
        self.text(42, 64, title, 34, '#fff', True)
        self.text(44, 103, subtitle, 21, '#d8efff')

    def rect(self, x, y, w, h, fill='white', stroke='none', r=12):
        self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')

    def text(self, x, y, text, size=24, color=INK, bold=False, anchor='start'):
        self.s.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(text)}</text>')

    def lines(self, x, y, lines, size=23, color=INK, gap=37):
        for i, line in enumerate(lines):
            self.text(x, y+i*gap, line, size, color)

    def panel(self, x, y, w, h, n, title, color=CYAN):
        self.rect(x, y, w, h, '#fff', color)
        self.rect(x+1, y+1, w-2, 52, color, r=10)
        self.s.append(f'<circle cx="{x+28}" cy="{y+27}" r="18" fill="white"/>')
        self.text(x+28, y+35, str(n), 23, color, True, 'middle')
        self.text(x+57, y+35, title, 25, 'white', True)

    def box(self, x, y, w, h, title, lines=(), color=CYAN, fill='#eef7ff'):
        self.rect(x, y, w, h, fill, color)
        self.text(x+18, y+34, title, 25, color, True)
        self.lines(x+18, y+72, lines, 22, gap=34)

    def arrow(self, x1, y1, x2, y2, label=None):
        self.s.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="#397bad" stroke-width="3" fill="none" marker-end="url(#arrow)"/>')
        if label:
            self.text((x1+x2)/2, (y1+y2)/2-12, label, 20, MUTED, anchor='middle')

    def footer(self, main, detail='原创原理示意 · 具体约定与适用条件见正文 · cxwiki / 2026-11-05'):
        y = self.height - 94
        self.rect(16, y, 1568, 78, 'url(#header)')
        self.text(40, y+32, main, 25, '#fff', True)
        self.text(40, y+61, detail, 18, '#d8efff')

    def save(self):
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f'{self.name}.svg').write_text('\n'.join(self.s)+ '\n</svg>')


def overview():
    f = Figure('retargeting-overview', '机器人动作重定向：保留什么？怎样求解？如何执行？',
               '从人体运动到机器人动作：先定义关系，再构造目标，用约束求解，最后检验物理执行。', 1160)
    f.panel(16, 144, 505, 302, 1, '为什么不能直接复制？', RED)
    f.box(32, 211, 473, 105, '形态不同 → 目标可能互相冲突', ['骨长、关节轴、限位、身体比例不同'], RED, '#fff3ef')
    f.lines(38, 356, ['手碰膝盖：位置像 ≠ 真的触碰', '脚底不穿地 ≠ 不滑脚 ≠ 站得稳'], 23, gap=40)
    f.panel(537, 144, 1047, 302, 2, '表示与目标：先说明每个数值的含义', CYAN)
    f.box(554, 218, 302, 164, '源动作', ['BVH / SMPL / 视频估计', '局部骨架 → 世界位姿', '身体名 → 位置 + 朝向'])
    f.box(910, 218, 302, 164, '形态适配', ['坐标与单位统一', '框架偏置 + 分部位缩放', '决定保留位置 / 姿态 / 关系'])
    f.box(1266, 218, 300, 164, '机器人目标', ['手、脚、骨盆等目标', '权重、接触与任务关系', '机器人 FK 负责计算当前值'])
    f.arrow(863, 300, 902, 300)
    f.arrow(1219, 300, 1258, 300)
    f.text(565, 424, '机器人配置 q：基座位置 + 四元数 + 关节角；广义速度 v 的维度与 q 不同。', 22, MUTED)
    f.panel(16, 465, 1035, 345, 3, '算法主干：误差 → 线性化 → QP → 积分', BLUE)
    for x, title, lines in [(34, '比较当前与目标', ['FK(q) 得身体位姿', '构造误差 e 与雅可比 J']),
                             (379, '求局部速度 v', ['最小化跟踪误差与速度', '同时处理限位 / 地面 / 避碰']),
                             (724, '积分，再重新计算', ['q⁺ = Integrate(q, v, Δt)', '下一帧热启动；逐帧推进'])]:
        f.box(x, 542, 309, 157, title, lines, BLUE)
    f.arrow(350, 616, 370, 616)
    f.arrow(695, 616, 715, 616)
    f.rect(34, 723, 999, 64, '#eaf2fb')
    f.text(54, 764, 'GMR：目标构造与两阶段 IK    PyRoki：组合优化    FRAX：编译与批处理', 24, BLUE, True)
    f.panel(1067, 465, 517, 345, 4, '约束为什么需要权衡？', PURPLE)
    f.box(1084, 542, 483, 131, 'ElastiQP：用 L₁ 松弛处理冲突', ['有解可继续 ≠ 每条约束都满足', '罚系数与约束残差必须一起看'], PURPLE, '#f5efff')
    f.lines(1090, 718, ['局部步、球形近似、离散误差仍存在', '求解成功不能替代碰撞与限位检查'], 23, gap=40)
    f.panel(16, 830, 766, 214, 5, '从参考动作到真实执行', GREEN)
    f.lines(40, 922, ['参考轨迹 + 状态反馈 → 控制器 → 力矩与接触', 'SONIC / ExtremControl：处理物理追踪与控制接口', '还需验证：平衡、摩擦、执行器能力与真实延迟'], 23, gap=42)
    f.panel(798, 830, 786, 214, 6, '怎样判断结果好不好？', CYAN)
    f.lines(822, 922, ['几何：位姿 / 相对关系    接触：脚滑 / 穿透', '动态：速度 / 抖动 / 执行成功率    约束：违反量', '性能：单流延迟与多片段吞吐分别计时'], 23, gap=42)
    f.footer('核心判断：重定向质量 = 目标是否正确 + 求解是否可靠 + 下游是否可用')
    f.save()


def representation():
    f = Figure('retargeting-representation', '表示与坐标：相同的动作，为什么会变成不同的数字？',
               '四件事分别检查：骨架层级、世界坐标、身体局部框架、形态比例。', 900)
    f.panel(16, 146, 766, 294, 1, '局部骨架 → 世界位姿', CYAN)
    f.box(36, 221, 328, 135, '相对父骨骼的变换', ['髋 → 大腿 → 小腿 → 脚', '不能把局部量直接当世界坐标'])
    f.box(426, 221, 336, 135, '沿骨架逐级相乘', ['Tᵂᵢ = Tᵂparent · Tparentᵢ', '得到每个部位的世界位置 / 朝向'])
    f.arrow(371, 288, 417, 288)
    f.text(40, 408, 'BVH 通道与骨段偏移必须按文件约定解释。', 23, MUTED)
    f.panel(798, 146, 786, 294, 2, '统一世界坐标：整体表达改变', BLUE)
    # Coordinate axes, deliberately separate from formula box.
    f.arrow(856, 355, 856, 245)
    f.arrow(856, 355, 973, 355)
    f.text(837, 236, 'Z', 24, BLUE, True)
    f.text(980, 361, 'X', 24, BLUE, True)
    f.box(1020, 221, 544, 135, '世界变换左乘：Tnew = C · Told', ['例如 Y-up → Z-up；不改变骨长比例', '位置单位先统一为米，不包含在刚体 C 中'], BLUE)
    f.text(822, 408, '现象：整个人倒下或运动方向错误 → 先查世界坐标。', 23, MUTED)
    f.panel(16, 461, 766, 320, 3, '身体框架偏置：局部轴对齐', PURPLE)
    f.box(36, 536, 726, 118, '框架变换右乘：Ttarget = Tbody · Toffset', ['人体脚局部轴与机器人脚局部轴未必一致', '朝向对齐与位置偏置需要写清所在坐标系'], PURPLE, '#f5efff')
    f.lines(42, 701, ['现象：脚位置对，但朝向扭了 90° → 查局部轴偏置', '对应“有几何含义的框架”，而不是只对应关节名'], 23, gap=40)
    f.panel(798, 461, 786, 320, 4, '形态缩放：改变目标的身体比例', GREEN)
    f.box(818, 536, 746, 118, '根轨迹与局部身体分别处理', ['根：走多远？    局部：手脚离身体多远？', '腿长比例与上半身触达比例可使用不同缩放'], GREEN, '#edf9f4')
    f.lines(824, 701, ['现象：方向正确，但手够不到 / 脚高度不对 → 查缩放', '缩放不是 SE(3) 刚体变换；不能当作标定偏置'], 23, gap=40)
    f.footer('先确认数值的含义，再优化误差；权重无法修复错误的坐标约定。')
    f.save()


def diffik():
    f = Figure('retargeting-diffik', '微分 IK：把“机器人应该到哪里”变成“下一步怎么动”',
               '通用原理示意；实际旋转残差、雅可比和权重约定以实现为准。', 960)
    f.panel(16, 147, 470, 337, 1, '比较目标与当前状态', CYAN)
    f.box(36, 224, 430, 104, '目标：位置与朝向', ['人体映射、缩放和偏置后的结果'])
    f.box(36, 351, 430, 106, '当前：FK(q)', ['输出身体位置、朝向与雅可比'])
    f.panel(543, 147, 496, 337, 2, '局部线性化', BLUE)
    f.lines(568, 245, ['误差 e：当前值 − 目标值', '误差变化：ė ≈ Jv', '希望误差下降：Jv ≈ −Ke'], 27, gap=59)
    f.text(568, 446, 'J 把广义速度映射到任务误差变化。', 22, MUTED)
    f.panel(1096, 147, 488, 337, 3, '求解速度 v', PURPLE)
    f.lines(1120, 244, ['min  ½‖W(Jv + Ke)‖²', '       + ½vᵀΛv', 's.t.  Gv ≤ h，Av = b'], 28, PURPLE, gap=57)
    f.text(1120, 444, '跟踪、正则与约束在同一问题中权衡。', 22, MUTED)
    f.arrow(494, 314, 532, 314)
    f.arrow(1047, 314, 1085, 314)
    f.panel(16, 507, 1023, 326, 4, '积分到下一配置，再重新计算', GREEN)
    f.box(36, 583, 983, 110, 'q⁺ = Integrate(q, v, Δt)', ['四元数基座：nq = n + 7，nv = n + 6；不能直接做 q + vΔt'], GREEN, '#edf9f4')
    f.lines(42, 742, ['当前配置 → 解一次局部 QP → 流形积分 → 新配置', '下一帧继续热启动；首帧通常需要多次迭代建立初始姿态'], 24, gap=45)
    f.panel(1096, 507, 488, 326, 5, '一个可算的小例子', BLUE)
    f.lines(1120, 602, ['角度误差 −0.2 rad', '增益 10 /s → 希望速度 2 rad/s', '限速 0.8 rad/s → 取 0.8', '步长 0.01 s → 只移动 0.008 rad'], 24, gap=55)
    f.footer('局部 QP 决定这一小步；轨迹连续性、接触与物理稳定性需要另行建模和验证。')
    f.save()


def elastic():
    f = Figure('retargeting-elastic', '弹性约束：始终有解，为什么不等于始终安全？',
               '一维速度示意；松弛让冲突时仍能给出折中，违反量需要被显式检查。', 900)
    f.panel(16, 146, 1568, 276, 1, '两个冲突条件：v ≥ 0.6，同时 v ≤ 0.2', RED)
    f.rect(122, 248, 294, 56, '#edf9f4')
    f.rect(984, 248, 432, 56, '#f3edff')
    f.arrow(118, 327, 1447, 327)
    for x, label in [(122, '0'), (416, '0.2'), (984, '0.6'), (1416, '0.9')]:
        f.s.append(f'<path d="M{x} 317 V338" stroke="{BLUE}" stroke-width="2"/>')
        f.text(x, 371, label, 24, BLUE, anchor='middle')
    f.text(150, 283, '满足 v ≤ 0.2', 24, GREEN, True)
    f.text(1010, 283, '满足 v ≥ 0.6', 24, PURPLE, True)
    f.text(700, 284, '没有交集 → 硬约束无解', 26, RED, True, 'middle')
    f.panel(16, 443, 766, 337, 2, '引入松弛：允许付出代价', PURPLE)
    f.box(36, 518, 726, 118, 'Gv ≤ h + s，s ≥ 0', ['目标函数加上 ρᵀs：违反越多，支付越多', '每条不等式可设置不同罚系数'], PURPLE, '#f5efff')
    f.lines(42, 686, ['求解器把松弛解析消去，减轻计算开销', '硬等式仍需相容；不是任意矛盾都能自动消失'], 23, gap=43)
    f.panel(798, 443, 786, 337, 3, '真正要检查什么？', GREEN)
    f.lines(824, 544, ['① 违反了哪条约束？最大违反量是多少？', '② 罚系数是否足够？求解是否收敛？', '③ 球形近似、离散步与筛选漏掉了什么？', '④ 输出参考轨迹能否被物理控制器执行？'], 25, gap=57)
    f.footer('有解是计算层面的性质；安全与可执行性取决于约束是否满足及模型是否充分。')
    f.save()


def batching():
    f = Figure('retargeting-batching', '离线批处理：并行的是动作片段，不是同一片段的所有帧',
               '横向依赖保留时间连续性；纵向并行提高总吞吐；两者回答不同的性能问题。', 900)
    f.panel(16, 146, 1040, 522, 1, '片段内顺序扫描，片段间独立并行', CYAN)
    for row, (label, color) in enumerate([('片段 A', CYAN), ('片段 B', PURPLE), ('片段 C', GREEN)]):
        y = 242 + row * 130
        f.text(40, y+37, label, 25, color, True)
        for col in range(4):
            x = 170 + col * 218
            f.rect(x, y, 171, 78, '#f2f7fd', color)
            f.text(x+85, y+34, f'帧 {col+1}', 23, color, True, 'middle')
            f.text(x+85, y+61, '状态 → IK → 积分', 18, MUTED, anchor='middle')
            if col < 3:
                f.arrow(x+177, y+39, x+208, y+39)
    f.text(40, 644, '每条片段首帧先收敛；后续传递配置与 QP 热启动状态。', 23, MUTED)
    f.panel(1073, 146, 511, 522, 2, '为什么批处理快？', PURPLE)
    f.box(1091, 220, 475, 115, 'JAX 编译 + 时间 scan', ['减少 Python 逐帧调度开销'], PURPLE, '#f5efff')
    f.box(1091, 353, 475, 115, '长度分桶 + 编译缓存', ['补齐长度，复用输入形状'], PURPLE, '#f5efff')
    f.box(1091, 486, 475, 150, '跨设备执行独立片段', ['总帧数 / 总处理时间 → 批吞吐', '它不是在线单帧响应延迟'], PURPLE, '#f5efff')
    f.rect(16, 689, 1568, 93, '#fff5e5', '#e7b45a')
    f.text(40, 726, '公平计时：硬件 / 并行数 / 约束 / 精度 / 误差容忍度一致，并报告首次编译与 I/O。', 25, '#80531a', True)
    f.text(40, 763, '在线看 p50 / p95 单流延迟；离线看吞吐与总耗时。不能直接相除得出统一条件下的加速比。', 23, '#80531a')
    f.footer('性能比较先对齐问题与计时边界，再比较数字。')
    f.save()


def geometry():
    f = Figure('retargeting-geometry', '一个几何例子：人够得到，机器人为什么够不到？',
               '相同末端目标不代表相同可达性；可改变身体配置，也可重新选择要保留的任务关系。', 900)
    panels = [(16, '源动作：长臂到达目标', CYAN),
              (543, '短臂机器人：目标不可达', RED),
              (1070, '移动基座：重新进入可达域', GREEN)]
    for i, (x, title, color) in enumerate(panels):
        f.panel(x, 146, 514, 554, i+1, title, color)
        f.text(x+24, 244, ['两段各 0.35 m；目标距离 0.60 m',
                           '两段各 0.22 m；目标距离 0.60 m',
                           '基座前移 0.22 m；剩余 0.38 m'][i], 21, MUTED)
        target, sy = (x+400, 400)
        sx = x+100 if i<2 else x+210
        length = 175 if i==0 else 110
        if i==1:
            ex, ey, hx, hy = sx+110, sy, sx+220, sy
        else:
            hx, hy = target, sy
            ex = (sx+hx)/2
            ey = sy-(length**2-((hx-sx)/2)**2)**0.5
        f.rect(sx-34, 468, 68, 23, '#e6eef7', color, 5)
        f.s.append(f'<path d="M{sx} 466 V{sy}" stroke="{color}" stroke-width="8"/>')
        f.s.append(f'<path d="M{sx} {sy} L{ex} {ey} L{hx} {hy}" fill="none" stroke="{color}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>')
        for jx, jy in [(sx,sy), (ex,ey), (hx,hy)]:
            f.s.append(f'<circle cx="{jx}" cy="{jy}" r="11" fill="white" stroke="{color}" stroke-width="5"/>')
        f.s.append(f'<circle cx="{target}" cy="{sy}" r="22" fill="none" stroke="{PURPLE}" stroke-width="2" stroke-dasharray="5 4"/>')
        f.s.append(f'<path d="M{target-11} {sy} H{target+11} M{target} {sy-11} V{sy+11}" stroke="{PURPLE}" stroke-width="2"/>')
        f.text(target, 449, '末端目标', 21, PURPLE, anchor='middle')
        if i==1:
            f.s.append(f'<path d="M{hx+12} {hy} H{target-25}" stroke="{RED}" stroke-width="2" stroke-dasharray="6 5"/>')
            f.text(x+275, 353, '差 0.16 m', 23, RED, True)
        if i==2:
            f.arrow(x+100, 513, sx, 513)
            f.text(x+155, 552, '基座平移', 22, GREEN, anchor='middle')
        f.lines(x+24, 606, [
            ['可达：选一个弯肘解', '同一目标也可能有多种关节姿态'],
            ['再增加位置权重也无法够到', '不可达首先是几何问题'],
            ['几何上可达；代价是身体改变位置', '双足实机移动仍需要动力学控制']][i], 22, gap=43)
    f.rect(16, 721, 1568, 61, '#eef3fc', BLUE)
    f.text(40, 760, '两连杆最大触达 = l₁ + l₂。重定向要决定：保持身体位置、保持末端目标，还是改变两者的权衡？', 24, BLUE, True)
    f.footer('调整目标与允许的自由度，往往比更换求解器更先决定是否有解。',
             '原创二维几何示意 · 长度与距离按相同比例绘制 · 不表示具体机器人或实机验证结果')
    f.save()


def export_png():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        page = browser.new_page(device_scale_factor=1.5)
        for svg in sorted(OUT.glob('retargeting-*.svg')):
            page.goto(svg.as_uri())
            page.evaluate('document.fonts.ready')
            page.locator('svg').screenshot(path=str(svg.with_suffix('.png')))
        browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--png', action='store_true')
    args = parser.parse_args()
    for draw in [overview, representation, diffik, elastic, batching, geometry]:
        draw()
    if args.png:
        export_png()
    print(f'Generated figures in {OUT}')
