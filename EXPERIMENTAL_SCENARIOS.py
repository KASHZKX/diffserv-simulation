"""
DiffServ QoS Experimental Scenarios
====================================

Author: Senior Network Engineer / QA Specialist
Date: December 21, 2025

This document defines 5 distinct experimental scenarios to validate DiffServ 
QoS performance. Each experiment tests specific aspects of the priority 
scheduling, queue management, and traffic policing mechanisms.

All parameters reference variables from src/config.py.
"""

# ============================================================================
# EXPERIMENT 1: BASELINE - Sanity Check
# ============================================================================

EXPERIMENT_1 = {
    "name": "Baseline - Low Traffic Sanity Check",
    "description": "Verify basic system functionality with low traffic and nominal parameters.",
    "objective": "Establish baseline metrics with minimal congestion.",
    
    "configuration": {
        # Time parameters
        "TIME_STEP": 0.1,                    # Keep nominal
        "GENERATION_INTERVAL": 1.0,          # Keep nominal
        
        # Queue capacities - GENEROUS to avoid drops
        "CORE_QUEUE_CAPACITY_EF": 100,       # Large buffer
        "CORE_QUEUE_CAPACITY_AF": 80,        # Large buffer
        "CORE_QUEUE_CAPACITY_BE": 60,        # Large buffer
        
        # Processing times - NOMINAL
        "EDGE_PROCESSING_TIME": 1.0,         # Standard
        "CORE_PROCESSING_TIME": 2.0,         # Standard
        
        # Network delays - NOMINAL
        "SRC_TO_EDGE_TRANSMISSION_DELAY": 1.0,
        "SRC_TO_EDGE_PROPAGATION_DELAY": 0.1,
        "EDGE_TO_CORE_TRANSMISSION_DELAY": 1.0,
        "EDGE_TO_CORE_PROPAGATION_DELAY": 0.1,
        "CORE_TO_DST_TRANSMISSION_DELAY": 1.0,
        "CORE_TO_DST_PROPAGATION_DELAY": 0.1,
        
        # Traffic policing
        "AF_REMARKING_INTERVAL": 5,          # Standard
        
        # Simulation
        "TARGET_SUCCESS_PACKETS": 100,       # Moderate run
    },
    
    "traffic_pattern": ["E", "A", "B"],      # One source of each type
    
    "hypothesis": {
        "expected_behavior": [
            "All packets should be delivered with near-zero drops",
            "EF should have lowest latency",
            "AF should have medium latency",
            "BE should have highest latency",
            "Clear priority differentiation should be visible",
        ],
        "expected_metrics": {
            "EF_drop_rate": "< 1%",
            "AF_drop_rate": "< 2%",
            "BE_drop_rate": "< 5%",
            "latency_ordering": "EF < AF < BE",
        }
    },
    
    "success_criteria": [
        "Zero or minimal packet loss (< 5% for any class)",
        "Latency follows strict priority: EF < AF < BE",
        "All sources complete successfully",
    ],
    
    "command": "python main.py --patterns E A B"
}


# ============================================================================
# EXPERIMENT 2: CONGESTION SATURATION - High Load Drop Testing
# ============================================================================

