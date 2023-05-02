#!/usr/bin/env bash

export LOG_LEVEL=${LOG_LEVEL:-"INFO"}

case $1 in
  "shell")
    bash
  ;;
  "export")
    echo "Run main.py"
    python main.py
  ;;
  *)
    echo "Please use of next parameters to start:"
    echo " help:   help information"
  ;;
esac