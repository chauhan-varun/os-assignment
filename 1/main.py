import os
import sys

def main():
    print(f"[Main] Starting process. PID: {os.getpid()}, PPID: {os.getppid()}")
    
    test_file = "test_file.txt"
    with open(test_file, "w") as f:
        f.write("Controlled test file data.\n")
    print(f"[File] Wrote to {test_file}")
    
    with open(test_file, "r") as f:
        data = f.read().strip()
    print(f"[File] Read from {test_file}: '{data}'")
    
    try:
        with open("/dev/null", "w") as f:
            f.write("writing to dev null\n")
        print("[Device] Successfully wrote to /dev/null")
    except Exception as e:
        print(f"[Device] Error writing to /dev/null: {e}")

    invalid_path = "/invalid/path/that/does/not/exist.txt"
    try:
        with open(invalid_path, "r") as f:
            f.read()
    except FileNotFoundError as e:
        print(f"[Error Handling] Caught expected error accessing {invalid_path}:\n  {e}")

    pid = os.fork()
    
    if pid > 0:
        print(f"[Parent] Created child process with PID: {pid}")
        _, status = os.wait()
        print(f"[Parent] Child process {pid} completed with status: {status}")
        
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"[Cleanup] Removed {test_file}")
            
    elif pid == 0:
        print(f"[Child] Running. PID: {os.getpid()}, PPID: {os.getppid()}")
        print("[Child] Executing 'ls' command:")
        os.system("ls")
        sys.exit(0)
    else:
        print("Fork failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