EXPERIMENT_2 = {
    "name": "Congestion Saturation - Drop Rate Analysis",
    "description": "Saturate the system with high traffic to test tail-drop and priority preservation.",
    "objective": "Verify that under congestion, lower-priority classes experience higher drops while EF is protected.",
    
    "configuration": {
        # Time parameters
        "TIME_STEP": 0.1,
        "GENERATION_INTERVAL": 1.0,          # Same rate as baseline
        
        # Queue capacities - VERY SMALL to force congestion
        "CORE_QUEUE_CAPACITY_EF": 5,         # Tiny EF queue
        "CORE_QUEUE_CAPACITY_AF": 3,         # Even smaller AF
        "CORE_QUEUE_CAPACITY_BE": 2,         # Smallest BE
        
        # Processing times - SLOWER to create bottleneck
        "EDGE_PROCESSING_TIME": 1.0,
        "CORE_PROCESSING_TIME": 5.0,         # SLOW processing → queue buildup
        
        # Network delays - nominal
        "SRC_TO_EDGE_TRANSMISSION_DELAY": 1.0,
        "SRC_TO_EDGE_PROPAGATION_DELAY": 0.1,
        "EDGE_TO_CORE_TRANSMISSION_DELAY": 1.0,
        "EDGE_TO_CORE_PROPAGATION_DELAY": 0.1,
        "CORE_TO_DST_TRANSMISSION_DELAY": 1.0,
        "CORE_TO_DST_PROPAGATION_DELAY": 0.1,
        
        # Traffic policing
        "AF_REMARKING_INTERVAL": 5,
        
        # Simulation
        "TARGET_SUCCESS_PACKETS": 200,       # More packets to observe patterns
    },
    
    "traffic_pattern": ["E", "E", "A", "A", "B", "B", "B"],  # Heavy mixed load
    
    "hypothesis": {
        "expected_behavior": [
            "Significant packet drops due to queue saturation",
            "BE should experience highest drop rate",
            "AF should have moderate drops (some remarked to BE)",
            "EF should have lowest drop rate (protected by priority)",
            "Drop rate ordering: BE > AF > EF",
        ],
        "expected_metrics": {
            "EF_drop_rate": "< 20%",
            "AF_drop_rate": "20-50%",
            "BE_drop_rate": "> 50%",
            "drop_ordering": "BE > AF > EF",
        }
    },
    
    "success_criteria": [
        "BE drop rate significantly higher than EF",
        "Priority preservation: EF packets are protected",
        "Tail-drop mechanism functions correctly",
        "System remains stable under overload",
    ],
    
    "command": "python main.py --patterns E E A A B B B"
}


# ============================================================================
# EXPERIMENT 3: BURSTY TRAFFIC - Token Bucket / Shaper Testing
# ============================================================================

EXPERIMENT_3 = {
    "name": "Bursty Traffic - AF Policing Behavior",
    "description": "Test AF remarking policy under bursty vs. constant traffic patterns.",
    "objective": "Validate that AF remarking (every 5th packet) effectively polices bursty AF traffic.",
    
    "configuration": {
        # Time parameters
        "TIME_STEP": 0.1,
        "GENERATION_INTERVAL": 1.0,
        
        # Queue capacities - MODERATE
        "CORE_QUEUE_CAPACITY_EF": 20,
        "CORE_QUEUE_CAPACITY_AF": 15,
        "CORE_QUEUE_CAPACITY_BE": 10,
        
        # Processing times - FAST to handle bursts
        "EDGE_PROCESSING_TIME": 0.5,         # Fast edge processing
        "CORE_PROCESSING_TIME": 1.0,         # Fast core processing
        
        # Network delays - LOW (LAN scenario)
        "SRC_TO_EDGE_TRANSMISSION_DELAY": 0.5,
        "SRC_TO_EDGE_PROPAGATION_DELAY": 0.05,
        "EDGE_TO_CORE_TRANSMISSION_DELAY": 0.5,
        "EDGE_TO_CORE_PROPAGATION_DELAY": 0.05,
        "CORE_TO_DST_TRANSMISSION_DELAY": 0.5,
        "CORE_TO_DST_PROPAGATION_DELAY": 0.05,
        
        # Traffic policing - TEST DIFFERENT VALUES
        "AF_REMARKING_INTERVAL": 3,          # MORE AGGRESSIVE: Every 3rd AF → BE
        
        # Simulation
        "TARGET_SUCCESS_PACKETS": 150,
    },
    
    "traffic_pattern": ["A", "A", "A", "A", "A"],  # Multiple AF sources (burst)
    
    "hypothesis": {
        "expected_behavior": [
            "1/3 of AF packets remarked to BE (due to AF_REMARKING_INTERVAL=3)",
            "Remarked packets experience degraded QoS",
            "AF sources compete for AF queue space",
            "Some AF traffic gets best-effort treatment",
        ],
        "expected_metrics": {
            "AF_drop_rate": "< 30%",
            "average_latency": "Higher than Exp1 due to remarking",
            "remarking_effect": "Visible latency increase for remarked packets",
        }
    },
    
    "success_criteria": [
        "AF remarking policy enforced correctly",
        "System handles burst of AF traffic",
        "Remarked packets (AF→BE) show degraded performance",
        "No system instability",
    ],
    
    "variations": {
        "aggressive_policing": {"AF_REMARKING_INTERVAL": 2},    # Every 2nd
        "lenient_policing": {"AF_REMARKING_INTERVAL": 10},      # Every 10th
    },
    
    "command": "python main.py --patterns A A A A A"
}


