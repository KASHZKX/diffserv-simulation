"""Comprehensive unit tests for DiffServ simulation refactored code.

This test suite covers:
1. Core DiffServ mechanisms (classification, queuing, scheduling)
2. Edge cases and boundary conditions
3. Configuration-driven behavior
4. Packet flow through the system

Author: Senior Network Engineer / QA Specialist
"""

import pytest
import sys
sys.path.insert(0, '../src')

from src.packet import Packet
from src.source import Source
from src.edge_node import EdgeNode
from src.core_node import CoreNode
from src.simulator import Simulator
from src import config


# ============================================================================
# PACKET CLASS TESTS
# ============================================================================

class TestPacketTimingCalculations:
    """Test packet timing calculations based on config."""
    
    def test_packet_timing_chain(self):
        """Test complete timing chain from source to edge."""
        gen_time = 0.0
        packet = Packet(source_id=0, packet_type='EF', gen_time=gen_time)
        
        # Verify timing chain
        expected_edge_arrival = (gen_time + 
                                config.SRC_TO_EDGE_TRANSMISSION_DELAY + 
                                config.SRC_TO_EDGE_PROPAGATION_DELAY)
        
        assert packet.edge_arrival_time == expected_edge_arrival
        assert packet.gen_time == gen_time
    
    def test_packet_timing_with_nonzero_start(self):
        """Test timing calculations with non-zero start time."""
        gen_time = 100.0
        packet = Packet(source_id=1, packet_type='AF', gen_time=gen_time)
        
        assert packet.edge_arrival_time == gen_time + 1.1
        assert packet.gen_time == 100.0


class TestPacketAttributes:
    """Test packet attribute management."""
    
    def test_packet_immutable_attributes(self):
        """Test that certain attributes should not change."""
        packet = Packet(source_id=5, packet_type='AF', gen_time=10.0)
        
        # Original attributes should be immutable
        original_id = packet.source_id
        original_gen = packet.gen_time
        original_type = packet.original_type
        
        # Even if current_type changes
        packet.current_type = 'BE'
        
        assert packet.source_id == original_id
        assert packet.gen_time == original_gen
        assert packet.original_type == original_type
    
    def test_packet_remarking_preserves_history(self):
        """Test that remarking preserves original type."""
        packet = Packet(source_id=0, packet_type='AF', gen_time=0.0)
        
        # Simulate multiple remarkings
        packet.current_type = 'BE'
        packet.current_type = 'EF'
        
        assert packet.original_type == 'AF'


# ============================================================================
# EDGE NODE TESTS
# ============================================================================

class TestEdgeNodeRemarking:
    """Test edge node remarking policy."""
    
    def test_af_remarking_policy(self):
        """Test AF remarking at configured interval."""
        edge = EdgeNode()
        packets = []
        
        # Generate AF packets
        for i in range(config.AF_REMARKING_INTERVAL + 2):
            packet = Packet(source_id=0, packet_type='AF', gen_time=float(i))
            edge.process(packet, current_time=float(i))
            packets.append(packet)
        
        # Check remarking pattern
        for i, packet in enumerate(packets):
            if (i + 1) % config.AF_REMARKING_INTERVAL == 0:
                assert packet.current_type == 'BE', f"Packet {i+1} should be remarked"
            else:
                assert packet.current_type == 'AF', f"Packet {i+1} should remain AF"
    
    def test_ef_not_remarked(self):
        """Test that EF packets are never remarked."""
        edge = EdgeNode()
        
        for i in range(10):
            packet = Packet(source_id=0, packet_type='EF', gen_time=float(i))
            edge.process(packet, current_time=float(i))
            assert packet.current_type == 'EF'
    
    def test_be_not_remarked(self):
        """Test that BE packets are never remarked."""
        edge = EdgeNode()
        
        for i in range(10):
            packet = Packet(source_id=0, packet_type='BE', gen_time=float(i))
            edge.process(packet, current_time=float(i))
            assert packet.current_type == 'BE'
    
    def test_edge_sets_timing_fields(self):
        """Test that edge node sets timing fields correctly."""
        edge = EdgeNode()
        packet = Packet(source_id=0, packet_type='EF', gen_time=0.0)
        current_time = packet.edge_arrival_time
        
        edge.process(packet, current_time=current_time)
        
        # Check that timing fields are set
        assert packet.edge_complete_time is not None
        assert packet.core_arrival_time is not None
        
        # Verify timing calculations
        expected_complete = (packet.edge_arrival_time + 
                           config.EDGE_PROCESSING_TIME)
        expected_core_arrival = (packet.edge_complete_time + 
                                config.EDGE_TO_CORE_TRANSMISSION_DELAY + 
                                config.EDGE_TO_CORE_PROPAGATION_DELAY)
        
        assert packet.edge_complete_time == expected_complete
        assert packet.core_arrival_time == expected_core_arrival


