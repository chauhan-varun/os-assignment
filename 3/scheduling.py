def get_input():
    processes = []
    print("Enter process details. Type 'done' when finished.")
    while True:
        entry = input("Enter PID, Arrival Time, Burst Time (e.g., P1 0 5): ")
        if entry.lower() == 'done':
            break
        
        parts = entry.split()
        if len(parts) != 3:
            print("Invalid input. Please provide exactly 3 values.")
            continue
            
        pid, at_str, bt_str = parts
        try:
            at = int(at_str)
            bt = int(bt_str)
            if at < 0 or bt <= 0:
                print("Invalid values. Arrival time >= 0 and Burst time > 0.")
                continue
            processes.append({"pid": pid, "at": at, "bt": bt})
        except ValueError:
            print("Invalid input. Arrival time and burst time must be integers.")
            
    return processes

def fcfs(processes):
    print("\n--- FCFS Scheduling ---")
    procs = sorted(processes, key=lambda x: x['at'])
    
    current_time = 0
    sequence = []
    
    for p in procs:
        if current_time < p['at']:
            print(f"Idle: {current_time} to {p['at']}")
            current_time = p['at']
            
        start_time = current_time
        current_time += p['bt']
        end_time = current_time
        
        sequence.append(p['pid'])
        print(f"Process {p['pid']} executed: {start_time} to {end_time}")
        
    print("Execution Sequence:", " -> ".join(sequence))

def sjf(processes):
    print("\n--- SJF (Non-preemptive) Scheduling ---")
    procs = sorted(processes, key=lambda x: x['at'])
    
    current_time = 0
    sequence = []
    completed = []
    n = len(procs)
    
    while len(completed) < n:
        available = [p for p in procs if p['at'] <= current_time and p not in completed]
        
        if not available:
            next_arrival = min(p['at'] for p in procs if p not in completed)
            print(f"Idle: {current_time} to {next_arrival}")
            current_time = next_arrival
            available = [p for p in procs if p['at'] <= current_time and p not in completed]
            
        selected = min(available, key=lambda x: (x['bt'], x['at']))
        
        start_time = current_time
        current_time += selected['bt']
        end_time = current_time
        
        sequence.append(selected['pid'])
        completed.append(selected)
        print(f"Process {selected['pid']} executed: {start_time} to {end_time}")
        
    print("Execution Sequence:", " -> ".join(sequence))

def main():
    processes = get_input()
    if not processes:
        print("No processes entered.")
        return
        
    fcfs(processes)
    sjf(processes)

if __name__ == "__main__":
    main()
