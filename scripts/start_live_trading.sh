#!/bin/bash
# Start live trading

if [ -z "$1" ]; then
    echo "Usage: ./start_live_trading.sh <model_path> [paper|live]"
    exit 1
fi

MODEL_PATH=$1
MODE=${2:-paper}

echo "Starting trading bot in $MODE mode..."
echo "Model: $MODEL_PATH"
echo "Press Ctrl+C to stop"

python main.py \
    --config config/config.yaml \
    --model "$MODEL_PATH" \
    --mode "$MODE"