class TestEdgeNodeCounters:
    """Test edge node counter management."""
    
    def test_af_counter_increments(self):
        """Test that AF counter increments correctly."""
        edge = EdgeNode()
        assert edge.af_counter == 0
        
        for i in range(5):
            packet = Packet(source_id=0, packet_type='AF', gen_time=float(i))
            edge.process(packet, current_time=float(i))
        
        assert edge.af_counter == 5
    
    def test_af_counter_not_affected_by_other_types(self):
        """Test that non-AF packets don't affect AF counter."""
        edge = EdgeNode()
        
        # Process EF and BE packets
        for pkt_type in ['EF', 'BE']:
            for i in range(3):
                packet = Packet(source_id=0, packet_type=pkt_type, gen_time=float(i))
                edge.process(packet, current_time=float(i))
        
        assert edge.af_counter == 0


# ============================================================================
# CORE NODE TESTS
# ============================================================================

class TestCoreNodeQueuing:
    """Test core node queuing mechanisms."""
    
    def test_enqueue_to_correct_queue(self):
        """Test packets are enqueued to correct priority queues."""
        core = CoreNode()
        
        ef_packet = Packet(source_id=0, packet_type='EF', gen_time=0.0)
        af_packet = Packet(source_id=1, packet_type='AF', gen_time=0.0)
        be_packet = Packet(source_id=2, packet_type='BE', gen_time=0.0)
        
        core.enqueue(ef_packet)
        core.enqueue(af_packet)
        core.enqueue(be_packet)
        
        assert len(core.q_ef) == 1
        assert len(core.q_af) == 1
        assert len(core.q_be) == 1
    
    def test_tail_drop_policy(self):
        """Test tail-drop when queue is full."""
        core = CoreNode(capacity_ef=2, capacity_af=2, capacity_be=2)
        
        # Fill EF queue
        for i in range(3):
            packet = Packet(source_id=0, packet_type='EF', gen_time=float(i))
            result = core.enqueue(packet)
            if i < 2:
                assert result == True
            else:
                assert result == False  # Third packet should be dropped
        
        assert len(core.q_ef) == 2
    
    def test_queue_independence(self):
        """Test that queues are independent (one full doesn't affect others)."""
        core = CoreNode(capacity_ef=1, capacity_af=1, capacity_be=1)
        
        # Fill EF queue
        ef1 = Packet(source_id=0, packet_type='EF', gen_time=0.0)
        ef2 = Packet(source_id=0, packet_type='EF', gen_time=0.0)
        core.enqueue(ef1)
        assert core.enqueue(ef2) == False  # EF full
        
        # AF should still accept packets
        af1 = Packet(source_id=1, packet_type='AF', gen_time=0.0)
        assert core.enqueue(af1) == True


class TestCoreNodeStrictPriority:
    """Test strict priority scheduling."""
    
    def test_strict_priority_ef_over_af(self):
        """Test EF is served before AF."""
        core = CoreNode()
        
        # Enqueue in reverse priority order
        be_packet = Packet(source_id=0, packet_type='BE', gen_time=0.0)
        af_packet = Packet(source_id=1, packet_type='AF', gen_time=0.0)
        ef_packet = Packet(source_id=2, packet_type='EF', gen_time=0.0)
        
        core.enqueue(be_packet)
        core.enqueue(af_packet)
        core.enqueue(ef_packet)
        
        # EF should be served first
        served = core.start_service(current_time=0.0, sources=None)
        assert served.source_id == 2
        assert served.current_type == 'EF'
    
    def test_strict_priority_af_over_be(self):
        """Test AF is served before BE when no EF."""
        core = CoreNode()
        
        be_packet = Packet(source_id=0, packet_type='BE', gen_time=0.0)
        af_packet = Packet(source_id=1, packet_type='AF', gen_time=0.0)
        
        core.enqueue(be_packet)
        core.enqueue(af_packet)
        
        served = core.start_service(current_time=0.0, sources=None)
        assert served.source_id == 1
        assert served.current_type == 'AF'
    
    def test_fifo_within_priority(self):
        """Test FIFO ordering within same priority."""
        core = CoreNode()
         # Increase capacity for test
        core.capacity_ef = 10 

        source0 = Source(1, 'EF')
        source1 = Source(2, 'EF')
        source2 = Source(3, 'EF')
        # # Prevent finishing
        # source.TARGET_SUCCESS = 100  
        # source.packets_success = 0
        sources = [source0,source1,source2]
        # Enqueue multiple EF packets
        for i in range(3):
            packet = Packet(source_id=i, packet_type='EF', gen_time=float(i))
            core.enqueue(packet)
        print(len(core.q_ef), "packets in EF queue")        
        # Should be served in order
        for i in range(3):
            served = core.start_service(current_time=float(i * 10), sources=sources)
            core.service_complete_time = float(i * 10 + 5)  # Simulate completion
            core.complete_service(current_time=float(i * 10 + 10))
            print(f"Served packet: {served}")
            assert served.source_id == i


