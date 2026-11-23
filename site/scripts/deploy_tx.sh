#!/usr/bin/env bash
# Update the already configured, password-protected cxwiki site on tx.
set -Eeuo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$repo_dir"
commit_id="$(git rev-parse --verify HEAD)"
deployed_commit="$(ssh -o BatchMode=yes tx 'if test -s /var/www/cxwiki/current/index.html && test -f /var/www/cxwiki/current/.deploy-commit; then cat /var/www/cxwiki/current/.deploy-commit; fi')"
if [[ "$commit_id" == "$deployed_commit" ]]; then
    printf 'tx 已部署 commit %s，跳过构建和部署。\n' "$commit_id"
    if [[ -n "$(git status --porcelain)" ]]; then
        printf '本地有未提交改动；如需发布，请先提交形成新的 commit。\n'
    fi
    exit 0
fi
bash build.sh
release_id="$(date -u +%Y%m%d-%H%M%S)"
release_path="/var/www/cxwiki/releases/$release_id"
ssh -o BatchMode=yes tx "sudo -n nginx -t && sudo -n test -s /etc/nginx/cxwiki.htpasswd && sudo -n mkdir '$release_path' && sudo -n chown ubuntu:ubuntu '$release_path'"
rsync -az --no-owner --no-group --chmod=D755,F644 \
    --link-dest=/var/www/cxwiki/current --info=stats2 \
    public/ "tx:$release_path/"
ssh -o BatchMode=yes tx "test -s '$release_path/index.html' && printf '%s\\n' '$commit_id' > '$release_path/.deploy-commit' && sudo -n ln -s '$release_path' '/var/www/cxwiki/current.next-$release_id' && sudo -n mv -Tf '/var/www/cxwiki/current.next-$release_id' /var/www/cxwiki/current"
ssh -o BatchMode=yes tx "test \"\$(readlink -f /var/www/cxwiki/current)\" = '$release_path' && sudo -n find /var/www/cxwiki/releases -mindepth 1 -maxdepth 1 -type d ! -path '$release_path' -exec rm -rf -- {} +"
printf '已更新 tx：%s\n访问：https://43.138.240.151/\n' "$release_path"
