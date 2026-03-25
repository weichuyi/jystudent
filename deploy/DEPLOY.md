# JYStudent 部署说明（针对 Ubuntu 20.04，公网访问）

概览：使用 systemd + Gunicorn + Nginx，静态文件由 Nginx 提供，Gunicorn 通过 unix socket 与 Nginx 通信。部署目录示例：`/opt/jystudent`。

关键点：
- 请替换 `app.py` 中的 `SECRET_KEY` 为强随机值，或通过环境变量注入。
- SQLite 适用于小规模部署；如并发或数据量增大，建议使用 PostgreSQL/MySQL。

快速步骤（在 VPS 上，root 或有 sudo 权限）：

1. 安装系统依赖
```
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git nginx ufw
```

2. 创建运行用户与目录
```
sudo useradd --system --group --no-create-home jystudent || true
sudo mkdir -p /opt/jystudent
sudo chown $USER:$USER /opt/jystudent
```

3. 传输代码（scp/rsync 或 git clone）到 `/opt/jystudent`。

4. 创建虚拟环境并安装依赖
```
cd /opt/jystudent
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
deactivate
```

5. 初始化数据库（在虚拟环境中运行）
```
source venv/bin/activate
python3 -c "from app import init_db; init_db()"
deactivate
```

6. 将 `deploy/jystudent.service` 复制到 `/etc/systemd/system/`，并按需修改 `WorkingDirectory` 与 `PATH`。
```
sudo cp deploy/jystudent.service /etc/systemd/system/jystudent.service
sudo systemctl daemon-reload
sudo systemctl enable --now jystudent.service
```

7. 将 `deploy/nginx_jystudent.conf` 复制到 `/etc/nginx/sites-available/jystudent`，修改 `server_name`，并启用：
```
sudo cp deploy/nginx_jystudent.conf /etc/nginx/sites-available/jystudent
sudo ln -s /etc/nginx/sites-available/jystudent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

8. 开放防火墙与云控制台端口（确保 80/443 可访问）
```
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

9. 启用 HTTPS（推荐）
```
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your.domain.com
```

排错提示：
- 查看 systemd 服务日志：`sudo journalctl -u jystudent.service -f`
- 查看 Nginx 日志：`sudo tail -F /var/log/nginx/error.log /var/log/nginx/access.log`
- 应用日志位于项目 `logs/error.log`（若存在）

安全建议：
- 不要在公网上使用默认 `DEFAULT_ADMIN_PASSWORD`，部署后立即修改管理员密码。
- 将 `SECRET_KEY` 存到系统环境或 `.env`，不要写在源码中。
- 考虑用 PostgreSQL 替代 SQLite 为生产数据库。
