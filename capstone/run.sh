#!/usr/bin/env bash
# ==============================================================================
# OS Simulator - Master Integrated Launcher & CLI Entrypoint
# Powered by uv / Python 3
# Student: Varun Chauhan (Roll No: 2401010276)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"

GREEN="\033[32m"
BLUE="\033[34m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
BOLD="\033[1m"
RESET="\033[0m"

# Resolve runner: prefer uv run python if uv is installed
if command -v uv &>/dev/null; then
    RUNNER="uv run python"
elif command -v python3 &>/dev/null; then
    RUNNER="python3"
else
    echo -e "${RED}[ERROR] Neither 'uv' nor 'python3' was found on your system.${RESET}"
    exit 1
fi

show_help() {
    cat << EOF
${BOLD}SIM-OS: Integrated OS Resource Management Simulator${RESET}
Managed via ${CYAN}uv${RESET} | Developed by Varun Chauhan (2401010276)

${BOLD}USAGE:${RESET}
    ./run.sh [OPTIONS]
    or with uv directly:
    uv run main.py [OPTIONS]

${BOLD}OPTIONS:${RESET}
    -m, --menu          Launch the interactive text-based console menu (Default)
    -b, --benchmark     Execute complete comparative benchmark and generate charts
    -t, --test          Run comprehensive unit test suite with boundary and error tests
    -s, --telemetry     Probe and inspect real host Linux OS kernel telemetry
    -c, --charts        Regenerate all visual comparison plots into output/charts/
    -h, --help          Show this assistance message

${BOLD}EXAMPLES:${RESET}
    ./run.sh                  # Interactive simulator
    ./run.sh --benchmark      # Run all benchmarks
    ./run.sh --test           # Run 37 unit tests
    ./run.sh --telemetry      # Probe Linux /proc telemetry

    # Direct uv invocation:
    uv run main.py
    uv run python -m unittest discover -s tests -p "test_*.py" -v
EOF
}

case "${1:-}" in
    -h|--help)
        show_help
        ;;
    -b|--benchmark)
        echo -e "${CYAN}${BOLD}[SIM-OS] Launching Full Benchmarks & Analytics (${RUNNER})...${RESET}"
        bash bash/run_benchmarks.sh
        ;;
    -t|--test)
        echo -e "${CYAN}${BOLD}[SIM-OS] Running Complete Test Suite (${RUNNER})...${RESET}"
        ${RUNNER} -m unittest discover -s tests -p "test_*.py" -v
        ;;
    -s|--telemetry)
        bash bash/host_telemetry.sh
        ;;
    -c|--charts)
        echo -e "${CYAN}${BOLD}[SIM-OS] Generating Analytical Visualization Plots (${RUNNER})...${RESET}"
        ${RUNNER} -c "from analysis.visualizer import generate_all_visualizations; generate_all_visualizations()"
        ;;
    -m|--menu|"")
        ${RUNNER} main.py
        ;;
    *)
        echo -e "${RED}[ERROR] Unknown option: $1${RESET}"
        show_help
        exit 1
        ;;
esac