# ============================================================================
# EXPERIMENT 4: STARVATION TEST - Extreme Priority Load
# ============================================================================

EXPERIMENT_4 = {
    "name": "Starvation Test - Low Priority Starvation",
    "description": "Test if extreme high-priority (EF) load causes complete starvation of BE traffic.",
    "objective": "Verify strict priority scheduling and measure BE starvation under EF flood.",
    
    "configuration": {
        # Time parameters
        "TIME_STEP": 0.1,
        "GENERATION_INTERVAL": 1.0,
        
        # Queue capacities - ASYMMETRIC
        "CORE_QUEUE_CAPACITY_EF": 50,        # Large EF queue
        "CORE_QUEUE_CAPACITY_AF": 5,         # Small AF queue
        "CORE_QUEUE_CAPACITY_BE": 2,         # Tiny BE queue
        
        # Processing times - SLOW to emphasize priority
        "EDGE_PROCESSING_TIME": 1.0,
        "CORE_PROCESSING_TIME": 3.0,         # Slow processing
        
        # Network delays - nominal
        "SRC_TO_EDGE_TRANSMISSION_DELAY": 1.0,
        "SRC_TO_EDGE_PROPAGATION_DELAY": 0.1,
        "EDGE_TO_CORE_TRANSMISSION_DELAY": 1.0,
        "EDGE_TO_CORE_PROPAGATION_DELAY": 0.1,
        "CORE_TO_DST_TRANSMISSION_DELAY": 1.0,
        "CORE_TO_DST_PROPAGATION_DELAY": 0.1,
        
        # Traffic policing
        "AF_REMARKING_INTERVAL": 5,
        
        # Simulation
        "TARGET_SUCCESS_PACKETS": 100,
    },
    
    "traffic_pattern": ["E", "E", "E", "E", "E", "E", "B"],  # 6 EF vs 1 BE
    
    "hypothesis": {
        "expected_behavior": [
            "EF traffic dominates core node service",
            "BE traffic experiences severe starvation",
            "BE completion time >> EF completion time",
            "BE experiences extreme latency and drops",
            "System demonstrates strict priority (no fairness)",
        ],
        "expected_metrics": {
            "EF_completion_time": "Normal",
            "BE_completion_time": ">>> EF (orders of magnitude higher)",
            "BE_drop_rate": "> 80%",
            "BE_avg_latency": ">>> EF latency",
        }
    },
    
    "success_criteria": [
        "Clear evidence of BE starvation",
        "EF traffic unaffected by BE presence",
        "BE completion time is dramatically higher",
        "Demonstrates strict priority scheduling",
    ],
    
    "warning": "This scenario demonstrates BE starvation, which is expected behavior for strict priority scheduling without fairness mechanisms.",
    
    "command": "python main.py --patterns E E E E E E B"
}


# ============================================================================
# EXPERIMENT 5: HIGH LATENCY/JITTER - Delay Variation Analysis
# ============================================================================

