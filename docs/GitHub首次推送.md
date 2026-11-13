# 首次推送（由用户执行）

2026-11-13 检查：本地项目尚未初始化 Git，远程仓库未返回分支。助手未执行 git commit 或 git push。下列命令在远程服务器执行；先用 ssh root@yrdb1465843.bohrium.tech 登录。

```bash
cd /personal/DPcompetition/poreva-open-2026
git init -b main
git config user.name "LynnChrisleetop"
read -rp "请输入你的 GitHub 提交邮箱: " commit_email
git config user.email "$commit_email"
git remote add origin git@github.com:LynnChrisleetop/CMP-poreva-2026.git
git add .
git status --short
git diff --cached --stat
git commit -m "Initialize Poreva competition project and repaired BindCraft image configuration"
git push -u origin main
```

检查暂存列表后再执行 commit/push。环境、权重、安装包、镜像归档、私有报名资料、机器运行记录已在 .gitignore 中排除。初步检查没有发现超过 50 MiB 的候选文件或常见密钥格式，但用户仍应复核拟公开内容。

若 push 报 Permission denied (publickey)，表示服务器尚未配置有仓库权限的 GitHub SSH 密钥。可先配置服务器的 GitHub SSH 访问，也可用下面的命令切换 HTTPS，再使用 GitHub 支持的凭据认证；普通账号密码不能用于 Git 推送：

```bash
git remote set-url origin https://github.com/LynnChrisleetop/CMP-poreva-2026.git
git push -u origin main
```

如果远程仓库后来已经有提交，不要使用 force push；先检查 git ls-remote origin，再决定如何合并。
