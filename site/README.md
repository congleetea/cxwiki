# cxwiki 网页项目

所有网页相关的源码、依赖、测试、预览和部署配置都位于本目录。文章输入来自仓库的 `wiki/` 与 `raw/`；文章制图工具位于 `scripts/figures/`，不参与普通网页构建。

## 生成和预览

以下命令从仓库根目录运行：

```bash
bash site/build.sh
bash site/build.sh --serve
```

一键脚本准备 Python 3.10+ 与 `site/.venv/`，安装 `site/requirements.txt` 后生成并校验网页。环境已有依赖时跳过安装；缺少 Ubuntu 系统组件时仍可能需要 sudo。端口可用 `--port 8080` 指定。

阅读入口为 `site/public/index.html`。推荐打开预览服务 http://127.0.0.1:8000/，支持拖动排序保存和视频范围请求。纯静态页面仅支持阅读，不能写回文件。

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

本地预览中拖动文章靠近窗口边缘会自动滚动；松手后保存排序文件并重新生成网页。生成器把最新排序复制到 `site/public/article-order.json`，浏览器从站点根目录读取副本。跨电脑同步需提交、推送排序源文件，另一台电脑拉取后重新构建。

## 检查

```bash
site/.venv/bin/python -m unittest discover -s site/tests
python3 site/tests/browser_drag_scroll.py
```

浏览器回归脚本需要 Playwright 和 Chromium，普通构建无需安装绘图环境。可在 site 虚拟环境安装 `site/requirements-dev.txt` 并运行 `playwright install chromium`。

## 发布

```bash
bash site/scripts/deploy_tx.sh
```

仅上传 `site/public/`。相同 commit 跳过；新版本上传并切换成功后删除旧版本。整站密码认证与 HTTPS 由服务器 Nginx 提供，详见 [部署记录](deploy/README.md)。
