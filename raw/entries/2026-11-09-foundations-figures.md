# 基础概念原创图重绘

日期：2026-11-09。按用户要求将旧配图和 ASCII 字符示意图改为原创矢量图，保留实际代码与数值算例。

- 脚本：`scripts/draw_foundations.py`，执行 `python scripts/draw_foundations.py --png` 同时生成 SVG 与 2 倍 PNG。
- 图保存于 `wiki/imgs/foundations-*`，覆盖人工智能基础及刚体运动学；并非论文原图或实验结果。
- 核对图中文字、箭头和正文，修正卷积数值示例为 −6、KL 示例为约 0.635；本次图示重绘不表示对全部旧文完成事实核验。

- 图内公式以 `$...$` LaTeX 数学语法保存在绘图脚本，Matplotlib MathText 排版为 SVG 路径，SVG 的 `data-latex` 属性保留对应源码。读取图片不需要在线渲染服务。
