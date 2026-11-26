# cxwiki 网页项目

所有网页相关的源码、依赖、测试、预览和部署配置都位于本目录。文章输入来自仓库的 `wiki/` 与 `raw/`；文章制图工具位于 `scripts/figures/`，不参与普通网页构建。

## 生成和预览

以下命令从仓库根目录运行：

```bash
bash site/build.sh
bash site/build.sh --serve
```

一键脚本准备 Python 3.10+ 与 `site/.venv/`，安装 `site/requirements.txt` 后生成并校验网页。环境已有依赖时跳过安装；缺少 Ubuntu 系统组件时仍可能需要 sudo。端口可用 `--port 8080` 指定。

阅读入口为 `site/public/index.html`。推荐打开预览服务 http://127.0.0.1:8000/，支持拖动排序保存和视频范围请求。直接打开本地 HTML 或静态站点也支持拖动排序；浏览器会保存顺序，写回仓库文件需点击保存按钮。

```text
site/
├── build.sh               一键构建与预览
├── requirements.txt       网页构建依赖
├── requirements-dev.txt   浏览器测试依赖
├── article-order.json     排序源数据（Git 跟踪）
├── scripts/               生成、检查、预览、部署、样式及前端资源
├── tests/                 网页回归测试
├── deploy/                Nginx 配置与部署说明
└── public/                生成的独立站点（Git 忽略，可部署）
```

构建只重新创建 `public/`，不会删除源码、配置和排序源数据。不要编辑 public 中的文章、样式和 PDF，它们下次构建会被覆盖。PDF 原件编辑位置仍为仓库的 `raw/papers/`。

## 文章与布局

文章源文件见 [wiki 编辑索引](../wiki/_index.md)。`published` 保存首次公开日期，目录仅显示年和月；`last_updated` 表示知识库文章更新日期，不能替代论文发布日期。`institution` 填具体机构；“综述”“多机构”等占位值不显示。

修改布局使用 `site/scripts/build_blog.py`，样式使用 `site/scripts/blog.css`，浏览器交互使用 `site/scripts/blog.js`。第三方静态资源保存在 `site/scripts/vendor/`，确保公式可以离线阅读。

## 目录顺序

排序只以 `site/article-order.json` 为源数据，形式为“目录 → 文章 ID → 数字”。编号大的在上、小的在下；新增文章使用更大的编号，已有编号不变。拖动通常仅修改被移动文章的编号，插入中间时取相邻编号的中值。

本地预览中拖动文章靠近窗口边缘会自动滚动；松手后保存排序文件并重新生成网页。只保留 `site/article-order.json` 一份排序文件；预览直接通过接口读取和保存它，生成的静态 HTML 已按该文件排序，不再复制 JSON。直接打开 HTML 或访问静态 HTTP/HTTPS 网站时，拖动顺序自动保存在当前浏览器，刷新和返回目录仍有效。点击“保存到排序文件”，在支持本地文件访问的浏览器（如 Chromium）中选择唯一的 `site/article-order.json`，即可合并修改；不支持文件选择写入的浏览器会导出临时修改补丁，用 `python3 site/scripts/article_order.py 路径/article-order-changes.json` 合并到源文件。跨电脑同步需提交、推送排序源文件，另一台电脑拉取后重新构建。

## 检查

```bash
site/.venv/bin/python -m unittest discover -s site/tests
python3 site/tests/browser_drag_scroll.py
python3 site/tests/browser_file_order.py
```

浏览器回归脚本需要 Playwright 和 Chromium，普通构建无需安装绘图环境。可在 site 虚拟环境安装 `site/requirements-dev.txt` 并运行 `playwright install chromium`。

## 发布

```bash
bash site/scripts/deploy_tx.sh
```

仅上传 `site/public/`。相同 commit 跳过；新版本上传并切换成功后删除旧版本。整站密码认证与 HTTPS 由服务器 Nginx 提供，详见 [部署记录](deploy/README.md)。
