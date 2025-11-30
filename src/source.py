"""Source class for DiffServ simulation."""

from typing import List
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

    TARGET_SUCCESS = 1000  # Number of successful packets needed to complete

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
        self.completion_time = 0
        self.latencies: List[int] = []

    def generate_packet(self, current_time: int) -> Packet:
        """Generate a new packet at the given time step.

        Args:
            current_time: The current simulation time step.

        Returns:
            A new Packet instance.
        """
        self.packets_generated += 1
        return Packet(self.id, self.type, current_time)

    def record_success(self, packet: Packet, service_time: int) -> None:
        """Record a successfully transmitted packet.

        Args:
            packet: The packet that was successfully transmitted.
            service_time: The time step when the packet was transmitted.
        """
        self.packets_success += 1
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
