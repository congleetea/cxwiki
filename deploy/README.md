# tx 部署记录

2026-11-23 已通过 SSH 主机别名 `tx` 部署当前工作区生成的 `site/`，包含网页、图示、视频与本地论文。后续更新以本地 Git HEAD 为版本标识，请先提交要发布的改动。

- 服务器：`ubuntu@43.138.240.151`，Ubuntu 22.04。
- 阅读地址：`https://43.138.240.151/`。
- 服务：Nginx，已启用开机启动。
- 页面目录：`/var/www/cxwiki/current`，指向 `releases/` 中的具体版本。
- 配置：`/etc/nginx/sites-available/cxwiki`，本仓库模板为 `cxwiki.nginx.conf`。
- 整站使用 HTTP Basic 用户认证，密码通过 HTTPS 传送。口令哈希存于服务器 `/etc/nginx/cxwiki.htpasswd`，不纳入仓库；用户名为 `cxwiki`，初始密码通过会话交付。
- 临时证书：`/etc/nginx/ssl/cxwiki.crt`，私钥 `/etc/nginx/ssl/cxwiki.key`。这是 IP 自签名证书，浏览器初次访问会提示不受信任；取得域名后应配置对应域名和可信证书。
- 云安全组/云防火墙需放行入站 TCP 443；TCP 80 用于跳转到 HTTPS。

## 更新

本机运行：

```bash
bash scripts/deploy_tx.sh
```

脚本先比较本地 HEAD 与远端当前版本的 `.deploy-commit`；相同则直接跳过，不构建、不上传、不创建新目录。未提交改动不会绕过这个判断，如需发布请先提交。远端没有版本标记时正常部署一次。

需要部署时，脚本重新构建并校验本地网页，再上传到新版本目录；上传成功后写入该版本的 `.deploy-commit`，再原子切换 `current` 软链接；上传失败不会修改当前线上版本或其 commit 标记。使用 rsync 硬链接复用上一版本未变的文件，避免每次重传全部论文。切换成功并确认 current 指向新版本后，自动删除 releases 下其他旧版本目录，仅保留当前版本以节省空间。构建或上传失败时不清理旧版本。

脚本用于更新已配置服务器，不安装 Nginx、不生成密码、不更改认证设置。部署前保证本机 SSH 别名 `tx` 可用，远端 `ubuntu` 可无交互执行所需 sudo 命令。

## 排序与编辑

服务器目前提供受密码保护的静态阅读站点，不开放预览服务的写入 API。排序在本机通过 `bash build.sh --serve` 调整并保存到 `site/article-order.json`，再执行部署脚本。云端直接拖动不能写回服务器文件。

## 检查

```bash
ssh tx 'sudo nginx -t && systemctl is-active nginx'
ssh tx 'readlink /var/www/cxwiki/current'
ssh tx 'ls /var/www/cxwiki/releases'
```

由于只保留当前版本，如需恢复历史内容，应切换到对应 Git commit 后重新部署；认证配置保存在 releases 目录之外，不受版本清理影响。Nginx 日志位于 `/var/log/nginx/access.log` 和 `error.log`。

首次部署验证：服务器内未认证首页、文章及 PDF 为 401；认证后首页和文章为 200，PDF 范围请求为 206。用户放行云端端口后，已从本机公网验证：HTTP 301 跳转 HTTPS；匿名 HTTPS 返回 401；指定新密码后首页与文章返回 200，匿名 PDF 返回 401。