class TestCoreNodeServiceTiming:
    """Test core node service timing."""
    
    def test_service_timing_constraints(self):
        """Test that core respects processing time before next service."""
        core = CoreNode()
         # Increase capacity for test
        core.capacity_ef = 10 
        
        source0 = Source(0, 'EF')
        source1 = Source(1, 'EF')   
        sources = [source0,source1]    
        # Enqueue two packets
        p1 = Packet(source_id=0, packet_type='EF', gen_time=0.0)
        p2 = Packet(source_id=1, packet_type='EF', gen_time=0.0)
        core.enqueue(p1)
        core.enqueue(p2)
        
        # Start first service at t=0
        served1 = core.start_service(current_time=0.0, sources=sources)
        assert served1 is not None
        
        # Try to start second service immediately (should fail)
        served2 = core.start_service(current_time=0.0, sources=sources)
        assert served2 is None
        
        # Complete first service
        assert core.complete_service(current_time=config.CORE_PROCESSING_TIME) is True
        
        # Now second service should succeed
        served2 = core.start_service(current_time=config.CORE_PROCESSING_TIME, sources=sources)
        assert served2 is not None
    
    def test_reach_time_calculation(self):
        """Test that packet reach time is calculated correctly."""
        core = CoreNode()
        
        packet = Packet(source_id=0, packet_type='EF', gen_time=0.0)
        core.enqueue(packet)
        
        current_time = 10.0
        served = core.start_service(current_time=current_time, sources=None)
        
        expected_reach = (current_time + 
                         config.CORE_TO_DST_TRANSMISSION_DELAY + 
                         config.CORE_TO_DST_PROPAGATION_DELAY)
        
        assert served.reach_time == expected_reach


class TestCoreNodeFinishedSourceHandling:
    """Test handling of packets from finished sources."""
    
    def test_skip_packets_from_finished_sources(self):
        """Test that packets from finished sources are skipped."""
        # Create sources
        source0 = Source(source_id=0, source_type='EF')
        source1 = Source(source_id=1, source_type='EF')
        
        # Mark source0 as finished
        for _ in range(config.TARGET_SUCCESS_PACKETS):
            p = Packet(source_id=0, packet_type='EF', gen_time=0.0)
            source0.record_success(p, service_time=10.0)
        
        # Enqueue packets from both sources
        core = CoreNode()
        # Increase capacity for test
        core.capacity_ef = 10             
        
        p0 = Packet(source_id=0, packet_type='EF', gen_time=0.0)
        p1 = Packet(source_id=1, packet_type='EF', gen_time=0.0)
        
        core.enqueue(p0)  # From finished source
        core.enqueue(p1)  # From active source
        
        # Should skip p0 and serve p1
        sources = [source0, source1]
        served = core.start_service(current_time=0.0, sources=sources)
        
        assert served.source_id == 1


# ============================================================================
# SOURCE CLASS TESTS
# ============================================================================

