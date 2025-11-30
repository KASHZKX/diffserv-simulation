"""Core Node (Scheduler) class for DiffServ simulation."""

from typing import Optional, List
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

    def __init__(self, capacity_ef: int = 40, capacity_af: int = 30,
                 capacity_be: int = 30):
        """Initialize the core node with queue capacities.

        Args:
            capacity_ef: Maximum capacity of EF queue.
            capacity_af: Maximum capacity of AF queue.
            capacity_be: Maximum capacity of BE queue.
        """
        self.q_ef: List[Packet] = []
        self.q_af: List[Packet] = []
        self.q_be: List[Packet] = []
        self.capacity_ef = capacity_ef
        self.capacity_af = capacity_af
        self.capacity_be = capacity_be

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

    def serve(self) -> Optional[Packet]:
        """Serve one packet using strict priority scheduling.

        Priority order: EF > AF > BE.
        Only one packet is served per time step.

        Returns:
            The served packet, or None if all queues are empty.
        """
        if self.q_ef:
            return self.q_ef.pop(0)
        elif self.q_af:
            return self.q_af.pop(0)
        elif self.q_be:
            return self.q_be.pop(0)
        return None

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
