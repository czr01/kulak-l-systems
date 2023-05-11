#!/bin/bash

# Change current directory to parent directory
cd "$(dirname "$0")/.."

# Set backup directory path
BACKUP_DIR=~/.l-systems/
# Set file path of history file
HISTORY_FILE="app/history.txt"

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
