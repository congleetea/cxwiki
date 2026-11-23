# 脚本分类

## 构建、预览与部署：本目录

| 文件 | 用途 |
|---|---|
| `build_blog.py` | 从 Markdown 构建 `site/` |
| `check_blog.py` | 检查生成网页、链接与资源 |
| `check_wiki.py` | 检查知识库链接、ID 与图稿配对 |
| `preview_blog.py` | 本地预览，提供排序保存接口与视频范围请求 |
| `article_order.py` | 排序文件读写、稳定编号及导入 |
| `deploy_tx.sh` | 构建并部署到 tx；跳过相同 commit，成功后清理旧版本 |
| `blog.css`、`blog.js` | 博客样式与浏览器交互 |
| `vendor/` | 随站点分发的第三方资源 |

仓库根目录的 `build.sh` 是一键构建与预览入口。

## 文章制图：`figures/`

全部 `draw_*.py` 位于此处，包括公共绘图组件 `draw_foundations.py`、各专题 SVG／PNG 制图脚本以及 Transformer 动画生成脚本。生成的成品仍保存到 `wiki/imgs/`，不在脚本目录中输出。

从仓库根目录运行，例如：

```bash
python3 scripts/figures/draw_foundations.py --png
python3 scripts/figures/draw_diffusion_flow.py
```

制图所需环境与站点构建环境分开：根据具体脚本，需要 Matplotlib、Pillow、Playwright 与 Chromium；动画另需 ffmpeg。普通构建与部署不需要重运行这些脚本。
