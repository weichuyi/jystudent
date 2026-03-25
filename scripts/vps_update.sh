#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash scripts/vps_update.sh
# Optional env overrides:
#   PROJECT_DIR=/opt/jystudent
#   REPO_URL=https://github.com/weichuyi/jystudent.git
#   VENV_PATH=/opt/jystudent/.venv
#   APP_MODULE=app:app
#   SERVICE_NAME=jystudent
#   BRANCH=main
#   DB_FILE=instance/students.db
#   BACKUP_DIR=/var/backups/jystudent
#   SKIP_RESTART=1
#   STAMP_HEAD_ONCE=1

PROJECT_DIR="${PROJECT_DIR:-/opt/jystudent}"
REPO_URL="${REPO_URL:-https://github.com/weichuyi/jystudent.git}"
VENV_PATH="${VENV_PATH:-$PROJECT_DIR/.venv}"
APP_MODULE="${APP_MODULE:-app:app}"
SERVICE_NAME="${SERVICE_NAME:-jystudent}"
BRANCH="${BRANCH:-main}"
DB_FILE="${DB_FILE:-instance/students.db}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/jystudent}"
SKIP_RESTART="${SKIP_RESTART:-0}"
STAMP_HEAD_ONCE="${STAMP_HEAD_ONCE:-0}"

log() {
  printf "[%s] %s\n" "$(date '+%F %T')" "$*"
}

fail() {
  log "ERROR: $*"
  exit 1
}

command -v git >/dev/null 2>&1 || fail "git is required"
command -v python3 >/dev/null 2>&1 || fail "python3 is required"

if [ ! -d "$PROJECT_DIR" ]; then
  log "Project directory not found, cloning repository"
  mkdir -p "$(dirname "$PROJECT_DIR")"
  git clone "$REPO_URL" "$PROJECT_DIR"
fi

[ -d "$PROJECT_DIR/.git" ] || fail "Not a git repository: $PROJECT_DIR"

cd "$PROJECT_DIR"

if [ ! -x "$VENV_PATH/bin/python" ]; then
  log "Virtual environment not found, creating: $VENV_PATH"
  python3 -m venv "$VENV_PATH"
fi

if [ -f "$DB_FILE" ]; then
  mkdir -p "$BACKUP_DIR"
  DB_BASENAME="$(basename "$DB_FILE")"
  BACKUP_PATH="$BACKUP_DIR/${DB_BASENAME%.db}_$(date +%F_%H%M%S).db"
  cp -a "$DB_FILE" "$BACKUP_PATH"
  log "Database backup created: $BACKUP_PATH"
else
  log "Database file not found, skip backup: $DB_FILE"
fi

log "Sync code from origin/$BRANCH"
git fetch origin "$BRANCH"
git pull --rebase origin "$BRANCH"

log "Install dependencies"
"$VENV_PATH/bin/python" -m pip install --upgrade pip
"$VENV_PATH/bin/pip" install -r requirements.txt

export FLASK_APP="$APP_MODULE"

if [ "$STAMP_HEAD_ONCE" = "1" ]; then
  log "Stamp migration head (first-time migration bootstrap)"
  "$VENV_PATH/bin/flask" db stamp head
fi

log "Run migration upgrade"
"$VENV_PATH/bin/flask" db upgrade

if [ "$SKIP_RESTART" = "1" ]; then
  log "Skip service restart (SKIP_RESTART=1)"
else
  log "Restart service: $SERVICE_NAME"
  sudo systemctl restart "$SERVICE_NAME"
  sudo systemctl --no-pager status "$SERVICE_NAME" | sed -n '1,12p'
fi

log "Update completed successfully"
