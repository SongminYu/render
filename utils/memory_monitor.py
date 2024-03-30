import psutil
import time


def monitor_python_memory_usage(interval=1):
    while True:
        python_memory_usage = 0
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            if 'python' in proc.info['name'].lower():
                python_memory_usage += proc.info['memory_info'].rss
        print("Memory Usage by Python Processes: {:.2f} GB".format(python_memory_usage / (1024 ** 3)))
        time.sleep(interval)


if __name__ == "__main__":
    monitor_python_memory_usage()

