"""Edge Node (Remarker) class for DiffServ simulation."""

from . import config
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

    def process(self, packet: Packet, current_time: float) -> None:
        """Process a packet through the edge node.

        Applies remarking policy:
        - AF packets: Every 5th AF packet is downgraded to BE.
        - EF and BE packets: Pass through unchanged.
        Sets edge processing completion time.

        Args:
            packet: The packet to process.
            current_time: Current simulation time (ms).
        """
        if packet.current_type == 'AF':
            self.af_counter += 1
            # Downgrade every N-th AF packet to BE (based on config)
            if self.af_counter % config.AF_REMARKING_INTERVAL == 0:
                packet.current_type = 'BE'
        
        # Edge processing time (from config)
        packet.edge_complete_time = packet.edge_arrival_time + config.EDGE_PROCESSING_TIME
        # After edge processing, packet travels to core
        packet.core_arrival_time = packet.edge_complete_time + config.EDGE_TO_CORE_TRANSMISSION_DELAY + config.EDGE_TO_CORE_PROPAGATION_DELAY

    def __repr__(self) -> str:
        """Return a string representation of the edge node."""
        return f"EdgeNode(af_counter={self.af_counter})"
