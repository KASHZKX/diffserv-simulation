"""Edge Node (Remarker) class for DiffServ simulation."""

from .packet import Packet


class EdgeNode:
    """Edge node that performs traffic policing and remarking.

    The edge node monitors AF traffic and downgrades every 5th AF packet
    to BE (Best Effort) service level. EF and BE packets pass through
    unchanged.

    Attributes:
        af_counter: Counter for AF packets processed.
    """

    def __init__(self):
        """Initialize the edge node."""
        self.af_counter = 0

    def process(self, packet: Packet) -> None:
        """Process a packet through the edge node.

        Applies remarking policy:
        - AF packets: Every 5th AF packet is downgraded to BE.
        - EF and BE packets: Pass through unchanged.

        Args:
            packet: The packet to process.
        """
        if packet.current_type == 'AF':
            self.af_counter += 1
            # Downgrade every 5th AF packet to BE
            if self.af_counter % 5 == 0:
                packet.current_type = 'BE'

    def __repr__(self) -> str:
        """Return a string representation of the edge node."""
        return f"EdgeNode(af_counter={self.af_counter})"
