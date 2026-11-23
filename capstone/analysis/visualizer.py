"""
Analytical Visualization Suite for OS Simulator.
Generates publication-quality charts using Matplotlib:
1. CPU Scheduling Turnaround & Waiting Time Comparison
2. Virtual Memory Page Faults vs Frame Count (FIFO, LRU, Optimal, LFU)
3. Disk Arm Movement & Seek Trajectory Comparison
4. Contiguous Allocation Memory Utilization & Fragmentation
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from analysis.benchmark_runner import BenchmarkRunner
from core.logger import get_logger

logger = get_logger()


class Visualizer:
    """Generates analytical charts and saves high-resolution images."""

    def __init__(self, charts_dir: str = "output/charts"):
        self.charts_dir = charts_dir
        os.makedirs(self.charts_dir, exist_ok=True)
        # Apply standard clean styling
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    def plot_cpu_scheduling(self, cpu_results):
        algorithms = [r.algorithm for r in cpu_results]
        avg_tat = [r.avg_turnaround_time for r in cpu_results]
        avg_wt = [r.avg_waiting_time for r in cpu_results]

        x = np.arange(len(algorithms))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        bars1 = ax.bar(x - width/2, avg_tat, width, label="Avg Turnaround Time", color="#1f77b4", edgecolor="black")
        bars2 = ax.bar(x + width/2, avg_wt, width, label="Avg Waiting Time", color="#ff7f0e", edgecolor="black")

        ax.set_ylabel("Time Units", fontsize=12, fontweight="bold")
        ax.set_title("CPU Scheduling Algorithms: Performance Metrics Comparison", fontsize=14, fontweight="bold", pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, rotation=25, ha="right", fontsize=10, fontweight="bold")
        ax.legend(fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.6)

        # Label values on bars
        for bar in bars1:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.2, f"{yval:.1f}", ha="center", va="bottom", fontsize=9)
        for bar in bars2:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.2, f"{yval:.1f}", ha="center", va="bottom", fontsize=9)

        plt.tight_layout()
        out_path = os.path.join(self.charts_dir, "cpu_scheduling_comparison.png")
        plt.savefig(out_path)
        plt.close()
        logger.info(f"Saved CPU comparison chart to {out_path}")
        return out_path

    def plot_page_replacement(self, page_results):
        frames = sorted(list(page_results.keys()))
        algos = ["FIFO", "LRU", "Optimal", "LFU"]
        colors = {"FIFO": "#e74c3c", "LRU": "#2980b9", "Optimal": "#27ae60", "LFU": "#8e44ad"}
        markers = {"FIFO": "o", "LRU": "s", "Optimal": "^", "LFU": "D"}

        fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)

        for algo in algos:
            faults = [page_results[f][algo].total_page_faults for f in frames]
            ax.plot(frames, faults, marker=markers[algo], linewidth=2.5, markersize=8, color=colors[algo], label=algo)

        ax.set_xlabel("Frame Capacity (Allocation Size)", fontsize=12, fontweight="bold")
        ax.set_ylabel("Total Page Faults", fontsize=12, fontweight="bold")
        ax.set_title("Virtual Memory Page Replacement: Page Faults vs Frame Count", fontsize=14, fontweight="bold", pad=15)
        ax.set_xticks(frames)
        ax.legend(title="Algorithm", fontsize=11, title_fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.6)

        plt.tight_layout()
        out_path = os.path.join(self.charts_dir, "page_replacement_faults.png")
        plt.savefig(out_path)
        plt.close()
        logger.info(f"Saved Page replacement chart to {out_path}")
        return out_path

    def plot_disk_scheduling(self, disk_results):
        algorithms = [r.algorithm for r in disk_results]
        seeks = [r.total_head_movement for r in disk_results]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

        # Bar chart
        colors = ["#34495e", "#16a085", "#2980b9", "#8e44ad", "#d35400", "#c0392b"]
        bars = ax1.bar(algorithms, seeks, color=colors, edgecolor="black", width=0.6)
        ax1.set_ylabel("Total Head Movement (Cylinders)", fontsize=11, fontweight="bold")
        ax1.set_title("Disk Scheduling: Total Head Movement Comparison", fontsize=12, fontweight="bold")
        ax1.tick_params(axis="x", rotation=25)
        ax1.grid(True, linestyle="--", alpha=0.5)

        for bar in bars:
            yval = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 5, f"{yval}", ha="center", va="bottom", fontsize=9, fontweight="bold")

        # Trajectory path for SSTF vs FCFS vs SCAN
        selected_algos = [r for r in disk_results if r.algorithm in ("FCFS", "SSTF", "SCAN", "LOOK")]
        style_map = {"FCFS": ("--", "o"), "SSTF": ("-", "s"), "SCAN": ("-.", "^"), "LOOK": (":", "D")}

        for r in selected_algos:
            linestyle, marker = style_map.get(r.algorithm, ("-", "o"))
            ax2.plot(r.seek_sequence, range(len(r.seek_sequence)), linestyle=linestyle, marker=marker, label=r.algorithm, linewidth=2)

        ax2.set_xlabel("Cylinder Number", fontsize=11, fontweight="bold")
        ax2.set_ylabel("Request Step Sequence", fontsize=11, fontweight="bold")
        ax2.set_title("Disk Arm Trajectory Over Time", fontsize=12, fontweight="bold")
        ax2.invert_yaxis()
        ax2.legend(fontsize=10)
        ax2.grid(True, linestyle="--", alpha=0.5)

        plt.tight_layout()
        out_path = os.path.join(self.charts_dir, "disk_scheduling_seeks.png")
        plt.savefig(out_path)
        plt.close()
        logger.info(f"Saved Disk scheduling chart to {out_path}")
        return out_path

    def plot_memory_allocation(self, contiguous_results):
        algos = [r.algorithm for r in contiguous_results]
        internal_frag = [r.total_internal_fragmentation for r in contiguous_results]
        utilization = [r.utilization_percentage for r in contiguous_results]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=300)

        # Internal Frag
        bars1 = ax1.bar(algos, internal_frag, color=["#3498db", "#2ecc71", "#e67e22"], edgecolor="black", width=0.5)
        ax1.set_ylabel("Internal Fragmentation (KB)", fontsize=11, fontweight="bold")
        ax1.set_title("Internal Fragmentation by Strategy", fontsize=12, fontweight="bold")
        ax1.grid(True, linestyle="--", alpha=0.5)
        for b in bars1:
            h = b.get_height()
            ax1.text(b.get_x() + b.get_width()/2.0, h + 5, f"{h} KB", ha="center", va="bottom", fontsize=10, fontweight="bold")

        # Memory Utilization
        bars2 = ax2.bar(algos, utilization, color=["#1abc9c", "#9b59b6", "#f39c12"], edgecolor="black", width=0.5)
        ax2.set_ylabel("Memory Utilization (%)", fontsize=11, fontweight="bold")
        ax2.set_title("Partition Memory Utilization (%)", fontsize=12, fontweight="bold")
        ax2.set_ylim(0, 100)
        ax2.grid(True, linestyle="--", alpha=0.5)
        for b in bars2:
            h = b.get_height()
            ax2.text(b.get_x() + b.get_width()/2.0, h + 2, f"{h:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

        plt.tight_layout()
        out_path = os.path.join(self.charts_dir, "memory_allocation_stats.png")
        plt.savefig(out_path)
        plt.close()
        logger.info(f"Saved Memory allocation chart to {out_path}")
        return out_path


def generate_all_visualizations():
    runner = BenchmarkRunner()
    cpu_res = runner.run_cpu_benchmarks()
    mem_res = runner.run_memory_benchmarks()
    st_res = runner.run_storage_benchmarks()

    viz = Visualizer()
    viz.plot_cpu_scheduling(cpu_res)
    viz.plot_page_replacement(mem_res["page_replacement"])
    viz.plot_disk_scheduling(st_res["disk_results"])
    viz.plot_memory_allocation(mem_res["contiguous"])
    print("All analytical visualizations successfully generated!")


if __name__ == "__main__":
    generate_all_visualizations()
