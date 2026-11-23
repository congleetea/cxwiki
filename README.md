# cxwiki：个人知识库

中文个人知识库，按“主题 → 概念 / 综述 → 文章目录 → 文章”阅读。Markdown 是正文源文件，HTML 是生成的阅读版。论文保存在本地，可以直接打开和批注。

## Ubuntu 一键生成与预览

在仓库根目录打开终端运行：

```bash
bash build.sh
```

脚本会准备 Python 3.10+、仓库内 `.venv` 虚拟环境与网页依赖，然后生成网页并检查链接和图片。若 Ubuntu 缺少系统组件，会通过 `sudo apt-get` 安装 `python3`、`python3-venv`，可能要求输入登录密码；以普通用户运行整个脚本即可。若机器已有 `uv`，也可以用它创建环境而不需要 sudo，脚本不会额外安装 uv。

再次运行相同命令会复用环境，跳过已完成的安装；依赖清单变动或依赖缺失时重新安装。**网页每次都会重新生成**，以包含最新的 Markdown、图片和样式。安装失败不会标为成功，修复网络或权限后直接重试。无需手动激活虚拟环境，也无需安装绘图、GPU 或 Node.js 依赖。

生成后可以双击`site/index.html`。更推荐启动本地预览：

```bash
bash build.sh --serve
```

在浏览器访问 <http://127.0.0.1:8000/>，按 `Ctrl+C` 停止。端口被占用时指定其他端口：

```bash
bash build.sh --serve --port 8080
```

预览服务仅监听本机地址，提供 `site/` 目录。完整 `site/` 可独立部署。后续编辑文章后重新执行脚本，再刷新浏览器；脚本不会监听文件自动重建。

环境损坏或搬动仓库后虚拟环境不可用时，可先把 `.venv` 改名备份，再运行脚本创建新环境。查看参数：`bash build.sh --help`。如需指定其他 Python，可运行 `CXWIKI_PYTHON=/path/to/python3 bash build.sh`。

## 手动安装与生成

需要 Python 3.10 或更新版本。以下命令都在仓库根目录执行，不需要安装机器人训练环境、Node.js 或 GPU 依赖。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_blog.py
```

Windows 激活虚拟环境使用 `.venv\Scripts\activate`。以后每次使用新终端时，先激活环境。

生成完成后直接用浏览器打开`site/index.html`，或启动本地静态服务：

```bash
python scripts/preview_blog.py --port 8000
```

然后访问 <http://127.0.0.1:8000/>，按 `Ctrl+C` 停止服务。该服务支持拖动排序保存到本机仓库；跨电脑同步仍需提交、推送排序文件。

## 修改文章

1. 编辑 `wiki/00-concepts/` 或 `wiki/01-comprehensive/` 下的 `.md` 文件。
2. 运行 `python scripts/build_blog.py`。
3. 刷新浏览器；如果样式仍旧，使用强制刷新。

不要直接编辑 `site/` 中生成的 HTML：构建会重新创建 `site/`，覆盖这些文件。在 HTML 页面点击“编辑、保存”并同步 Markdown 的功能目前尚未实现。

文章 frontmatter 可以填写标题、稳定 ID、日期、标签和 `institution`（主体机构）。同系列使用稳定 ASCII 前缀，例如 `pi-*`、`nvidia-*`；中文标题保留在正文。新增文章后维护 `wiki/_index.md`，运行生成器即可更新主题文章目录。新主题会生成分类页；当前顶部导航仍需在 `scripts/build_blog.py` 中添加入口和中文名称。

## 修改布局与交互

| 文件 | 负责内容 |
| --- | --- |
| `scripts/build_blog.py` | 分类、目录、文章结构及本地链接转换 |
| `scripts/blog.css` | 字体、配色、正文宽度、左侧大纲和手机布局 |
| `scripts/blog.js` | 公式渲染、大纲高亮和目录排序 |

改完上述文件后同样运行生成器。KaTeX 脚本、字体和样式已随仓库保存，公式排版不需要联网。

构建时会把所有文章的当前顺序写入排序文件；后续新增文章默认放在已保存文章之前，已有文章保持原顺序。文件按文章 ID 保存稳定编号，编号越大越靠前；新增文章使用更大的编号，拖动通常只改一个编号，插入中间时取相邻编号的中值。目录顺序保存到仓库的 `site/article-order.json`，随 Git 同步，生成后的静态站点会使用该顺序。

### 拖动后自动固定顺序

用 `bash build.sh --serve` 打开博客，拖动文章靠近窗口顶部或底部时会自动滚动，松手后会自动保存到仓库并重新生成网页，页面显示“已保存到 site/article-order.json”，无需点击其他按钮。页面加载时直接读取该文件；重新构建也会保留它，不再使用浏览器缓存保存排序。

生成的 `site/` 已包含固定顺序，可直接部署。其他电脑使用源码生成时，将 `site/article-order.json` 随 Git 同步即可。纯静态文件无法写回仓库，因此调整顺序请使用上述本地预览入口。

## 本地论文与图片

- `raw/papers/` 是论文原件目录。批注或编辑这里的 PDF，再构建即可更新站点阅读副本。
- `site/raw/papers/` 是自动复制的论文，直接编辑这里会被下次构建覆盖。
- 文章引用本地材料时使用相对路径；未归档的材料继续保留在线引用。
- 图片放在 `wiki/imgs/`，技术图保留 SVG 源文件及 PNG 阅读图，不使用 Excalidraw。

已有图片不需要重新生成。需要运行绘图脚本时，可选安装：

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
```

