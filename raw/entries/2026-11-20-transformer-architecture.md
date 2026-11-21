# Transformer 经典框架图与读图说明

核验日期：2026-11-20。

- Vaswani 等，Attention Is All You Need（2017），[arXiv v7](https://arxiv.org/html/1706.03762v7)，§3.1–3.4 与 Figure 1。
- [原始图片 URL](https://arxiv.org/html/1706.03762v7/Figures/ModalNet-21.png)；[本地来源图片](../../wiki/imgs/transformer-original-figure-1.png)。文章显示的副本未修改。
- 原文开头授权说明：注明出处时，Google 允许在新闻或学术作品中复制图表。文章图注明确原图及来源，不伪装成原创图。
- 读图展开：编码器、解码器、右移目标、三个注意力子层的 QKV 来源、Add & Norm、FFN、训练与生成区别。翻译例子与统一列向量公式为解释性重写。
- 相邻修正：多头注意力伪代码误将 K 传入 V 参数，改为使用 V，补 nn 导入；纠正因果注意力不能并行训练和交叉注意力要求等长等表述。
- 本次未全面核验文章里全部注意力变体，尤其不将原文其他泛化比较当成本次已核验结论。
