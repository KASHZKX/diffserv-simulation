"""Core Node (Scheduler) class for DiffServ simulation."""

from typing import Optional, List
from . import config
from .packet import Packet


class CoreNode:
    """Core node that performs priority-based queuing and scheduling.

    The core node maintains three separate queues for different service
    types (EF, AF, BE) with strict priority scheduling.

    Attributes:
        q_ef: Queue for EF (Expedited Forwarding) packets.
        q_af: Queue for AF (Assured Forwarding) packets.
        q_be: Queue for BE (Best Effort) packets.
        capacity_ef: Maximum capacity of EF queue (default: 40).
        capacity_af: Maximum capacity of AF queue (default: 30).
        capacity_be: Maximum capacity of BE queue (default: 30).
    """

    def __init__(self, capacity_ef: int = None, capacity_af: int = None,
                 capacity_be: int = None):
        """Initialize the core node with queue capacities.

        Args:
            capacity_ef: Maximum capacity of EF queue (default from config).
            capacity_af: Maximum capacity of AF queue (default from config).
            capacity_be: Maximum capacity of BE queue (default from config).
        """
        self.q_ef: List[Packet] = []
        self.q_af: List[Packet] = []
        self.q_be: List[Packet] = []
        self.capacity_ef = capacity_ef if capacity_ef is not None else config.CORE_QUEUE_CAPACITY_EF
        self.capacity_af = capacity_af if capacity_af is not None else config.CORE_QUEUE_CAPACITY_AF
        self.capacity_be = capacity_be if capacity_be is not None else config.CORE_QUEUE_CAPACITY_BE
        self.serving_packet: Optional[Packet] = None
        self.service_complete_time: Optional[float] = None

    def enqueue(self, packet: Packet) -> bool:
        """Attempt to enqueue a packet into the appropriate queue.

        Uses tail-drop policy: if the queue is full, the packet is dropped.

        Args:
            packet: The packet to enqueue.

        Returns:
            True if the packet was successfully enqueued, False if dropped.
        """
        pkt_type = packet.current_type

        if pkt_type == 'EF':
            if len(self.q_ef) < self.capacity_ef:
                self.q_ef.append(packet)
                return True
        elif pkt_type == 'AF':
            if len(self.q_af) < self.capacity_af:
                self.q_af.append(packet)
                return True
        elif pkt_type == 'BE':
            if len(self.q_be) < self.capacity_be:
                self.q_be.append(packet)
                return True

        return False  # Packet dropped (tail drop)

    def start_service(self, current_time: float, sources=None) -> Optional[Packet]:
        """Start serving a packet if not already serving.

        Priority order: EF > AF > BE.
        Processing time: 1ms (core must wait 1ms before next service).
        Transmission delay: 1.1ms (1ms transmission + 0.1ms propagation).

        Args:
            current_time: Current simulation time (ms).
            sources: List of sources to check if finished (optional).

        Returns:
            The packet that was popped and sent, or None if no packet available.
        """
        if self.serving_packet is not None and not abs(self.service_complete_time - current_time) < 1e-9:
            return None
        
        packet = None
        # Keep popping packets until we find one from an unfinished source
        while True:
            
            # Pop packet with priority: EF > AF > BE
            if self.q_ef:
                packet = self.q_ef.pop(0)
            elif self.q_af:
                packet = self.q_af.pop(0)
            elif self.q_be:
                packet = self.q_be.pop(0)
            else:
                # No more packets in any queue
                packet = None
                break
            # Check if the source is already finished (sources must be provided)
            if sources:
                source = sources[packet.source_id]
                if source.is_finished():
                    # Discard this packet and decrease generated count
                    source.decrease_generated()
                    # Continue loop to pop next packet
                    continue
                else:
                    # Found a packet from unfinished source
                    break
            else:
                # No source check, use the packet as is
                break
        
        if packet:
            packet.core_service_start_time = current_time
            # Packet reaches destination after transmission + propagation (from config)
            packet.reach_time = current_time + config.CORE_TO_DST_TRANSMISSION_DELAY + config.CORE_TO_DST_PROPAGATION_DELAY
            # Core must wait processing time before servicing next packet (from config)
            self.service_complete_time = current_time + config.CORE_PROCESSING_TIME
            self.serving_packet = packet
            return packet
        return None
    
    def complete_service(self, current_time: float) -> bool:
        """Complete serving a packet if service time is reached.

        Args:
            current_time: Current simulation time (ms).

        Returns:
            The completed packet, or None if no packet ready.
        """
        if self.serving_packet is None:
            return False
        
        if current_time >= self.service_complete_time:
            self.serving_packet = None
            self.service_complete_time = None
            return True
        return False

    def get_queue_sizes(self) -> dict:
        """Get current queue sizes.

        Returns:
            Dictionary with queue sizes for each service type.
        """
        return {
            'EF': len(self.q_ef),
            'AF': len(self.q_af),
            'BE': len(self.q_be)
        }

    def __repr__(self) -> str:
        """Return a string representation of the core node."""
        return (f"CoreNode(EF={len(self.q_ef)}/{self.capacity_ef}, "
                f"AF={len(self.q_af)}/{self.capacity_af}, "
                f"BE={len(self.q_be)}/{self.capacity_be})")