基础概念图可用 `python scripts/figures/draw_foundations.py --png` 重绘。图内公式使用 LaTeX 数学语法，排版为 SVG 矢量路径后导出 PNG，不依赖阅读端安装公式字体；中文排版使用 Noto Sans CJK 字体。

## 检查与提交

```bash
python scripts/build_blog.py
python scripts/check_wiki.py
python scripts/check_blog.py
git status --short
```

检查器验证链接、图片、页面 ID 和代码证据快照；技术结论仍需核对论文，检查通过不表示复现实验成功。

提交文章源文件、原始材料、图片、脚本、依赖清单、说明及 `.agents/skills/`。生成站点、首页、缓存、虚拟环境和本地实施计划由 `.gitignore` 排除；它们仍可以保留在本机。

`raw/codes/` 只提交 `.gitkeep` 以保留目录，不提交代码仓库或快照；可按需自行下载。本地没有代码时，生成页面保留引用文字并提示“本地代码未下载”，不影响文章阅读与构建。已有快照存在时仍检查其文件哈希。

```bash
git add .
git diff --cached --stat
git commit -m "更新知识库内容"
```

论文原件体积较大，是离线阅读和个人批注所需材料，因此保留在 Git；构建副本不重复提交。完整 `site/` 可单独用于静态部署，当前没有自动部署流程。

## 目录与 skill

```text
.agents/skills/wiki/SKILL.md  仓库版写作与维护约定
AGENTS.md                   仓库工作约定
wiki/00-concepts/            概念文章
wiki/01-comprehensive/       主题综述
wiki/imgs/                  图片和矢量图源文件
wiki/logs/                  更新记录
raw/                        论文、网页和代码证据
scripts/                    生成器、样式、交互和检查工具
site/                       构建结果（不提交）
```

[仓库版 wiki skill](.agents/skills/wiki/SKILL.md) 随 Git 保存。本机 `~/.codex/skills/wiki/` 是安装副本；其他电脑如需安装，可将仓库版复制到自己的 Codex skills 目录。skill 中 ingest、absorb 等是工作类型标签，不是终端命令。

## 云端阅读站点

`tx` 的部署、访问认证和更新步骤见 [部署记录](deploy/README.md)。后续更新运行 `bash scripts/deploy_tx.sh`。

脚本职责与文章制图目录见 [scripts/README.md](scripts/README.md)。
