#!/usr/bin/env python3
"""
Benchmark runner for the countryflag package.

This script runs benchmarks on the countryflag package and generates reports
in various formats (JSON, CSV, HTML, and Markdown).
"""

import argparse
import csv
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add the parent directory to the path so we can import countryflag
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import countryflag
from countryflag.cache.disk import DiskCache
from countryflag.cache.memory import MemoryCache
from countryflag.core.flag import CountryFlag

try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    HAS_VISUALIZATION_DEPS = True
except ImportError:
    HAS_VISUALIZATION_DEPS = False


def generate_country_list(size: int) -> List[str]:
    """Generate a list of country names of the specified size."""
    real_countries = [
        "United States",
        "Canada",
        "Mexico",
        "Brazil",
        "Argentina",
        "United Kingdom",
        "France",
        "Germany",
        "Italy",
        "Spain",
        "Russia",
        "China",
        "Japan",
        "India",
        "Australia",
        "South Africa",
        "Egypt",
        "Nigeria",
        "Kenya",
        "Morocco",
        "Saudi Arabia",
        "United Arab Emirates",
        "Israel",
        "Turkey",
        "Iran",
        "Thailand",
        "Vietnam",
        "Indonesia",
        "Malaysia",
        "Philippines",
        "South Korea",
        "North Korea",
        "Mongolia",
        "Kazakhstan",
        "Ukraine",
        "Poland",
        "Sweden",
        "Norway",
        "Finland",
        "Denmark",
        "Netherlands",
        "Belgium",
        "Switzerland",
        "Austria",
        "Greece",
        "Portugal",
        "Ireland",
        "Iceland",
        "New Zealand",
        "Singapore",
    ]

    # Repeat the list as needed to get the desired size
    if size <= len(real_countries):
        return real_countries[:size]
    else:
        return (real_countries * ((size // len(real_countries)) + 1))[:size]


def run_benchmark(
    name: str,
    func: callable,
    args: Tuple = (),
    kwargs: Dict = None,
    iterations: int = 5,
    warmup: int = 1,
) -> Dict[str, Any]:
    """
    Run a benchmark function and return timing statistics.

    Args:
        name: Name of the benchmark
        func: Function to benchmark
        args: Arguments to pass to the function
        kwargs: Keyword arguments to pass to the function
        iterations: Number of iterations to run
        warmup: Number of warmup iterations

    Returns:
        Dict containing benchmark results
    """
    if kwargs is None:
        kwargs = {}

    # Warmup
    for _ in range(warmup):
        func(*args, **kwargs)

    # Actual benchmark
    times = []
    for _ in range(iterations):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        times.append(end_time - start_time)

    # Calculate statistics
    mean_time = statistics.mean(times)
    median_time = statistics.median(times)
    min_time = min(times)
    max_time = max(times)
    stdev_time = statistics.stdev(times) if len(times) > 1 else 0

    return {
        "name": name,
        "iterations": iterations,
        "mean_time": mean_time,
        "median_time": median_time,
        "min_time": min_time,
        "max_time": max_time,
        "stdev_time": stdev_time,
        "times": times,
    }


def run_all_benchmarks(
    sizes: List[int] = None, iterations: int = 5, with_cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Run all benchmarks for the countryflag package.

    Args:
        sizes: List of dataset sizes to benchmark
        iterations: Number of iterations per benchmark
        with_cache: Whether to include cache benchmarks

    Returns:
        List of benchmark results
    """
    if sizes is None:
        sizes = [5, 25, 100, 250, 500]

    results = []

    # Prepare data
    data_sets = {size: generate_country_list(size) for size in sizes}

    # Standard conversion benchmarks
    for size in sizes:
        countries = data_sets[size]

        # No cache
        cf = CountryFlag()
        results.append(
            run_benchmark(
                f"convert_{size}_no_cache",
                cf.get_flag,
                args=(countries,),
                iterations=iterations,
            )
        )

        # With memory cache
        if with_cache:
            memory_cache = MemoryCache()
            cf_memory = CountryFlag(cache=memory_cache)

            # First run (cache miss)
            results.append(
                run_benchmark(
                    f"convert_{size}_memory_cache_miss",
                    cf_memory.get_flag,
                    args=(countries,),
                    iterations=iterations,
                )
            )

            # Second run (cache hit)
            results.append(
                run_benchmark(
                    f"convert_{size}_memory_cache_hit",
                    cf_memory.get_flag,
                    args=(countries,),
                    iterations=iterations,
                )
            )

    # Reverse lookup benchmarks
    for size in sizes:
        countries = data_sets[size]
        cf = CountryFlag()
        flags, _ = cf.get_flag(countries)
        flag_list = flags.split(" ")

        results.append(
            run_benchmark(
                f"reverse_lookup_{size}",
                cf.reverse_lookup,
                args=(flag_list,),
                iterations=iterations,
            )
        )

    # Format output benchmarks
    formats = ["text", "json", "csv"]
    for size in sizes:
        countries = data_sets[size]
        cf = CountryFlag()
        _, pairs = cf.get_flag(countries)

        for fmt in formats:
            results.append(
                run_benchmark(
                    f"format_output_{size}_{fmt}",
                    cf.format_output,
                    args=(pairs,),
                    kwargs={"output_format": fmt},
                    iterations=iterations,
                )
            )

    # Disk cache benchmarks
    if with_cache:
        with tempfile.TemporaryDirectory() as tmp_dir:
            for size in sizes:
                countries = data_sets[size]

                disk_cache = DiskCache(tmp_dir)
                cf_disk = CountryFlag(cache=disk_cache)

                # First run (cache miss)
                results.append(
                    run_benchmark(
                        f"convert_{size}_disk_cache_miss",
                        cf_disk.get_flag,
                        args=(countries,),
                        iterations=iterations,
                    )
                )

                # Second run (cache hit)
                results.append(
                    run_benchmark(
                        f"convert_{size}_disk_cache_hit",
                        cf_disk.get_flag,
                        args=(countries,),
                        iterations=iterations,
                    )
                )

    return results


def save_json_report(results: List[Dict[str, Any]], filename: str) -> None:
    """Save benchmark results as JSON."""
    with open(filename, "w") as f:
        json.dump(
            {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": countryflag.__version__,
                    "python_version": platform.python_version(),
                    "platform": platform.platform(),
                },
                "results": results,
            },
            f,
            indent=2,
        )


def save_csv_report(results: List[Dict[str, Any]], filename: str) -> None:
    """Save benchmark results as CSV."""
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Name",
                "Iterations",
                "Mean Time (s)",
                "Median Time (s)",
                "Min Time (s)",
                "Max Time (s)",
                "Std Dev (s)",
            ]
        )
        for result in results:
            writer.writerow(
                [
                    result["name"],
                    result["iterations"],
                    result["mean_time"],
                    result["median_time"],
                    result["min_time"],
                    result["max_time"],
                    result["stdev_time"],
                ]
            )


def save_markdown_report(results: List[Dict[str, Any]], filename: str) -> None:
    """Save benchmark results as Markdown."""
    with open(filename, "w") as f:
        f.write("# CountryFlag Benchmark Results\n\n")
        f.write(f"- Generated: {datetime.now().isoformat()}\n")
        f.write(f"- Version: {countryflag.__version__}\n")
        f.write(f"- Python: {platform.python_version()}\n")
        f.write(f"- Platform: {platform.platform()}\n\n")

        f.write("## Results\n\n")
        f.write(
            "| Benchmark | Iterations | Mean (s) | Median (s) | Min (s) | Max (s) | Std Dev (s) |\n"
        )
        f.write(
            "|-----------|------------|----------|------------|---------|---------|-------------|\n"
        )

        for result in results:
            f.write(
                f"| {result['name']} | {result['iterations']} | "
                f"{result['mean_time']:.6f} | {result['median_time']:.6f} | "
                f"{result['min_time']:.6f} | {result['max_time']:.6f} | "
                f"{result['stdev_time']:.6f} |\n"
            )

        f.write("\n")

        # Add cache performance comparison
        f.write("## Cache Performance Comparison\n\n")
        f.write(
            "| Dataset Size | No Cache (s) | Memory Cache Hit (s) | Improvement |\n"
        )
        f.write(
            "|--------------|--------------|----------------------|-------------|\n"
        )

        sizes = set()
        no_cache_times = {}
        memory_cache_hit_times = {}

        for result in results:
            if result["name"].startswith("convert_"):
                parts = result["name"].split("_")
                if len(parts) >= 3:
                    size = int(parts[1])
                    sizes.add(size)

                    if result["name"].endswith("no_cache"):
                        no_cache_times[size] = result["mean_time"]
                    elif result["name"].endswith("memory_cache_hit"):
                        memory_cache_hit_times[size] = result["mean_time"]

        for size in sorted(sizes):
            if size in no_cache_times and size in memory_cache_hit_times:
                improvement = no_cache_times[size] / memory_cache_hit_times[size]
                f.write(
                    f"| {size} | {no_cache_times[size]:.6f} | "
                    f"{memory_cache_hit_times[size]:.6f} | {improvement:.2f}x |\n"
                )


def generate_plots(results: List[Dict[str, Any]], output_dir: str) -> None:
    """Generate plots for benchmark results."""
    if not HAS_VISUALIZATION_DEPS:
        print("Matplotlib, pandas, and seaborn are required for plot generation.")
        return

    os.makedirs(output_dir, exist_ok=True)

    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(results)

    # Extract dataset size and benchmark type from name
    df["size"] = df["name"].apply(
        lambda x: int(x.split("_")[1]) if x.split("_")[0] == "convert" else 0
    )
    df["type"] = df["name"].apply(
        lambda x: (
            "_".join(x.split("_")[2:])
            if x.split("_")[0] == "convert"
            else x.split("_")[0]
        )
    )

    # Plot 1: Performance by dataset size
    plt.figure(figsize=(12, 8))
    sns.barplot(x="size", y="mean_time", hue="type", data=df[df["size"] > 0])
    plt.title("Performance by Dataset Size")
    plt.xlabel("Dataset Size")
    plt.ylabel("Mean Time (s)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "performance_by_size.png"))

    # Plot 2: Cache performance comparison
    cache_df = df[
        df["name"].str.contains("convert_")
        & (
            df["name"].str.contains("no_cache")
            | df["name"].str.contains("memory_cache_hit")
        )
    ]

    plt.figure(figsize=(12, 8))
    sns.barplot(x="size", y="mean_time", hue="type", data=cache_df)
    plt.title("Cache Performance Comparison")
    plt.xlabel("Dataset Size")
    plt.ylabel("Mean Time (s)")
    plt.yscale("log")  # Log scale to better show differences
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "cache_performance.png"))

    # Plot 3: Format output performance
    format_df = df[df["name"].str.contains("format_output_")]
    format_df["format"] = format_df["name"].apply(lambda x: x.split("_")[-1])
    format_df["size"] = format_df["name"].apply(lambda x: int(x.split("_")[2]))

    plt.figure(figsize=(12, 8))
    sns.barplot(x="size", y="mean_time", hue="format", data=format_df)
    plt.title("Format Output Performance")
    plt.xlabel("Dataset Size")
    plt.ylabel("Mean Time (s)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "format_performance.png"))


def save_html_report(
    results: List[Dict[str, Any]], filename: str, plot_dir: Optional[str] = None
) -> None:
    """Save benchmark results as HTML."""
    plots_html = ""
    if plot_dir and os.path.exists(plot_dir):
        plots_html = f"""
        <h2>Performance Plots</h2>
        <div class="plots">
            <img src="{os.path.join(plot_dir, 'performance_by_size.png')}" alt="Performance by Dataset Size" />
            <img src="{os.path.join(plot_dir, 'cache_performance.png')}" alt="Cache Performance Comparison" />
            <img src="{os.path.join(plot_dir, 'format_performance.png')}" alt="Format Output Performance" />
        </div>
        """

    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>CountryFlag Benchmark Results</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 1200px; margin: 0 auto; }}
            h1, h2 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ text-align: left; padding: 12px; }}
            th {{ background-color: #3498db; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .metadata {{ margin-bottom: 30px; }}
            .metadata p {{ margin: 5px 0; }}
            .plots img {{ max-width: 100%; height: auto; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>CountryFlag Benchmark Results</h1>

        <div class="metadata">
            <p><strong>Generated:</strong> {datetime.now().isoformat()}</p>
            <p><strong>Version:</strong> {countryflag.__version__}</p>
            <p><strong>Python:</strong> {platform.python_version()}</p>
            <p><strong>Platform:</strong> {platform.platform()}</p>
        </div>

        <h2>Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Benchmark</th>
                    <th>Iterations</th>
                    <th>Mean (s)</th>
                    <th>Median (s)</th>
                    <th>Min (s)</th>
                    <th>Max (s)</th>
                    <th>Std Dev (s)</th>
                </tr>
            </thead>
            <tbody>
    """

    for result in results:
        html += f"""
                <tr>
                    <td>{result['name']}</td>
                    <td>{result['iterations']}</td>
                    <td>{result['mean_time']:.6f}</td>
                    <td>{result['median_time']:.6f}</td>
                    <td>{result['min_time']:.6f}</td>
                    <td>{result['max_time']:.6f}</td>
                    <td>{result['stdev_time']:.6f}</td>
                </tr>
        """

    html += """
            </tbody>
        </table>

        <h2>Cache Performance Comparison</h2>
        <table>
            <thead>
                <tr>
                    <th>Dataset Size</th>
                    <th>No Cache (s)</th>
                    <th>Memory Cache Hit (s)</th>
                    <th>Improvement</th>
                </tr>
            </thead>
            <tbody>
    """

    sizes = set()
    no_cache_times = {}
    memory_cache_hit_times = {}

    for result in results:
        if result["name"].startswith("convert_"):
            parts = result["name"].split("_")
            if len(parts) >= 3:
                size = int(parts[1])
                sizes.add(size)

                if result["name"].endswith("no_cache"):
                    no_cache_times[size] = result["mean_time"]
                elif result["name"].endswith("memory_cache_hit"):
                    memory_cache_hit_times[size] = result["mean_time"]

    for size in sorted(sizes):
        if size in no_cache_times and size in memory_cache_hit_times:
            improvement = no_cache_times[size] / memory_cache_hit_times[size]
            html += f"""
                <tr>
                    <td>{size}</td>
                    <td>{no_cache_times[size]:.6f}</td>
                    <td>{memory_cache_hit_times[size]:.6f}</td>
                    <td>{improvement:.2f}x</td>
                </tr>
            """

    html += f"""
            </tbody>
        </table>

        {plots_html}

    </body>
    </html>
    """

    with open(filename, "w") as f:
        f.write(html)


def main():
    """Run benchmarks and generate reports."""
    parser = argparse.ArgumentParser(
        description="Run benchmarks for the countryflag package"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="benchmark_results",
        help="Output directory for benchmark reports",
    )
    parser.add_argument(
        "--sizes",
        "-s",
        type=int,
        nargs="+",
        default=[5, 25, 100, 250, 500],
        help="Dataset sizes to benchmark",
    )
    parser.add_argument(
        "--iterations",
        "-i",
        type=int,
        default=5,
        help="Number of iterations per benchmark",
    )
    parser.add_argument("--no-cache", action="store_true", help="Skip cache benchmarks")
    parser.add_argument(
        "--formats",
        "-f",
        nargs="+",
        choices=["json", "csv", "markdown", "html", "all"],
        default=["all"],
        help="Report formats to generate",
    )
    parser.add_argument("--no-plots", action="store_true", help="Skip plot generation")

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Running benchmarks for dataset sizes: {args.sizes}...")
    results = run_all_benchmarks(
        sizes=args.sizes, iterations=args.iterations, with_cache=not args.no_cache
    )
    print("Benchmarks complete.")

    # Determine formats to generate
    formats = set(args.formats)
    if "all" in formats:
        formats = {"json", "csv", "markdown", "html"}

    # Generate plots
    plot_dir = None
    if not args.no_plots and HAS_VISUALIZATION_DEPS:
        plot_dir = os.path.join(args.output_dir, "plots")
        print("Generating plots...")
        generate_plots(results, plot_dir)

    # Generate reports
    print("Generating reports...")
    if "json" in formats:
        json_file = os.path.join(args.output_dir, "benchmarks.json")
        save_json_report(results, json_file)
        print(f"JSON report saved to {json_file}")

    if "csv" in formats:
        csv_file = os.path.join(args.output_dir, "benchmarks.csv")
        save_csv_report(results, csv_file)
        print(f"CSV report saved to {csv_file}")

    if "markdown" in formats:
        md_file = os.path.join(args.output_dir, "benchmarks.md")
        save_markdown_report(results, md_file)
        print(f"Markdown report saved to {md_file}")

    if "html" in formats:
        html_file = os.path.join(args.output_dir, "benchmarks.html")
        save_html_report(results, html_file, plot_dir)
        print(f"HTML report saved to {html_file}")

    print("Done.")


if __name__ == "__main__":
    main()
