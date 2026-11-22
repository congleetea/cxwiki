#!/usr/bin/env bash
# Ubuntu setup, repeatable site generation, and optional local preview.
set -Eeuo pipefail
trap 'printf "\n失败：第 %s 行执行失败。修复上方错误后，重新运行本脚本即可。\n" "$LINENO" >&2' ERR

usage() {
    cat <<'EOF'
用法：bash build.sh [--serve] [--port 8000]

首次运行自动准备 Python 虚拟环境和网页依赖，然后生成并检查网页。
再次运行复用环境；依赖清单变化或依赖缺失时才重新安装。

  --serve       生成后启动预览：http://127.0.0.1:8000/（Ctrl+C 停止）
  --port PORT   预览端口，默认 8000
  -h, --help    显示帮助

Ubuntu 缺少 Python 或 venv 时会用 sudo apt-get 安装所需系统组件。
若已装有 uv，则可用它创建环境，无需 sudo；脚本不会额外安装 uv。
请以普通用户运行，勿用 sudo 执行整个脚本。
构建会重新创建 site/，请编辑 wiki/ 中的源文章。
EOF
}
serve=0
port=8000
while (($#)); do
    case "$1" in
        --serve) serve=1; shift ;;
        --port)
            if (($# < 2)); then printf '缺少端口参数。\n' >&2; exit 2; fi
            port="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) printf '未知参数：%s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
done
if [[ ! "$port" =~ ^[0-9]{1,5}$ ]] || ((10#$port < 1 || 10#$port > 65535)); then
    printf '端口必须为 1–65535 的整数。\n' >&2
    exit 2
fi
port=$((10#$port))
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$repo_dir"
# A sourced ROS/Conda shell must not inject unrelated packages into this venv.
unset PYTHONPATH PYTHONHOME
python_bin="${CXWIKI_PYTHON:-python3}"
venv_dir="$repo_dir/.venv"

install_system_python() {
    if [[ -n "${CXWIKI_PYTHON:-}" ]]; then
        printf '指定的 CXWIKI_PYTHON 不可用或缺少 venv / ensurepip，请修复该解释器。\n' >&2
        exit 1
    fi
    if ! command -v apt-get >/dev/null; then
        printf '请先安装 Python 3.10+ 及 venv 支持，再重新运行。\n' >&2
        exit 1
    fi
    local -a elevate=()
    if ((EUID != 0)); then
        if ! command -v sudo >/dev/null; then
            printf '系统缺少依赖且没有 sudo；请管理员安装 python3 python3-venv。\n' >&2
            exit 1
        fi
        elevate=(sudo)
    fi
    printf '安装缺少的系统组件（可能需要输入 Ubuntu 登录密码）……\n'
    "${elevate[@]}" apt-get update
    "${elevate[@]}" apt-get install -y python3 python3-venv
}

if ! command -v "$python_bin" >/dev/null; then
    install_system_python
fi
if ! "$python_bin" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    printf '需要 Python 3.10+。请升级 Ubuntu/Python，或用 CXWIKI_PYTHON 指定解释器。\n' >&2
    exit 1
fi

if [[ ! -x "$venv_dir/bin/python" ]]; then
    printf '创建虚拟环境：%s\n' "$venv_dir"
    if "$python_bin" -c 'import venv, ensurepip' 2>/dev/null; then
        "$python_bin" -m venv "$venv_dir"
    elif command -v uv >/dev/null; then
        # Existing uv can seed a venv without Ubuntu's ensurepip package.
        uv venv --python "$(command -v "$python_bin")" --seed "$venv_dir"
    else
        install_system_python
        "$python_bin" -m venv "$venv_dir"
    fi
else
    printf '复用已有虚拟环境。\n'
fi
venv_python="$venv_dir/bin/python"
if ! "$venv_python" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    printf '.venv 无法运行或版本过旧。请将其移走，再重新执行以创建新环境。\n' >&2
    exit 1
fi

requirements_hash="$(sha256sum requirements.txt)"
requirements_hash="${requirements_hash%% *}"
stamp="$venv_dir/.cxwiki-requirements.sha256"
dependencies_ready() {
    [[ -f "$stamp" ]] && [[ "$(cat -- "$stamp")" == "$requirements_hash" ]] || return 1
    "$venv_python" - <<'PY'
from importlib.metadata import version
import mistune
import yaml
assert version('mistune') == '3.1.2'
assert 6 <= int(version('PyYAML').split('.')[0]) < 7
PY
}
if dependencies_ready; then
    printf '网页依赖已就绪，跳过安装。\n'
else
    printf '安装／更新网页依赖……\n'
    "$venv_python" -m pip install -r requirements.txt
    "$venv_python" -m pip check
    printf '%s\n' "$requirements_hash" > "$stamp"
fi

printf '\n生成网页……\n'
"$venv_python" scripts/build_blog.py
"$venv_python" scripts/check_blog.py
"$venv_python" scripts/check_wiki.py
printf '\n完成！首页：%s/index.html\n独立部署目录：%s/site/\n' "$repo_dir" "$repo_dir"
if ((serve)); then
    printf '\n预览：http://127.0.0.1:%s/\n按 Ctrl+C 停止服务。\n' "$port"
    exec "$venv_python" scripts/preview_blog.py --port "$port"
fi
printf '\n需要本地预览时运行：bash build.sh --serve\n'
