"""Packet class for DiffServ simulation."""

from . import config


class Packet:
    """Represents a network packet in the DiffServ simulation.

    Attributes:
        source_id: The ID of the source that generated this packet.
        original_type: The original service type (EF, AF, or BE).
        current_type: The current service type (may be modified by edge node).
        gen_time: The time when this packet was generated (ms).
        edge_arrival_time: Time when packet arrives at edge node (ms).
        edge_complete_time: Time when edge node completes processing (ms).
        core_arrival_time: Time when packet arrives at core node (ms).
        core_service_start_time: Time when core node starts serving (ms).
        core_service_end_time: Time when core node completes serving (ms).
    """

    def __init__(self, source_id: int, packet_type: str, gen_time: float):
        """Initialize a new packet.

        Args:
            source_id: The ID of the source generating this packet.
            packet_type: The service type ('EF', 'AF', or 'BE').
            gen_time: The time when the packet is generated (ms).
        """
        self.source_id = source_id
        self.original_type = packet_type
        self.current_type = packet_type
        self.gen_time = gen_time
        
        # Calculate arrival times based on config
        self.edge_arrival_time = gen_time + config.SRC_TO_EDGE_TRANSMISSION_DELAY + config.SRC_TO_EDGE_PROPAGATION_DELAY
        self.edge_complete_time = None
        self.core_arrival_time = None
        self.core_service_start_time = None
        self.reach_time = None  # Time when packet reaches destination (ms)

    def __repr__(self) -> str:
        """Return a string representation of the packet."""
        return (f"Packet(source={self.source_id}, "
                f"type={self.current_type}, gen_time={self.gen_time})")
