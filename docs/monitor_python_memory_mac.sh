while true; do
    total_memory=$(ps aux | grep '[P]ython' | awk '{sum += $6} END {print sum}')
    echo "Total memory usage of Python processes: $total_memory KB"
    sleep 1  # Adjust the sleep interval as needed
done
