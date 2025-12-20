"""Packet class for DiffServ simulation."""


class Packet:
    """Represents a network packet in the DiffServ simulation.

    Attributes:
        source_id: The ID of the source that generated this packet.
        original_type: The original service type (EF, AF, or BE).
        current_type: The current service type (may be modified by edge node).
        gen_time: The time step when this packet was generated.
    """

    def __init__(self, source_id: int, packet_type: str, gen_time: int):
        """Initialize a new packet.

        Args:
            source_id: The ID of the source generating this packet.
            packet_type: The service type ('EF', 'AF', or 'BE').
            gen_time: The time step when the packet is generated.
        """
        self.source_id = source_id
        self.original_type = packet_type
        self.current_type = packet_type
        self.gen_time = gen_time

    def __repr__(self) -> str:
        """Return a string representation of the packet."""
        return (f"Packet(source={self.source_id}, "
                f"type={self.current_type}, gen_time={self.gen_time})")
