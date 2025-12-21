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
    
    Time model:
    - Time step: 0.1 ms (discrete event simulation)
    - Sources generate packets every 1 ms (10 time steps)
    - Core node processes packets with 1 ms processing time

    Attributes:
        sources: List of traffic sources.
        edge_node: Edge node for traffic policing/remarking.
        core_node: Core node for priority queuing and scheduling.
        current_time: Current simulation time in ms.
        packets_in_transit_to_edge: Packets traveling from source to edge.
        packets_at_edge: Packets being processed at edge node.
        packets_in_transit_to_core: Packets traveling from edge to core.
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
        self.current_time = 0.0  # Time in ms
        
        # Track packets in various stages
        self.packets_at_src = [] # Packets being processed at source
        self.packets_at_edge = []  # Packets being processed at edge
        self.packets_in_transit_to_core = []  # Packets traveling to core
        self.packets_in_transit_to_dst = []  # Packets traveling from core to destination

    def run(self) -> None:
        """Run the simulation until all sources complete.

        The simulation continues until all sources have successfully
        transmitted 1000 packets each.
        
        Time step: 0.1 ms
        - Sources generate packets every 1 ms (10 time steps)
        - Edge processing: 1 ms (10 time steps)
        - Core processing: 1 ms (10 time steps)
        """
        TIME_STEP = 0.1  # ms
        GENERATION_INTERVAL = 1.0  # ms
        
        while not self._all_sources_finished():
            # 1. Packet generation phase (every 1ms)
            if abs(self.current_time % GENERATION_INTERVAL) < 1e-9:
                for source in self.sources:
                    if not source.is_finished():
                        packet = source.generate_packet(self.current_time)
                        # Packets arrive at edge after 1.1ms (transmission + propagation)
                        self.packets_at_src.append(packet)
                        # Shuffle packets at source to simulate random arrival order
                        random.shuffle(self.packets_at_src)
            # 2. Process packets that arrive at edge node
            packets_to_remove = []
            for packet in self.packets_at_src:
                if self.current_time >= packet.edge_arrival_time and packet.edge_complete_time is None:
                    # Edge receives packet
                    print(f"[Edge Receive] ID={packet.source_id}, Type={packet.current_type}, Time={self.current_time:.1f}ms")
                    # Process packet at edge node (remarking + set completion time)
                    self.edge_node.process(packet, self.current_time)

                elif packet.edge_complete_time is not None and self.current_time >= packet.edge_complete_time:
                    packets_to_remove.append(packet)
                    # Move to transit to core
                    self.packets_in_transit_to_core.append(packet)
                    # Edge sends packet
                    print(f"[Edge Send] ID={packet.source_id}, Type={packet.current_type}, Time={self.current_time:.1f}ms")
            
            for packet in packets_to_remove:
                self.packets_at_src.remove(packet)
            
            # 3. Process packets that arrive at core node
            packets_to_remove = []
            for packet in self.packets_in_transit_to_core:
                if self.current_time >= packet.core_arrival_time:
                    source = self.sources[packet.source_id]
                    # Check if source is already finished
                    if source.is_finished():
                        # Don't enqueue, discard packet and decrease generated count
                        source.decrease_generated()
                        packets_to_remove.append(packet)
                    else:
                        # Core receives packet
                        print(f"[Core Receive] ID={packet.source_id}, Type={packet.current_type}, Time={self.current_time:.1f}ms")
                        # Enqueue to core (may be dropped if full)
                        self.core_node.enqueue(packet)
                        packets_to_remove.append(packet)
            
            for packet in packets_to_remove:
                self.packets_in_transit_to_core.remove(packet)
            
            # 4. Core node service phase
            # Try to start serving if idle (pop and send immediately)
            # Check if any packet reached destination
            packets_to_remove = []
            for packet in self.packets_in_transit_to_dst:
                if abs(packet.reach_time - self.current_time) < 1e-9:
                    # Packet reaches destination
                    print(f"[Dst Reach] ID={packet.source_id}, Type={packet.current_type}, Time={self.current_time:.1f}ms")
                    # Record success
                    source = self.sources[packet.source_id]
                    source.record_success(packet, self.current_time)
                    packets_to_remove.append(packet)
            
            for packet in packets_to_remove:
                self.packets_in_transit_to_dst.remove(packet)

            served_packet = self.core_node.start_service(self.current_time,sources=self.sources)
            if served_packet is not None:
                # Core sends packet immediately after popping
                print(f"[Core Send] ID={served_packet.source_id}, Type={served_packet.current_type}, Time={self.current_time:.1f}ms")
                # Add to transit list for tracking reach time
                self.packets_in_transit_to_dst.append(served_packet)
            
            # Check if core service completed (can serve next packet)
            self.core_node.complete_service(self.current_time)

            # 5. Advance time
            self.current_time += TIME_STEP
            # Round to avoid floating point precision issues
            self.current_time = round(self.current_time, 1)
        
        # Clean up remaining packets after simulation completes
        self._cleanup_remaining_packets()

    def _cleanup_remaining_packets(self) -> None:
        """Clean up all remaining packets in the system and adjust generated counts."""
        # Clean up packets at edge
        for packet in self.packets_at_src:
            source = self.sources[packet.source_id]
            source.decrease_generated()
        self.packets_at_src.clear()

        # Clean up packets at edge
        for packet in self.packets_at_edge:
            source = self.sources[packet.source_id]
            source.decrease_generated()
        self.packets_at_edge.clear()
        
        # Clean up packets in transit to core
        for packet in self.packets_in_transit_to_core:
            source = self.sources[packet.source_id]
            source.decrease_generated()
        self.packets_in_transit_to_core.clear()
        
        # Clean up packets in transit to destination
        for packet in self.packets_in_transit_to_dst:
            source = self.sources[packet.source_id]
            source.decrease_generated()
        self.packets_in_transit_to_dst.clear()
        
        # Clean up packets in core node queues
        for packet in self.core_node.q_ef:
            source = self.sources[packet.source_id]
            source.decrease_generated()
        self.core_node.q_ef.clear()
        
        for packet in self.core_node.q_af:
            source = self.sources[packet.source_id]
            source.decrease_generated()
        self.core_node.q_af.clear()
        
        for packet in self.core_node.q_be:
            source = self.sources[packet.source_id]
            source.decrease_generated()
        self.core_node.q_be.clear()

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
