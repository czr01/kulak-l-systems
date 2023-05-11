#!/bin/bash

# Change current directory to parent directory
cd "$(dirname "$0")/.."

# Set backup directory path
BACKUP_DIR=~/.l-systems/
# Set file path of history file
HISTORY_FILE="app/history.txt"

# Check if backup directory does not exist, create it
if [ ! -d "$BACKUP_DIR" ]; then
mkdir "$BACKUP_DIR"
fi

# Generate the backup filename using current timestamp
BACKUP_FILENAME=history-$(date +"%Y-%m-%d-%H-%M-%S").txt.old

# Copy the history file to the backup directory with generated filename
cp "$HISTORY_FILE" "$BACKUP_DIR/$BACKUP_FILENAME"