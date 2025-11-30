# DiffServ Simulation

A discrete-event simulator for Differentiated Services (DiffServ) network architecture, modeling packet flow through edge nodes (traffic policing/remarking) and core nodes (priority queuing).

## System Architecture

```
Sources (n sources) --> Edge Node (Remarker) --> Core Node (Scheduler) --> Destination
     |                        |                        |
     |                        |                        |
  Generate              Traffic Policing          Priority Queuing
  Packets               AF Remarking              Strict Priority
  (EF/AF/BE)            (every 5th AF→BE)         (EF > AF > BE)
```

### Components

1. **Sources**: Multiple independent traffic generators, each belonging to one service class:
   - **EF** (Expedited Forwarding): Highest priority
   - **AF** (Assured Forwarding): Medium priority (subject to remarking)
   - **BE** (Best Effort): Lowest priority

2. **Edge Node**: Traffic policing without buffering
   - Every 5th AF packet is downgraded to BE

3. **Core Node**: Bottleneck with limited buffers (total: 100 packets)
   - Q_EF capacity: 40 packets
   - Q_AF capacity: 30 packets
   - Q_BE capacity: 30 packets
   - Tail-drop policy when queue is full
   - Strict priority scheduling (1 packet/time step)

## Installation

```bash
# Clone the repository
git clone https://github.com/KASHZKX/diffserv-simulation.git
cd diffserv-simulation

# No external dependencies required (Python 3.6+)
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage with space-separated patterns
python main.py --patterns E A B A E

# Patterns as a single string
python main.py --patterns EABAE

# Using short option
python main.py -p E A B

# Get help
python main.py --help
```

### Pattern Types

| Pattern | Full Name | Priority | Description |
|---------|-----------|----------|-------------|
| E | Expedited Forwarding (EF) | High | Real-time traffic, served first |
| A | Assured Forwarding (AF) | Medium | Subject to remarking policy |
| B | Best Effort (BE) | Low | Served last, no guarantees |

## Output Format

```text
Simulating for inputs: EF, AF, BE, AF, EF
----------------------------------------------------------------------
Source ID  | Type | Completion Time | Drop Rate (%) | Avg Latency
----------------------------------------------------------------------
0          | EF   | 2015            | 50.4          | 38.3       
1          | AF   | 4030            | 75.2          | 80.9       
2          | BE   | 5095            | 80.4          | 118.4      
3          | AF   | 4065            | 75.4          | 68.6       
4          | EF   | 1970            | 49.3          | 38.2       
----------------------------------------------------------------------
```

### Metrics Explained

1. **Completion Time**: Time step when 1000th packet successfully transmitted
2. **Drop Rate**: `(packets_generated - 1000) / packets_generated × 100%`
3. **Average Latency**: Mean of `(service_time - generation_time)` for 1000 successful packets

## Project Structure

```
diffserv-simulation/
├── README.md              # Project documentation
├── main.py                # Entry point with CLI parsing
├── requirements.txt       # Dependencies (none required)
├── src/
│   ├── __init__.py        # Package initialization
│   ├── packet.py          # Packet class
│   ├── source.py          # Source class
│   ├── edge_node.py       # EdgeNode (Remarker) class
│   ├── core_node.py       # CoreNode (Scheduler) class
│   └── simulator.py       # Main simulator logic
└── tests/
    ├── __init__.py        # Test package
    ├── test_packet.py     # Packet unit tests
    ├── test_source.py     # Source unit tests (metrics calculation)
    ├── test_edge_node.py  # EdgeNode unit tests
    ├── test_core_node.py  # CoreNode unit tests
    └── test_simulator.py  # Integration tests
```

## Testing

Run all tests:
```bash
python -m unittest discover tests/ -v
```

### Test Coverage

- **Packet tests**: Packet creation, type modification, representation
- **Source tests**: Type normalization, packet generation, metrics calculation (drop rate, latency, completion time)
- **EdgeNode tests**: AF remarking logic (every 5th packet), EF/BE passthrough
- **CoreNode tests**: Queue management, tail-drop policy, strict priority scheduling
- **Simulator tests**: End-to-end integration with various traffic patterns

## Simulation Details

### Time Model
- Discrete time steps (t = 0, 1, 2, ...)
- Each active source generates 1 packet per time step
- Core node serves 1 packet per time step

### Termination Condition
- Each source completes when 1000 packets are successfully transmitted
- Simulation ends when all sources complete

### Fairness
- Packets from the same time step are randomly shuffled before processing
- This ensures no source has systematic advantage from processing order

## License

MIT License