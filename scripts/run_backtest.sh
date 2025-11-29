#!/bin/bash
# Backtest script

if [ -z "$1" ]; then
    echo "Usage: ./run_backtest.sh <model_path>"
    exit 1
fi

MODEL_PATH=$1

echo "Running backtest with model: $MODEL_PATH"

python -m backtester.run_backtest \
    --config config/config.yaml \
    --model "$MODEL_PATH" \
    --days 30

echo "Backtest completed!"
