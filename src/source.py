"""Source class for DiffServ simulation."""

from typing import List
from . import config
from .packet import Packet


class Source:
    """Represents a traffic source in the DiffServ simulation.

    Each source generates packets of a specific service type (EF, AF, or BE)
    and tracks statistics about generated and successfully transmitted packets.

    Attributes:
        id: Unique identifier for this source.
        type: Service type ('EF', 'AF', or 'BE').
        packets_generated: Total number of packets generated.
        packets_success: Number of packets successfully transmitted.
        completion_time: Time step when 1000th packet was transmitted.
        latencies: List of latencies for successfully transmitted packets.
    """

    TARGET_SUCCESS = config.TARGET_SUCCESS_PACKETS  # Number of successful packets needed to complete

    def __init__(self, source_id: int, source_type: str):
        """Initialize a new source.

        Args:
            source_id: Unique identifier for this source.
            source_type: Service type ('E'/'EF', 'A'/'AF', or 'B'/'BE').
        """
        self.id = source_id
        # Normalize type to full form
        type_map = {'E': 'EF', 'A': 'AF', 'B': 'BE'}
        self.type = type_map.get(source_type, source_type)
        self.packets_generated = 0
        self.packets_success = 0
        self.completion_time = 0.0
        self.latencies: List[float] = []

    def generate_packet(self, current_time: float) -> Packet:
        """Generate a new packet at the given time.

        Args:
            current_time: The current simulation time (ms).

        Returns:
            A new Packet instance.
        """
        self.packets_generated += 1
        
        packet = Packet(self.id, self.type, current_time)
        print(f"[Src send] ID={self.id}-{self.packets_generated}, Type={self.type}, Time={current_time:.1f}ms")
        return packet

    def record_success(self, packet: Packet, service_time: float) -> None:
        """Record a successfully transmitted packet.

        Args:
            packet: The packet that was successfully transmitted.
            service_time: The actual completion time (in ms) including all delays.
        """
        self.packets_success += 1
        # Total end-to-end latency calculation:
        # service_time already includes:
        # - src->edge: 1.1ms (added at packet creation)
        # - edge processing: 5ms (added at packet creation)
        # - edge->core: 1.1ms (added at packet creation)
        # - core queuing: dynamic (time difference in queue)
        # - core processing: 1ms (added at serve time)
        # - core transmission: 1ms (added at serve time)
        latency = service_time - packet.gen_time
        self.latencies.append(latency)
        if self.packets_success == self.TARGET_SUCCESS:
            self.completion_time = service_time

    def is_finished(self) -> bool:
        """Check if this source has completed transmission.

        Returns:
            True if 1000 packets have been successfully transmitted.
        """
        return self.packets_success >= self.TARGET_SUCCESS
    
    def decrease_generated(self) -> None:
        """Decrease the packets_generated count by 1.
        
        Used when a packet is discarded from the system.
        """
        if self.packets_generated > 0:
            self.packets_generated -= 1

    def get_drop_rate(self) -> float:
        """Calculate the packet drop rate.

        Returns:
            Drop rate as a percentage (0-100).
        """
        if self.packets_generated == 0:
            return 0.0
        dropped = self.packets_generated - self.packets_success
        return (dropped / self.packets_generated) * 100

    def get_avg_latency(self) -> float:
        """Calculate the average end-to-end latency.

        Returns:
            Average latency for successfully transmitted packets.
        """
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    def __repr__(self) -> str:
        """Return a string representation of the source."""
        return (f"Source(id={self.id}, type={self.type}, "
                f"success={self.packets_success}/{self.packets_generated})")
