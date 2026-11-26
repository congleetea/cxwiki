"""Draw the PEFT background's toy full fine-tuning example."""
from draw_foundations import Fig, BLUE, PURPLE, GREEN, ORANGE, OUT

def main():
    f = Fig('foundations-full-finetuning', '全量微调：直接更新已有模型的全部参数',
            '教学算例：线性模型的两个参数都参与训练；使用一次梯度下降。', 490)
    f.box(30, 132, 265, 210, '① 加载预训练权重',
          [r'$w=1,\ b=0$', r'$\hat y=wx+b$', r'样本：$x=2,\ y=5$'], BLUE)
    f.box(320, 132, 265, 210, '② 前向与损失',
          [r'$\hat y=2$', r'$L=\frac{1}{2}(\hat y-y)^2$', r'$L=4.5$'], PURPLE)
    f.box(610, 132, 265, 210, '③ 反向与更新',
          [r'$\partial_w L=-6$', r'$\partial_b L=-3$', r'学习率 $\eta=0.1$'], ORANGE)
    f.box(900, 132, 270, 210, '④ 更新后的模型',
          [r'$w=1.6,\ b=0.3$', r'$\hat y=3.5$', '保存更新后的权重'], GREEN)
    for x in (295, 585, 875):
        f.line(x+3, 235, x+22, 235, arrow=True)
    f.path('M1035 345 L1035 382 L452 382 L452 350', GREEN, 3)
    f.line(452, 357, 452, 347, GREEN, arrow=True)
    f.text(745, 414, '下一批数据：使用当前权重继续训练', 24, GREEN, 'middle')
    f.footer('训练是在同一组模型参数上反复更新，而不是额外训练一套与原模型同样大的参数。')
    f.save()

if __name__ == '__main__':
    main()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width':1200,'height':490}, device_scale_factor=2)
        path = OUT / 'foundations-full-finetuning.svg'
        page.goto(path.resolve().as_uri())
        page.screenshot(path=str(path.with_suffix('.png')))
        browser.close()