EXPERIMENT_5 = {
    "name": "High Latency/Jitter - Queuing Delay Analysis",
    "description": "Create scenario with high queuing delays to observe latency variation (jitter).",
    "objective": "Measure jitter (latency variation) under different queue depths and processing rates.",
    
    "configuration": {
        # Time parameters
        "TIME_STEP": 0.1,
        "GENERATION_INTERVAL": 1.0,
        
        # Queue capacities - MEDIUM but constrained
        "CORE_QUEUE_CAPACITY_EF": 10,
        "CORE_QUEUE_CAPACITY_AF": 8,
        "CORE_QUEUE_CAPACITY_BE": 5,
        
        # Processing times - VARIABLE/SLOW
        "EDGE_PROCESSING_TIME": 2.0,         # Slow edge
        "CORE_PROCESSING_TIME": 4.0,         # Very slow core → high queuing
        
        # Network delays - HIGH (WAN scenario)
        "SRC_TO_EDGE_TRANSMISSION_DELAY": 5.0,      # High transmission delay
        "SRC_TO_EDGE_PROPAGATION_DELAY": 2.0,       # High propagation (long distance)
        "EDGE_TO_CORE_TRANSMISSION_DELAY": 5.0,
        "EDGE_TO_CORE_PROPAGATION_DELAY": 2.0,
        "CORE_TO_DST_TRANSMISSION_DELAY": 5.0,
        "CORE_TO_DST_PROPAGATION_DELAY": 2.0,
        
        # Traffic policing
        "AF_REMARKING_INTERVAL": 5,
        
        # Simulation
        "TARGET_SUCCESS_PACKETS": 100,
    },
    
    "traffic_pattern": ["E", "A", "A", "B", "B"],  # Mixed traffic with congestion
    
    "hypothesis": {
        "expected_behavior": [
            "High baseline latency due to propagation delays",
            "Variable queuing delays cause jitter",
            "EF has lowest jitter (priority service)",
            "BE has highest jitter (variable queue waiting)",
            "AF jitter is intermediate",
        ],
        "expected_metrics": {
            "EF_avg_latency": "High but consistent",
            "BE_avg_latency": "Very high with high variance",
            "latency_variance": "EF < AF < BE",
            "jitter_ordering": "EF < AF < BE",
        },
        "analysis_required": [
            "Calculate latency standard deviation for each class",
            "Plot latency distribution histograms",
            "Measure min, max, avg latency per class",
        ]
    },
    
    "success_criteria": [
        "Latency variation (jitter) is measurably higher for BE than EF",
        "EF shows more consistent latency",
        "High propagation delays reflected in all metrics",
        "Priority still preserved despite high delays",
    ],
    
    "command": "python main.py --patterns E A A B B",
    
    "post_analysis": {
        "metrics_to_calculate": [
            "Latency standard deviation per class",
            "Min/Max/Median latency per class",
            "Jitter (max latency - min latency)",
            "95th percentile latency",
        ],
        "visualization": [
            "Latency distribution histogram",
            "Box plot of latencies by class",
            "Time series of packet latencies",
        ]
    }
}


# ============================================================================
# EXPERIMENT EXECUTION GUIDE
# ============================================================================

