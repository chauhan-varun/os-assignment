import sys
import os
import subprocess

def check_env():
    print("Environment Verification:")
    
    print(f"- Python Version: {sys.version.split()[0]}")
    
    if os.name == 'posix':
        try:
            with open('/proc/version', 'r') as f:
                version = f.read().lower()
                if 'wsl' in version or 'microsoft' in version:
                    print("- OS Environment: Ubuntu on WSL")
                elif 'ubuntu' in version:
                    print("- OS Environment: Ubuntu Linux")
                else:
                    print("- OS Environment: Linux")
        except FileNotFoundError:
            print("- OS Environment: Linux (POSIX)")
    else:
        print("- OS Environment: Windows or other")
        
    try:
        result = subprocess.run(['code', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"- VS Code: Installed (Version: {result.stdout.splitlines()[0]})")
        else:
            print("- VS Code: 'code' command failed")
    except FileNotFoundError:
        print("- VS Code: 'code' command not found in PATH")
        
    print("\nAll required components checked.")

if __name__ == "__main__":
    check_env()
