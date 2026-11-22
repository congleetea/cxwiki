# Transformer 图解系列：来源、版本与验证

核验日期：2026-11-21。九篇概念按学习依赖编排，不以某个最新模型作为全部 Transformer 的定义。

## 原始材料

- **Vaswani 等，Attention Is All You Need**，2017；核验 v7，2023-08-02。[原文](https://arxiv.org/html/1706.03762v7) · [本地 PDF](../papers/transformer/attention-is-all-you-need.pdf)。§3、Figure 1–2、§5：模块、行列维度转换、遮罩、右移、经典配方。 SHA-256：`bdfaa68d8984f0dc02beaca527b76f207d99b666d31d1da728ee0728182df697`。
- **Xiong 等，On Layer Normalization in the Transformer Architecture**，2020；v1。[原文](https://arxiv.org/html/2002.04745v1) · [本地 PDF](../papers/transformer/pre-ln.pdf)。§3：Post-LN／Pre-LN 与初始化分析条件。 SHA-256：`af4234e423f7e89acc075fee9edf45a9317689524baac1071da30100d8a26bb8`。
- **Su 等，RoFormer**，2021；核验 v5，2023-11-08。[原文](https://arxiv.org/html/2104.09864v5) · [本地 PDF](../papers/transformer/rope.pdf)。§3：二维旋转、相对位置点积、Query／Key 的处理。 SHA-256：`e9a481fbe1c8a20b7b1fa566b13102a1896c7829fa9a8b4c80528452a5ddaf79`。
- **Devlin 等，BERT**，2018；核验 v2，2019-05-24。[原文](https://arxiv.org/html/1810.04805v2) · [本地 PDF](../papers/transformer/bert.pdf)。§3 及附录：双向编码、MLM、NSP、输入表示与扰动策略。 SHA-256：`5692a5514787a8c6727b4ff3b726a3385798bc68e12138d1d4af83947e2acf6e`。
- **Radford 等，GPT-2 报告**，2019；官方报告。[原文](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) · [本地 PDF](../papers/transformer/gpt2.pdf)。§2：自回归目标与 §2.3 的归一化位置修改。 SHA-256：`d9d852e2894556e73f53cb22b7c605a9643d6f0b19bf604b429ed6192fa24f4e`。
- **Dosovitskiy 等，ViT**，2020；核验 v2，2021-06-03。[原文](https://arxiv.org/html/2010.11929v2) · [本地 PDF](../papers/transformer/vit.pdf)。§3、Figure 1：Patch 投影、位置表示、分类接口。 SHA-256：`8ce7b83971a14508ca711a27c875c9b6914c4f6767cf3150fb1ca6c07aa056d6`。
- **Dao 等，FlashAttention**，2022；核验 v2。[原文](https://arxiv.org/html/2205.14135v2) · [本地 PDF](../papers/transformer/flashattention.pdf)。§3 与附录：分块、稳定在线 softmax、IO 与算术复杂度的区别。 SHA-256：`ca7f9fda10b90fc05dd291a3accc85e9c1a4a860b99b31928dab03ed3fcb14e4`。
- **Ainslie 等，GQA**，2023；[v3 原文](https://arxiv.org/html/2305.13245v3)，§2：Query 头与 KV 头分组共享。在线阅读，未保存 PDF。

## 推导与插图的性质

- 全系列除 RoPE 局部二维几何外，统一行向量约定；RoPE 局部列向量与右乘转置的对应在正文说明。
- 注意力手算、缓存容量、在线 softmax 重写与置换等变说明是教学推导；不声称为原论文某次实验的测量结果。
- 原始 Transformer Figure 1 沿用已有清晰来源图，按论文开头 Google 的图表授权声明注明出处。另作中文 SVG／PNG 重绘，标明来源；不改写原始图片。
- 新增二十六张解释性 SVG／PNG，六个 MP4 动画及其静态首帧 SVG／PNG，源脚本为 `scripts/draw_transformer_series.py`。所有公式由 LaTeX 数学源经排版器转成 SVG 路径，再栅格化与编码；没有生成式图片绘制公式。
- 动画是分阶段的慢速说明，不是真实 GPU 执行时间线。页面使用本地 H.264 MP4，原生播放控件可暂停、拖动、重播，不依赖外站视频。
- 不同注意力头的颜色不作为固定语义职责；热图不作为模型解释的因果证据。
- 未运行上述论文的完整训练或基准测试；只验证教学例子、结构检查、渲染和本地动画播放。

## 阅读入口

- [Transformer 00：整体框架与各模块的作用](../../wiki/00-concepts/03-ai-foundations/transformer-00-overview.md)。

- [Transformer 01：Token、嵌入与上下文表示](../../wiki/00-concepts/03-ai-foundations/transformer-01-tokens-embeddings.md)。
- [Transformer 04：经典 Encoder–Decoder 架构](../../wiki/00-concepts/03-ai-foundations/transformer-04-encoder-decoder.md)。

- 补充系列开篇整体概念讲解：翻译任务全流程、经典原图、模块职责与训练／生成关系。两张新增图稿由 `scripts/draw_transformer_intro.py` 重建；原有详细篇保留稳定编号和链接。
