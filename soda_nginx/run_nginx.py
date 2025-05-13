import subprocess
import threading
import time
import os
import signal  # For more robust signal handling
from pathlib import Path


CR = Path(__file__).parent
bindir = CR.parent.joinpath('soda_nginx_bin')
nginx_path = bindir.joinpath('nginx.exe')  # Replace with your actual path


def monitor_access_log_daemon(log_file_path, stop_event):
    # Same log monitoring function as before
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            f.seek(0, os.SEEK_END)
            while not stop_event.is_set():
                line = f.readline()
                if line:
                    print(f'Access Log: {line.strip()}')
                time.sleep(0.1)
    except FileNotFoundError:
        print(f'Error: Access log file not found at {log_file_path}')
    except Exception as e:
        print(f'Error monitoring access log: {e}')


def start_nginx_daemon(nginx_path, config_path):
    try:
        subprocess.Popen(
            [nginx_path, '-c', config_path],
            creationflags=subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        print('Nginx started as a daemon.')
    except FileNotFoundError:
        print(f'Error: Nginx executable not found at {nginx_path}')
    except Exception as e:
        print(f'Error starting Nginx daemon: {e}')


def stop_nginx_daemon():
    # Implement a way to gracefully stop the Nginx daemon
    # This might involve sending a signal (if Nginx is configured to listen)
    # or using the nginx.exe -s stop command.
    # print('Stopping Nginx daemon (implementation needed).')
    # Example using subprocess to send the stop command:
    try:
        subprocess.run(
            [nginx_path, '-s', 'stop'], check=True
        )  # Replace with actual path
        print('Nginx daemon stopped.')
    except FileNotFoundError:
        print('Error: nginx.exe not found for stopping.')
    except subprocess.CalledProcessError as e:
        print(f'Error stopping Nginx: {e}')


stop_monitoring_daemon = threading.Event()


def signal_handler(signum, frame):
    global stop_monitoring_daemon
    print('\nCtrl+C detected. Stopping log monitoring and Nginx daemon...')
    stop_monitoring_daemon.set()
    stop_nginx_daemon()
    exit(0)  # Or let the main thread exit


def ai_run_nginx():
    config_path = bindir.joinpath(
        'conf/nginx.conf'
    )  # Replace with your actual config path
    access_log_path = bindir.joinpath(
        'logs/access.log'
    )  # Replace with your access log path

    log_thread_daemon = threading.Thread(
        target=monitor_access_log_daemon, args=(access_log_path, stop_monitoring_daemon)
    )
    log_thread_daemon.daemon = True
    log_thread_daemon.start()

    start_nginx_daemon(nginx_path, config_path)

    signal.signal(signal.SIGINT, signal_handler)  # Register the Ctrl+C handler

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive to catch signals
    except KeyboardInterrupt:
        # This part might not be reached directly if the signal handler exits
        print('Exiting main thread.')
    finally:
        stop_monitoring_daemon.set()
        log_thread_daemon.join(timeout=2)
        print('Log monitoring stopped.')
