"""Simulator class for DiffServ simulation."""

import random
from typing import List
from .source import Source
from .edge_node import EdgeNode
from .core_node import CoreNode


class Simulator:
    """Main simulator for DiffServ network simulation.

    Coordinates the simulation of multiple sources, an edge node,
    and a core node to model Differentiated Services behavior.

    Attributes:
        sources: List of traffic sources.
        edge_node: Edge node for traffic policing/remarking.
        core_node: Core node for priority queuing and scheduling.
        current_time: Current simulation time step.
    """

    def __init__(self, patterns: List[str]):
        """Initialize the simulator with traffic patterns.

        Args:
            patterns: List of service types ('E', 'A', 'B' or 'EF', 'AF', 'BE')
                     for each source.
        """
        self.sources = [Source(i, p) for i, p in enumerate(patterns)]
        self.edge_node = EdgeNode()
        self.core_node = CoreNode()
        self.current_time = 0

    def run(self) -> None:
        """Run the simulation until all sources complete.

        The simulation continues until all sources have successfully
        transmitted 1000 packets each.
        """
        while not self._all_sources_finished():
            # 1. Generation phase: collect packets from active sources
            new_packets = []
            for source in self.sources:
                if not source.is_finished():
                    packet = source.generate_packet(self.current_time)
                    new_packets.append(packet)

            # 2. Random shuffle for fairness
            random.shuffle(new_packets)

            # 3. Edge and enqueue phase
            for packet in new_packets:
                # Edge node processing (remarking)
                self.edge_node.process(packet)
                # Core node enqueue (may drop if queue full)
                self.core_node.enqueue(packet)

            # 4. Service phase: serve one packet
            served_packet = self.core_node.serve()
            if served_packet:
                source = self.sources[served_packet.source_id]
                source.record_success(served_packet, self.current_time)

            self.current_time += 1

    def _all_sources_finished(self) -> bool:
        """Check if all sources have finished transmission.

        Returns:
            True if all sources have transmitted 1000 packets.
        """
        return all(source.is_finished() for source in self.sources)

    def print_results(self) -> None:
        """Print simulation results in tabular format."""
        # Print input patterns
        patterns_str = ', '.join(source.type for source in self.sources)
        print(f"Simulating for inputs: {patterns_str}")
        print("-" * 70)
        print(f"{'Source ID':<10} | {'Type':<4} | {'Completion Time':<15} | "
              f"{'Drop Rate (%)':<13} | {'Avg Latency':<11}")
        print("-" * 70)

        for source in self.sources:
            drop_rate = source.get_drop_rate()
            avg_latency = source.get_avg_latency()
            print(f"{source.id:<10} | {source.type:<4} | "
                  f"{source.completion_time:<15} | "
                  f"{drop_rate:<13.1f} | {avg_latency:<11.1f}")

        print("-" * 70)

    def get_results(self) -> List[dict]:
        """Get simulation results as a list of dictionaries.

        Returns:
            List of result dictionaries, one per source.
        """
        results = []
        for source in self.sources:
            results.append({
                'source_id': source.id,
                'type': source.type,
                'completion_time': source.completion_time,
                'drop_rate': source.get_drop_rate(),
                'avg_latency': source.get_avg_latency(),
                'packets_generated': source.packets_generated
            })
        return results
