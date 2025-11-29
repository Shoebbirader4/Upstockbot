#!/bin/bash
# Training script

echo "Starting model training..."

python -m model_training.train \
    --config config/config.yaml \
    --days 90

echo "Training completed!"
