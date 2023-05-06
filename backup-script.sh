#!/bin/bash

BACKUP_DIR=~/.l-systems/
HISTORY_FILE="./history.txt"

if [ ! -d "$BACKUP_DIR" ]; then
mkdir "$BACKUP_DIR"
fi

BACKUP_FILENAME=history-$(date +"%Y-%m-%d-%H-%M-%S").txt.old

cp "$HISTORY_FILE" "$BACKUP_DIR/$BACKUP_FILENAME"
