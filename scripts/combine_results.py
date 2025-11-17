#!/usr/bin/env python3
"""Combine multiple foliage_results.csv files into a single summary."""

import argparse
import csv
import os
from pathlib import Path


def combine_results(input_base, output_file):
    """Combine all CSV results from subdirectories."""
    results = []
    
    base_path = Path(input_base)
    csv_files = list(base_path.rglob("foliage_results.csv"))
    
    print(f"Found {len(csv_files)} result files")
    
    for csv_file in csv_files:
        group_name = csv_file.parent.name
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['group'] = group_name
                results.append(row)
    
    if not results:
        print("No results found!")
        return
    
    # Write combined results
    fieldnames = ['group'] + list(results[0].keys() - {'group'})
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Combined {len(results)} records into {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Combine foliage results from multiple directories")
    parser.add_argument("--input", required=True, help="Base directory containing result subdirectories")
    parser.add_argument("--output", default="combined_results.csv", help="Output CSV file")
    
    args = parser.parse_args()
    combine_results(args.input, args.output)


if __name__ == "__main__":
    main()
