"""Configuration parameters for DiffServ simulation.

This file contains all configurable parameters for the simulation.
Users can modify these values to adjust the simulation behavior.
"""

# ============================================================================
# Time Parameters (in milliseconds)
# ============================================================================

# Discrete time step for simulation
TIME_STEP = 0.1  # ms

# Packet generation interval for each source
GENERATION_INTERVAL = 1.0  # ms


# ============================================================================
# Network Delay Parameters (in milliseconds)
# ============================================================================

# Source to Edge Node delays
SRC_TO_EDGE_TRANSMISSION_DELAY = 1.0  # ms
SRC_TO_EDGE_PROPAGATION_DELAY = 0.1  # ms

# Edge Node processing time
EDGE_PROCESSING_TIME = 1.0  # ms

# Edge Node to Core Node delays
EDGE_TO_CORE_TRANSMISSION_DELAY = 1.0  # ms
EDGE_TO_CORE_PROPAGATION_DELAY = 0.1  # ms

# Core Node processing time (time before can serve next packet)
CORE_PROCESSING_TIME = 2.0  # ms

# Core Node to Destination delays
CORE_TO_DST_TRANSMISSION_DELAY = 1.0  # ms
CORE_TO_DST_PROPAGATION_DELAY = 0.1  # ms


# ============================================================================
# Queue Capacity Parameters
# ============================================================================

# Core node queue capacities (in packets)
CORE_QUEUE_CAPACITY_EF = 1  # EF (Expedited Forwarding) queue
CORE_QUEUE_CAPACITY_AF = 1  # AF (Assured Forwarding) queue
CORE_QUEUE_CAPACITY_BE = 1  # BE (Best Effort) queue


# ============================================================================
# Traffic Policing Parameters
# ============================================================================

# Edge node remarking policy: every N-th AF packet is downgraded to BE
AF_REMARKING_INTERVAL = 5  # Every 5th AF packet -> BE


# ============================================================================
# Simulation Termination Parameters
# ============================================================================

# Number of successful packets needed for each source to complete
TARGET_SUCCESS_PACKETS = 1000
