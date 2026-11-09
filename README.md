# cxwiki：个人知识库

中文个人知识库，按“主题 → 概念 / 综述 → 文章目录 → 文章”阅读。Markdown 是正文源文件，HTML 是生成的阅读版。论文保存在本地，可以直接打开和批注。

## 首次安装与生成

需要 Python 3.10 或更新版本。以下命令都在仓库根目录执行，不需要安装机器人训练环境、Node.js 或 GPU 依赖。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_blog.py
```

Windows 激活虚拟环境使用 `.venv\Scripts\activate`。以后每次使用新终端时，先激活环境。

生成完成后直接用浏览器打开根目录 `index.html`，或启动本地静态服务：

```bash
python -m http.server 8000 --bind 127.0.0.1
```

然后访问 <http://127.0.0.1:8000/>，按 `Ctrl+C` 停止服务。该服务只供阅读，尚不支持网页保存文章。

## 修改文章

1. 编辑 `wiki/00-concepts/` 或 `wiki/01-comprehensive/` 下的 `.md` 文件。
2. 运行 `python scripts/build_blog.py`。
3. 刷新浏览器；如果样式仍旧，使用强制刷新。

不要直接编辑 `site/` 或生成的 `index.html`：构建会重新创建 `site/`，覆盖这些文件。在 HTML 页面点击“编辑、保存”并同步 Markdown 的功能目前尚未实现。

文章 frontmatter 可以填写标题、稳定 ID、日期、标签和 `institution`（主体机构）。同系列使用稳定 ASCII 前缀，例如 `pi-*`、`nvidia-*`；中文标题保留在正文。新增文章后维护 `wiki/_index.md`，运行生成器即可更新主题文章目录。新主题会生成分类页；当前顶部导航仍需在 `scripts/build_blog.py` 中添加入口和中文名称。

## 修改布局与交互

| 文件 | 负责内容 |
| --- | --- |
| `scripts/build_blog.py` | 分类、目录、文章结构及本地链接转换 |
| `scripts/blog.css` | 字体、配色、正文宽度、左侧大纲和手机布局 |
| `scripts/blog.js` | 公式渲染、大纲高亮和目录排序 |

改完上述文件后同样运行生成器。KaTeX 脚本、字体和样式已随仓库保存，公式排版不需要联网。

目录拖拽顺序保存在当前浏览器的本地存储中，不写回 Git 或 Markdown。清除浏览器数据、换浏览器或切换访问地址后不保证保留该顺序。

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
