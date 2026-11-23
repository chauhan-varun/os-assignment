#!/usr/bin/env bash
# ==============================================================================
# OS Simulator - Automated Benchmark & Test Harness
# Executes test suites, workload simulations, and captures execution timings via uv.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAPSTONE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

GREEN="\033[32m"
BLUE="\033[34m"
CYAN="\033[36m"
RESET="\033[0m"

echo -e "${BLUE}============================================================${RESET}"
echo -e "${CYAN}   SIM-OS AUTOMATED BENCHMARK SUITE & INTEGRATION HARNESS   ${RESET}"
echo -e "${BLUE}============================================================${RESET}"

cd "${CAPSTONE_DIR}"

# Determine runner: prefer uv run python
if command -v uv &>/dev/null; then
    PY="uv run python"
else
    PY="python3"
fi

mkdir -p output/reports output/charts output/traces logs

echo -e "\n${GREEN}[Step 1/3] Running Python Unittest Suite via ${PY}...${RESET}"
START_TIME=$(date +%s%N)
${PY} -m unittest discover -s tests -p "test_*.py" -v
END_TIME=$(date +%s%N)
TEST_DIFF=$(( (END_TIME - START_TIME) / 1000000 ))
echo -e "✓ Test suite completed in ${TEST_DIFF} ms."

echo -e "\n${GREEN}[Step 2/3] Running Multi-Algorithm Workload Benchmarks...${RESET}"
${PY} -c "from analysis.benchmark_runner import run_all_benchmarks; run_all_benchmarks()"
echo -e "✓ Benchmark execution completed."

echo -e "\n${GREEN}[Step 3/3] Generating Visual Comparison Plots & Analytics...${RESET}"
${PY} -c "from analysis.visualizer import generate_all_visualizations; generate_all_visualizations()"
echo -e "✓ Plots successfully generated in output/charts/."

echo -e "\n${BLUE}============================================================${RESET}"
echo -e "${GREEN}✓ All capstone verification steps finished successfully!${RESET}"
echo -e "${BLUE}============================================================${RESET}\n"