class TestSourceMetrics:
    """Test source metrics calculation accuracy."""
    
    def test_drop_rate_accuracy(self):
        """Test drop rate calculation with various scenarios."""
        test_cases = [
            (100, 100, 0.0),    # No drops
            (100, 50, 50.0),    # 50% drops
            (100, 90, 10.0),    # 10% drops
            (10, 1, 90.0),      # 90% drops
        ]
        
        for generated, success, expected_rate in test_cases:
            source = Source(source_id=0, source_type='EF')
            source.packets_generated = generated
            source.packets_success = success
            
            assert source.get_drop_rate() == expected_rate
    
    def test_latency_statistics(self):
        """Test latency statistics calculation."""
        source = Source(source_id=0, source_type='EF')
        
        # Add various latencies
        latencies = [5.0, 10.0, 15.0, 20.0, 25.0]
        for lat in latencies:
            packet = Packet(source_id=0, packet_type='EF', gen_time=0.0)
            source.record_success(packet, service_time=lat)
        
        avg_latency = source.get_avg_latency()
        assert avg_latency == 15.0  # Mean of latencies
    
    def test_completion_time_accuracy(self):
        """Test that completion time is recorded at exact target."""
        source = Source(source_id=0, source_type='EF')
        
        # Record successes up to target - 1
        for i in range(config.TARGET_SUCCESS_PACKETS - 1):
            packet = Packet(source_id=0, packet_type='EF', gen_time=0.0)
            source.record_success(packet, service_time=10.0 * i)
        
        # Completion time should still be 0
        assert source.completion_time == 0.0
        
        # Record final packet
        final_packet = Packet(source_id=0, packet_type='EF', gen_time=0.0)
        final_time = 999.9
        source.record_success(final_packet, service_time=final_time)
        
        # Now completion time should be set
        assert source.completion_time == final_time


# ============================================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_queue_service_attempt(self):
        """Test attempting to serve from empty queue."""
        core = CoreNode()
        served = core.start_service(current_time=0.0, sources=None)
        assert served is None
    
    def test_zero_capacity_queue(self):
        """Test queue with zero capacity."""
        core = CoreNode(capacity_ef=0, capacity_af=0, capacity_be=0)
        
        packet = Packet(source_id=0, packet_type='EF', gen_time=0.0)
        result = core.enqueue(packet)
        
        assert result == False
        assert len(core.q_ef) == 0
    
    def test_single_packet_flow(self):
        """Test single packet flowing through system."""
        edge = EdgeNode()
        core = CoreNode()
        
        packet = Packet(source_id=0, packet_type='EF', gen_time=0.0)
        
        # Process through edge
        edge.process(packet, current_time=packet.edge_arrival_time)
        
        # Enqueue to core
        result = core.enqueue(packet)
        assert result == True
        
        # Serve from core
        served = core.start_service(current_time=10.0, sources=None)
        assert served is not None
        assert served.source_id == 0
    
    def test_large_number_of_packets(self):
        """Test system with large number of packets."""
        core = CoreNode(capacity_ef=1000, capacity_af=1000, capacity_be=1000)
        
        # Enqueue 1000 packets
        for i in range(1000):
            packet = Packet(source_id=i % 10, packet_type='EF', gen_time=float(i))
            result = core.enqueue(packet)
            assert result == True
        
        assert len(core.q_ef) == 1000


class TestConfigurationDriven:
    """Test that behavior is driven by configuration."""
    
    def test_af_remarking_respects_config(self):
        """Test that AF remarking uses config value."""
        edge = EdgeNode()
        
        # Process exactly config.AF_REMARKING_INTERVAL packets
        remarked_count = 0
        for i in range(config.AF_REMARKING_INTERVAL * 2):
            packet = Packet(source_id=0, packet_type='AF', gen_time=float(i))
            edge.process(packet, current_time=float(i))
            if packet.current_type == 'BE':
                remarked_count += 1
        
        # Should have remarked exactly 2 packets
        expected_remarkings = 2
        assert remarked_count == expected_remarkings
    
    def test_queue_capacities_respect_config(self):
        """Test that queue capacities match config."""
        core = CoreNode()  # Uses default from config
        
        assert core.capacity_ef == config.CORE_QUEUE_CAPACITY_EF
        assert core.capacity_af == config.CORE_QUEUE_CAPACITY_AF
        assert core.capacity_be == config.CORE_QUEUE_CAPACITY_BE
    
    def test_timing_respects_config(self):
        """Test that timing calculations use config values."""
        packet = Packet(source_id=0, packet_type='EF', gen_time=0.0)
        
        expected = (0.0 + 
                   config.SRC_TO_EDGE_TRANSMISSION_DELAY + 
                   config.SRC_TO_EDGE_PROPAGATION_DELAY)
        
        assert packet.edge_arrival_time == expected


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
