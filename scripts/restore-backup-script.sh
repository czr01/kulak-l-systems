#!/bin/bash

cd "$(dirname "$0")/.."

HISTORY_FILE="app/history.txt"
BACKUP_DIR=~/.l-systems/

if [ ! -d "$BACKUP_DIR" ]; then
  echo "Backup directory not found."
  exit 1
fi

BACKUPS=$(ls "$BACKUP_DIR" | grep -E "^history-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}.txt.old$")

if [ -z "$BACKUPS" ]; then
  echo "No backups found in $BACKUP_DIR."
  exit 1
fi

echo "Available backups:"
echo $BACKUPS

read -p "Which backup do you want to restore? (Enter the filename): " BACKUP_FILENAME

if [ ! -f "$BACKUP_DIR/$BACKUP_FILENAME" ]; then
  echo "Backup file not found."
  exit 1
fi

cp "$BACKUP_DIR/$BACKUP_FILENAME" "$HISTORY_FILE"
