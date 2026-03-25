#!/usr/bin/env bash
set -euo pipefail

# 强制重装脚本（不可恢复）
# 用法示例：
#   sudo ./scripts/force_reinstall.sh
# 注意：脚本会删除 /srv/jystudent 的所有内容并重建，请在 VPS 环境中谨慎运行。

CONFIRM_PROMPT() {
  echo "警告：此操作将不可恢复地删除 /srv/jystudent 并覆盖所有内容。"
  read -p "若确认要继续请输入大写 YES：" ans
  if [ "$ans" != "YES" ]; then
    echo "已取消。"
    exit 1
  fi
}

if [ "${CI:-}" = "1" ]; then
  echo "CI 模式 - 跳过交互确认"
else
  CONFIRM_PROMPT
fi

# 停服务（忽略错误）
systemctl stop jystudent.service || true

# 删除旧项目（不可恢复）
rm -rf /srv/jystudent

# 克隆最新代码到 /srv/jystudent
git clone https://github.com/weichuyi/jystudent.git /srv/jystudent

# 设置属主为 www-data（安全）
chown -R www-data:www-data /srv/jystudent

# 创建并安装虚拟环境与依赖（以 www-data 身份运行）
# 注意：某些系统中 www-data 无法登录，使用 sudo -u 切换用户执行
sudo -u www-data bash -c '
  set -e
  cd /srv/jystudent
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  if [ -f requirements.txt ]; then
    pip install -r requirements.txt
  else
    pip install flask
  fi
  pip install gunicorn
'

# 写 systemd 单元（使用 127.0.0.1:8001，wsgi:app）
cat > /etc/systemd/system/jystudent.service <<'EOF'
[Unit]
Description=jystudent gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/srv/jystudent
Environment="PATH=/srv/jystudent/venv/bin"
ExecStart=/srv/jystudent/venv/bin/gunicorn -w 4 -b 127.0.0.1:8001 wsgi:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now jystudent.service

# 写 nginx 配置并启用（反代到 127.0.0.1:8001）
cat > /etc/nginx/sites-available/jystudent <<'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60;
        proxy_read_timeout 120;
    }
}
EOF

ln -sf /etc/nginx/sites-available/jystudent /etc/nginx/sites-enabled/jystudent
nginx -t && systemctl reload nginx

# 验证
echo "----- systemd status -----"
systemctl status jystudent.service --no-pager | sed -n '1,120p' || true

echo "----- 本机访问 -----"
curl -I http://127.0.0.1:8001 || true

echo "重装完成。"
