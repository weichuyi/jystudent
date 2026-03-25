#!/usr/bin/env bash
set -euo pipefail

# 安装脚本（在 VPS 上以 root 或 sudo 运行）
# 用法示例：
# 1) 如果代码已经在 /opt/jystudent：直接运行脚本
#    sudo bash install_on_ubuntu20.sh
# 2) 从本地运行并将仓库上传并执行：
#    tar -czf jystudent.tar.gz . && scp jystudent.tar.gz root@YOUR_HOST:/tmp
#    ssh root@YOUR_HOST 'cd /tmp && tar -xzf jystudent.tar.gz -C /opt && bash /opt/jystudent/deploy/install_on_ubuntu20.sh'

REPO_DIR="/opt/jystudent"
VENV_DIR="$REPO_DIR/venv"
SERVICE_FILE="/etc/systemd/system/jystudent.service"
NGINX_AVAILABLE="/etc/nginx/sites-available/jystudent"

echo "更新 apt 并安装依赖..."
apt update
apt install -y python3 python3-venv python3-pip git nginx ufw curl

echo "创建运行用户（如果不存在）..."
id -u jystudent >/dev/null 2>&1 || useradd --system --group --no-create-home jystudent || true

if [ ! -d "$REPO_DIR" ]; then
  echo "错误：未找到代码目录 $REPO_DIR。请先把项目放到该目录，或修改脚本的 REPO_DIR 变量。"
  exit 1
fi

echo "设置目录权限..."
chown -R $(whoami):$(whoami) "$REPO_DIR"

echo "创建虚拟环境并安装 Python 依赖..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip wheel
if [ -f "$REPO_DIR/requirements.txt" ]; then
  pip install -r "$REPO_DIR/requirements.txt"
else
  echo "警告：未找到 requirements.txt，跳过 pip 安装。"
fi
deactivate

echo "初始化数据库（SQLite）..."
source "$VENV_DIR/bin/activate"
python3 -c "from app import init_db; init_db()"
deactivate

echo "部署 systemd 服务文件..."
if [ -f "$REPO_DIR/deploy/jystudent.service" ]; then
  cp "$REPO_DIR/deploy/jystudent.service" "$SERVICE_FILE"
  sed -i "s|WorkingDirectory=.*|WorkingDirectory=$REPO_DIR|" "$SERVICE_FILE" || true
  sed -i "s|Environment=\"PATH=.*\"|Environment=\"PATH=$VENV_DIR/bin\"|" "$SERVICE_FILE" || true
  systemctl daemon-reload
  systemctl enable --now jystudent.service
else
  echo "未找到 deploy/jystudent.service，跳过 systemd 安装。"
fi

echo "配置 Nginx 站点..."
if [ -f "$REPO_DIR/deploy/nginx_jystudent.conf" ]; then
  cp "$REPO_DIR/deploy/nginx_jystudent.conf" "$NGINX_AVAILABLE"
  ln -sf "$NGINX_AVAILABLE" /etc/nginx/sites-enabled/jystudent
  nginx -t
  systemctl restart nginx
else
  echo "未找到 deploy/nginx_jystudent.conf，跳过 Nginx 配置。"
fi

echo "打开防火墙（SSH 和 Nginx）..."
ufw allow OpenSSH || true
ufw allow 'Nginx Full' || true
ufw --force enable || true

echo "部署完成。请访问服务器公网 IP 或配置域名并为 Nginx 启用 HTTPS。"
echo "重要安全提示：请立即更改默认管理员密码并将 SECRET_KEY 设为随机值（可通过环境变量或配置文件）。"
