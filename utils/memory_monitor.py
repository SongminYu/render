import csv
import psutil
import time


def monitor_python_memory_usage(interval=1):
    output_file = f'memory_usage_{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.csv'
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'memory_usage_gb', 'unit']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            python_memory_usage = 0
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                if 'python' in proc.info['name'].lower():
                    python_memory_usage += proc.info['memory_info'].rss
            memory_usage_gb = python_memory_usage / (1024 ** 3)
            print("Memory Usage by Python Processes: {:.2f} GB".format(memory_usage_gb))

            writer.writerow({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                'memory_usage_gb': round(memory_usage_gb, 3),
                'unit': 'GB'
            })

            time.sleep(interval)


if __name__ == "__main__":
    monitor_python_memory_usage()
