#!/bin/bash
# Run benchmarks and generate reports

# Ensure we're in the project root directory
cd "$(dirname "$0")/.." || exit 1

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install the package with benchmark dependencies
pip install -e ".[benchmarks]"

# Create output directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="benchmark_results/${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

# Run benchmarks
echo "Running benchmarks..."
python benchmarks/run_benchmarks.py --output-dir "$OUTPUT_DIR" "$@"

# Generate summary
echo "Benchmark results saved to $OUTPUT_DIR"
echo "Summary:"
echo "-------"
cat "$OUTPUT_DIR/benchmarks.md" | grep -A 10 "## Cache Performance Comparison"

# Create a symlink to the latest benchmark results
ln -sf "$TIMESTAMP" benchmark_results/latest

echo "Done. View full report at $OUTPUT_DIR/benchmarks.html"
