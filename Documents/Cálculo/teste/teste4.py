import psutil
import time

def get_pid_with_most_cpu_usage(interval=1):
    """
    Finds the PID with the highest CPU usage percentage over a given interval.
    
    Args:
        interval (int/float): The time interval in seconds over which to measure 
                              CPU usage. A non-zero interval is recommended for accuracy.

    Returns:
        tuple: (pid, cpu_percent, process_name) of the process with max usage, 
               or None if no processes are found.
    """
    
    # Enable a one-time call to cpu_percent() for all processes with a 
    # non-blocking interval=0.0 to initialize the counters.
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent(interval=0.0)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Wait for the specified interval to measure actual CPU time
    time.sleep(interval)
    
    max_cpu_usage = 0
    best_proc = None

    # Iterate again to get the CPU usage over the interval
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # The second call to cpu_percent() will calculate the usage percentage 
            # since the last call.
            cpu_usage = proc.cpu_percent(interval=0.0)
            
            if cpu_usage > max_cpu_usage:
                max_cpu_usage = cpu_usage
                best_proc = proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if best_proc:
        return (best_proc.info['pid'], max_cpu_usage, best_proc.info['name'])
    else:
        return None

# Example usage:
if __name__ == "__main__":
    # Measure CPU usage over a 1 second interval
    result = get_pid_with_most_cpu_usage(interval=1)
    
    if result:
        pid, cpu_percent, name = result
        print(f"Process with most CPU usage (over last 1s):")
        print(f"* PID: {pid}")
        print(f"* Name: {name}")
        print(f"* CPU Usage: {cpu_percent:.2f}%")
    else:
        print("No processes found or unable to retrieve data.")
