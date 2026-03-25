import os
import shutil
import sqlite3
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, 'instance', 'students.db')

if not os.path.exists(DB_PATH):
    print(f"数据库文件不存在: {DB_PATH}")
    raise SystemExit(2)

# 备份
bak_name = f"students.db.bak_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.bak"
bak_path = os.path.join(os.path.dirname(DB_PATH), bak_name)
shutil.copy2(DB_PATH, bak_path)
print(f"已备份数据库到: {bak_path}")

# 检查列是否存在
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
try:
    cur.execute("PRAGMA table_info(users);")
    cols = [r[1] for r in cur.fetchall()]
    if 'avatar' in cols:
        print('users 表已包含 avatar 列，跳过。')
    else:
        cur.execute("ALTER TABLE users ADD COLUMN avatar VARCHAR(255);")
        conn.commit()
        print('已为 users 表添加 avatar 列。')
finally:
    cur.close()
    conn.close()
