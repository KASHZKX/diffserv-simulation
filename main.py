#!/usr/bin/env python3
"""Main entry point for DiffServ simulation.

This module handles command-line argument parsing and runs the simulation.

Usage:
    python main.py --patterns E A B A E
    python main.py --patterns EABAE
"""

import argparse
from typing import List

from src import Simulator


def parse_patterns(patterns_input: List[str]) -> List[str]:
    """Parse and normalize pattern input.

    Args:
        patterns_input: List of pattern strings from command line.

    Returns:
        List of single-character patterns ('E', 'A', or 'B').

    Raises:
        ValueError: If an invalid pattern is provided.
    """
    patterns = []

    for item in patterns_input:
        # Handle case where patterns are provided as a single string (e.g., "EABAE")
        for char in item.upper():
            if char in ('E', 'A', 'B'):
                patterns.append(char)
            elif char in (' ', ','):
                continue  # Skip whitespace and commas
            else:
                raise ValueError(
                    f"Invalid pattern '{char}'. "
                    "Use 'E' for EF, 'A' for AF, or 'B' for BE."
                )

    return patterns


def main():
    """Main function to run the DiffServ simulation."""
    parser = argparse.ArgumentParser(
        description='DiffServ Network Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --patterns E A B A E
    python main.py --patterns EABAE
    python main.py --patterns E,A,B,A,E

Pattern Types:
    E - Expedited Forwarding (EF) - Highest priority
    A - Assured Forwarding (AF) - Medium priority (subject to remarking)
    B - Best Effort (BE) - Lowest priority
        """
    )

    parser.add_argument(
        '--patterns', '-p',
        nargs='+',
        required=True,
        help='Traffic patterns for each source (E=EF, A=AF, B=BE)'
    )

    args = parser.parse_args()

    try:
        patterns = parse_patterns(args.patterns)
    except ValueError as e:
        parser.error(str(e))
        return

    if not patterns:
        parser.error("At least one pattern must be provided.")
        return

    # Create and run simulation
    simulator = Simulator(patterns)
    simulator.run()
    simulator.print_results()


if __name__ == '__main__':
    main()
