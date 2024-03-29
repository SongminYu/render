#!/bin/bash

while true; do
    total_memory=$(ps aux | grep '[p]ython' | awk '{sum += $6} END {print sum}')
    total_memory_mb=$(echo "scale=2; $total_memory / 1024" | bc)
    echo "Total memory usage of Python processes: $total_memory_mb MB"
    sleep 1  # Adjust the sleep interval as needed
done
