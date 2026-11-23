#!/usr/bin/env bash
# ==============================================================================
# OS Simulator - Host OS Telemetry and Resource Inspection Script
# Extracts real Linux kernel telemetry from procfs, sysfs, and system utilities.
# ==============================================================================

set -euo pipefail

# ANSI color codes
BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
BLUE="\033[34m"
RED="\033[31m"
RESET="\033[0m"

print_header() {
    echo -e "${BLUE}${BOLD}========================================================================${RESET}"
    echo -e "${CYAN}${BOLD}       SIM-OS REAL-TIME HOST LINUX TELEMETRY & SYSTEM PROBE             ${RESET}"
    echo -e "${BLUE}${BOLD}========================================================================${RESET}"
}

print_kernel_info() {
    echo -e "\n${GREEN}${BOLD}[1] Kernel & Architecture Diagnostics${RESET}"
    echo -e "  • OS Platform     : $(uname -s)"
    echo -e "  • Kernel Release  : $(uname -r)"
    echo -e "  • Architecture    : $(uname -m)"
    echo -e "  • Hostname        : $(hostname)"
    echo -e "  • Uptime          : $(uptime -p 2>/dev/null || uptime)"
}

print_cpu_info() {
    echo -e "\n${GREEN}${BOLD}[2] CPU Topology & Utilization (/proc/cpuinfo)${RESET}"
    if [ -f /proc/cpuinfo ]; then
        local model
        model=$(grep -m1 "model name" /proc/cpuinfo | awk -F: '{print $2}' | xargs)
        local cores
        cores=$(grep -c "processor" /proc/cpuinfo)
        echo -e "  • Processor Model : ${model:-Virtual / Emulated CPU}"
        echo -e "  • Logical Cores   : ${cores}"
    fi

    if [ -f /proc/loadavg ]; then
        local l1 l5 l15
        read -r l1 l5 l15 _ _ < /proc/loadavg
        echo -e "  • Load Average    : 1m=${l1}, 5m=${l5}, 15m=${l15}"
    fi
}

print_memory_info() {
    echo -e "\n${GREEN}${BOLD}[3] Memory & Swapping Diagnostics (/proc/meminfo)${RESET}"
    if [ -f /proc/meminfo ]; then
        local mem_total mem_free mem_avail swap_total swap_free
        mem_total=$(grep "MemTotal:" /proc/meminfo | awk '{printf "%.2f MB", $2/1024}')
        mem_free=$(grep "MemFree:" /proc/meminfo | awk '{printf "%.2f MB", $2/1024}')
        mem_avail=$(grep "MemAvailable:" /proc/meminfo | awk '{printf "%.2f MB", $2/1024}')
        swap_total=$(grep "SwapTotal:" /proc/meminfo | awk '{printf "%.2f MB", $2/1024}')
        swap_free=$(grep "SwapFree:" /proc/meminfo | awk '{printf "%.2f MB", $2/1024}')

        echo -e "  • Total Physical RAM : ${mem_total}"
        echo -e "  • Free Memory        : ${mem_free}"
        echo -e "  • Available Memory   : ${mem_avail}"
        echo -e "  • Total Swap Space   : ${swap_total}"
        echo -e "  • Free Swap Space    : ${swap_free}"
    fi
}

print_process_info() {
    echo -e "\n${GREEN}${BOLD}[4] Process Table Summary (POSIX PID Snapshot)${RESET}"
    local total_procs running_procs
    total_procs=$(ps -e --no-headers | wc -l)
    running_procs=$(ps -eo stat --no-headers | grep -c "^R" || true)
    echo -e "  • Active Processes : ${total_procs}"
    echo -e "  • Running (State R): ${running_procs}"

    echo -e "\n  ${YELLOW}Top 5 Processes by Memory Usage:${RESET}"
    printf "  %-8s %-10s %-8s %-8s %-20s\n" "PID" "USER" "%CPU" "%MEM" "COMMAND"
    ps -eo pid,user,%cpu,%mem,comm --sort=-%mem --no-headers | head -n 5 | while read -r p u c m cmd; do
        printf "  %-8s %-10s %-8s %-8s %-20s\n" "$p" "$u" "$c" "$m" "$cmd"
    done
}

print_storage_info() {
    echo -e "\n${GREEN}${BOLD}[5] Storage & Mount Points (df -h)${RESET}"
    printf "  %-20s %-10s %-10s %-10s %-6s %-15s\n" "Filesystem" "Size" "Used" "Avail" "Use%" "Mounted on"
    df -h -x tmpfs -x devtmpfs --output=source,size,used,avail,pcent,target | tail -n +2 | head -n 5 | while read -r fs sz us av pc mt; do
        printf "  %-20s %-10s %-10s %-10s %-6s %-15s\n" "$fs" "$sz" "$us" "$av" "$pc" "$mt"
    done
}

main() {
    print_header
    print_kernel_info
    print_cpu_info
    print_memory_info
    print_process_info
    print_storage_info
    echo -e "\n${BLUE}${BOLD}========================================================================${RESET}\n"
}

main "$@"