EXECUTION_GUIDE = """
HOW TO RUN EXPERIMENTS
======================

Step 1: Modify config.py
-------------------------
For each experiment, update the parameters in src/config.py according to 
the "configuration" section above.

Step 2: Run Simulation
-----------------------
Execute the simulation with the specified traffic pattern:

    cd /home/kash/diffserv-simulation
    python main.py --patterns [PATTERN]

Where [PATTERN] is from the "command" field of each experiment.

Step 3: Collect Results
------------------------
The simulator outputs:
- Source ID
- Type (EF/AF/BE)
- Completion Time
- Drop Rate (%)
- Average Latency

Step 4: Analysis
----------------
Compare results against the "hypothesis" and "success_criteria" for each
experiment.

For Experiment 5 specifically, you may need to modify source.py to record
individual packet latencies for jitter analysis.


PARAMETER SUMMARY TABLE
=======================

| Parameter                          | Exp1   | Exp2   | Exp3   | Exp4   | Exp5   |
|------------------------------------|--------|--------|--------|--------|--------|
| CORE_QUEUE_CAPACITY_EF             | 100    | 5      | 20     | 50     | 10     |
| CORE_QUEUE_CAPACITY_AF             | 80     | 3      | 15     | 5      | 8      |
| CORE_QUEUE_CAPACITY_BE             | 60     | 2      | 10     | 2      | 5      |
| CORE_PROCESSING_TIME (ms)          | 2.0    | 5.0    | 1.0    | 3.0    | 4.0    |
| EDGE_PROCESSING_TIME (ms)          | 1.0    | 1.0    | 0.5    | 1.0    | 2.0    |
| AF_REMARKING_INTERVAL              | 5      | 5      | 3      | 5      | 5      |
| TARGET_SUCCESS_PACKETS             | 100    | 200    | 150    | 100    | 100    |
| Traffic Pattern                    | E A B  | EEAABBB| AAAAA  | EEEEEEB| EAABB  |
| Network Delays                     | Normal | Normal | Low    | Normal | High   |


KEY TUNABLE PARAMETERS IDENTIFIED
==================================

From code analysis, these are the key parameters that affect QoS:

1. Queue Capacities (CORE_QUEUE_CAPACITY_EF/AF/BE)
   - Controls buffer space for each priority class
   - Affects drop probability under load
   - Independent per-class configuration

2. Processing Times (CORE_PROCESSING_TIME, EDGE_PROCESSING_TIME)
   - Controls service rate
   - Affects throughput and queuing delays
   - Creates bottlenecks when too high

3. Network Delays (TRANSMISSION_DELAY, PROPAGATION_DELAY)
   - Affects baseline latency
   - Models different network scenarios (LAN vs WAN)
   - Impacts total end-to-end delay

4. AF Remarking Interval (AF_REMARKING_INTERVAL)
   - Controls traffic policing aggressiveness
   - Lower value = more AF packets downgraded to BE
   - Affects effective AF service rate

5. Generation Interval (GENERATION_INTERVAL)
   - Controls offered load
   - Lower value = higher traffic rate
   - Can create congestion when too low

6. Time Step (TIME_STEP)
   - Simulation granularity
   - Affects precision of timing measurements
   - Should be small relative to other timings

7. Target Success Packets (TARGET_SUCCESS_PACKETS)
   - Controls simulation duration
   - Higher value = better statistical significance
   - Affects total runtime


EXPECTED OUTCOMES SUMMARY
==========================

Experiment 1 (Baseline):
- Low drops, clear priority differentiation
- Validates basic DiffServ functionality

Experiment 2 (Congestion):
- High drops, especially for BE
- Tests priority preservation under overload
- Validates tail-drop policy

Experiment 3 (Bursty):
- Tests AF policing effectiveness
- Shows impact of remarking on QoS
- Validates edge node behavior

Experiment 4 (Starvation):
- Demonstrates strict priority (no fairness)
- BE severely degraded under EF load
- Expected behavior for DiffServ

Experiment 5 (Jitter):
- High latency variation for low-priority
- EF shows consistent performance
- Tests WAN scenario
"""


# ============================================================================
# EXPORT FOR PROGRAMMATIC ACCESS
# ============================================================================

ALL_EXPERIMENTS = [
    EXPERIMENT_1,
    EXPERIMENT_2,
    EXPERIMENT_3,
    EXPERIMENT_4,
    EXPERIMENT_5,
]


if __name__ == '__main__':
    # Print experiment summary
    print("=" * 80)
    print("DIFFSERV EXPERIMENTAL SCENARIOS")
    print("=" * 80)
    print()
    
    for i, exp in enumerate(ALL_EXPERIMENTS, 1):
        print(f"EXPERIMENT {i}: {exp['name']}")
        print(f"Objective: {exp['objective']}")
        print(f"Traffic Pattern: {' '.join(exp['traffic_pattern'])}")
        print(f"Command: {exp['command']}")
        print()
        print("Key Parameters:")
        for key in ['CORE_QUEUE_CAPACITY_EF', 'CORE_PROCESSING_TIME', 'AF_REMARKING_INTERVAL']:
            if key in exp['configuration']:
                print(f"  {key}: {exp['configuration'][key]}")
        print()
        print("-" * 80)
        print()
    
    print(EXECUTION_GUIDE)
