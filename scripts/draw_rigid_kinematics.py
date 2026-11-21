"""Original geometric illustrations for the rigid body kinematics article."""
from draw_foundations import Fig, BLUE, PURPLE, GREEN, ORANGE, OUT


def axes(f,x,y,rot=False):
    f.line(x,y,x+(0 if rot else 150),y- (150 if rot else 0),BLUE,True,width=3)
    f.line(x,y,x- (150 if rot else 0),y-(0 if rot else 150),GREEN,True,width=3)
    f.text(x+(10 if rot else 150),y-(155 if rot else 12),'$x_B$' if rot else '$x_A$',22,BLUE)
    f.text(x-(185 if rot else 35),y-(0 if rot else 155),'$y_B$' if rot else '$y_A$',22,GREEN)

f=Fig('rigid-basis','01  旋转矩阵的列：新坐标轴在旧坐标系中的方向','俯视 xy 平面；两系原点重合，B 相对 A 绕 +z 转 90°。',520)
axes(f,260,340);axes(f,260,340,True)
f.text(275,365,'$O$；$+z$ 垂直图面向外',21)
f.box(560,135,600,260,'把 B 的轴逐列装进 $R$',[
 '第一列：$x_B$ 在 A 中为 $(0,1,0)$',
 '第二列：$y_B$ 在 A 中为 $(-1,0,0)$',
 '第三列：$z_B$ 在 A 中为 $(0,0,1)$',
 'B 中 $(1,0,0)$ → A 中 $(0,1,0)$'],PURPLE)
f.footer('原创几何示意：坐标变换时，向量没有移动，变化的是描述它的三个分量。');f.save()

f=Fig('rigid-transform','02  齐次变换：先换方向，再加原点偏移','同一个点 P；R = Rz(90°)，t = (1, 2, 0) m。',560)
# schematic with equal x/y scale 75 pixels per metre
ox,oy=160,430
f.line(ox,oy,490,oy,BLUE,True);f.line(ox,oy,ox,130,GREEN,True)
f.text(490,455,'$x_A$',22);f.text(115,125,'$y_A$',22)
bx,by=235,280;px,py=235,205
f.line(ox,oy,bx,by,PURPLE,True,width=4);f.text(265,365,'$t=(1,2,0)$',22,PURPLE)
f.line(bx,by,px,py,GREEN,True,width=4);f.text(255,245,'$R\\,{}^Bp$',22,GREEN)
f.line(ox,oy,px,py,ORANGE,True,width=3)
f.text(70,295,'${}^Ap$',24,ORANGE);f.text(190,305,'$O_B$',22);f.text(245,195,'$P:(1,3,0)_A$',22)
f.box(580,140,570,290,'沿箭头相加，就到达同一个 P',[
 '① B 中的点：${}^Bp=(1,0,0)$',
 '② A 中方向：$R\\,{}^Bp=(0,1,0)$',
 '③ 加偏移：${}^Ap=(1,3,0)$',
 '方向向量没有原点偏移，只做第②步',
 '反向变换：先减 $t$，再乘 $R^T$'],BLUE)
f.footer('原创平面例子；z 分量为零。紫箭头与绿箭头首尾相接，等于橙箭头。');f.save()

f=Fig('rigid-velocity','03  刚体点速度：整体平移 + 绕原点转动','固定参考系的俯视图；ω 沿 +z 向外，刚体逆时针转动。',540)
f.line(120,340,340,340,PURPLE,True,width=4);f.text(160,375,'$r_{OP}$',23,PURPLE)
f.text(85,340,'$O$',25);f.text(345,365,'$P$',25)
f.line(120,340,220,270,BLUE,True,width=4);f.text(125,255,'$v_O$',23,BLUE)
f.line(340,340,440,270,BLUE,True,width=4)
f.line(440,270,440,150,GREEN,True,width=4);f.text(455,225,'$\\omega\\times r_{OP}$',23,GREEN)
f.line(340,340,440,150,ORANGE,True,width=4);f.text(320,210,'$v_P$',24,ORANGE)
f.text(75,425,'$\\odot\\;\\omega$；同一刚体角速度相同',22)
f.box(660,135,490,285,'在 P 点做速度向量相加',[
 '蓝：随 $O$ 一起平移的速度',
 '绿：绕 $O$ 转动的切向速度',
 '橙：$P$ 在固定系中的总速度',
 '$v_P=v_O+\\omega\\times r_{OP}$',
 '本例 $r_{OP}$ 向右，转动速度向上'],BLUE)
f.footer('原创速度分解；速度箭头表示向量相加，其长度采用独立于位置的示意比例。');f.save()

if __name__ == '__main__':
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for path in OUT.glob('rigid-*.svg'):
            import re
            height=int(re.search(r'height="(\d+)"',path.read_text())[1])
            page=browser.new_page(viewport={'width':1200,'height':height},device_scale_factor=2)
            page.goto(path.resolve().as_uri())
            page.screenshot(path=str(path.with_suffix('.png')))
            page.close()
        browser.close()
