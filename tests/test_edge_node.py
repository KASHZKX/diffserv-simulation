"""Unit tests for EdgeNode class."""

import unittest
from src.edge_node import EdgeNode
from src.packet import Packet
from src import config


class TestEdgeNode(unittest.TestCase):
    """Test cases for EdgeNode remarking logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.edge = EdgeNode()

    def test_initial_state(self):
        """Test initial state of edge node."""
        self.assertEqual(self.edge.af_counter, 0)

    def test_ef_packets_pass_unchanged(self):
        """Test that EF packets pass through without modification."""
        for i in range(10):
            packet = Packet(0, 'EF', gen_time=float(i))
            self.edge.process(packet, current_time=float(i) + 1.1)
            
            self.assertEqual(packet.current_type, 'EF')
            self.assertEqual(packet.original_type, 'EF')

        # AF counter should not change
        self.assertEqual(self.edge.af_counter, 0)

    def test_be_packets_pass_unchanged(self):
        """Test that BE packets pass through without modification."""
        for i in range(10):
            packet = Packet(0, 'BE', gen_time=float(i))
            self.edge.process(packet, current_time=float(i) + 1.1)
            
            self.assertEqual(packet.current_type, 'BE')
            self.assertEqual(packet.original_type, 'BE')

        # AF counter should not change
        self.assertEqual(self.edge.af_counter, 0)

    def test_af_remarking_every_nth(self):
        """Test that every N-th AF packet is downgraded to BE."""
        interval = config.AF_REMARKING_INTERVAL
        results = []
        
        for i in range(interval * 4):  # Test 4 cycles
            packet = Packet(0, 'AF', gen_time=float(i))
            self.edge.process(packet, current_time=float(i) + 1.1)
            results.append(packet.current_type)

        # Every interval-th packet should be BE
        for i, pkt_type in enumerate(results):
            if (i + 1) % interval == 0:
                self.assertEqual(pkt_type, 'BE', f"Packet {i+1} should be BE")
            else:
                self.assertEqual(pkt_type, 'AF', f"Packet {i+1} should be AF")

    def test_af_counter_increments(self):
        """Test that AF counter increments correctly."""
        self.assertEqual(self.edge.af_counter, 0)

        for i in range(7):
            packet = Packet(0, 'AF', gen_time=float(i))
            self.edge.process(packet, current_time=float(i) + 1.1)

        self.assertEqual(self.edge.af_counter, 7)

    def test_mixed_traffic_af_counter(self):
        """Test AF counter only counts AF packets in mixed traffic."""
        packets = [
            ('EF', 0.0),
            ('AF', 1.0),
            ('BE', 2.0),
            ('AF', 3.0),
            ('EF', 4.0),
            ('AF', 5.0),
        ]

        for pkt_type, gen_time in packets:
            packet = Packet(0, pkt_type, gen_time)
            self.edge.process(packet, current_time=gen_time + 1.1)

        # Only 3 AF packets
        self.assertEqual(self.edge.af_counter, 3)

    def test_original_type_preserved_after_remarking(self):
        """Test that original_type is preserved after remarking."""
        interval = config.AF_REMARKING_INTERVAL
        
        for i in range(interval):
            packet = Packet(0, 'AF', gen_time=float(i))
            self.edge.process(packet, current_time=float(i) + 1.1)
            
            # Original type should always be AF
            self.assertEqual(packet.original_type, 'AF')

            # Every interval-th packet should be remarked
            if (i + 1) % interval == 0:
                self.assertEqual(packet.current_type, 'BE')
            else:
                self.assertEqual(packet.current_type, 'AF')

    def test_edge_processing_time_set(self):
        """Test that edge_complete_time is set correctly."""
        packet = Packet(0, 'EF', gen_time=0.0)
        current_time = packet.edge_arrival_time  # Should be 1.1ms
        
        self.edge.process(packet, current_time=current_time)
        
        expected_complete = packet.edge_arrival_time + config.EDGE_PROCESSING_TIME
        self.assertEqual(packet.edge_complete_time, expected_complete)

    def test_core_arrival_time_set(self):
        """Test that core_arrival_time is set correctly."""
        packet = Packet(0, 'EF', gen_time=0.0)
        current_time = packet.edge_arrival_time
        
        self.edge.process(packet, current_time=current_time)
        
        expected_core_arrival = (packet.edge_complete_time + 
                                config.EDGE_TO_CORE_TRANSMISSION_DELAY + 
                                config.EDGE_TO_CORE_PROPAGATION_DELAY)
        self.assertEqual(packet.core_arrival_time, expected_core_arrival)

    def test_timing_chain(self):
        """Test complete timing chain from generation to core arrival."""
        gen_time = 0.0
        packet = Packet(0, 'AF', gen_time=gen_time)
        
        # Packet should arrive at edge after src->edge delays
        expected_edge_arrival = gen_time + config.SRC_TO_EDGE_TRANSMISSION_DELAY + config.SRC_TO_EDGE_PROPAGATION_DELAY
        self.assertEqual(packet.edge_arrival_time, expected_edge_arrival)
        
        # Process at edge
        self.edge.process(packet, current_time=expected_edge_arrival)
        
        # Check edge processing completion
        expected_edge_complete = expected_edge_arrival + config.EDGE_PROCESSING_TIME
        self.assertEqual(packet.edge_complete_time, expected_edge_complete)
        
        # Check core arrival
        expected_core_arrival = expected_edge_complete + config.EDGE_TO_CORE_TRANSMISSION_DELAY + config.EDGE_TO_CORE_PROPAGATION_DELAY
        self.assertEqual(packet.core_arrival_time, expected_core_arrival)

    def test_multiple_sources(self):
        """Test edge node with packets from multiple sources."""
        for source_id in range(5):
            packet = Packet(source_id, 'AF', gen_time=0.0)
            self.edge.process(packet, current_time=1.1)
        
        # AF counter should count all AF packets regardless of source
        self.assertEqual(self.edge.af_counter, 5)

    def test_remarking_boundary(self):
        """Test remarking at boundary conditions."""
        interval = config.AF_REMARKING_INTERVAL
        
        # Start from a fresh edge node and process packets from 0
        for i in range(interval + 2):
            packet = Packet(0, 'AF', gen_time=float(i))
            self.edge.process(packet, current_time=float(i) + 1.1)
            
            # The (interval)th packet should be remarked (when counter reaches interval)
            if (i + 1) % interval == 0:
                self.assertEqual(packet.current_type, 'BE', 
                               f"Packet {i+1} (counter={self.edge.af_counter}) should be remarked to BE")
            else:
                self.assertEqual(packet.current_type, 'AF',
                               f"Packet {i+1} (counter={self.edge.af_counter}) should remain AF")

    def test_repr(self):
        """Test string representation."""
        # Process some AF packets
        for i in range(3):
            packet = Packet(0, 'AF', gen_time=float(i))
            self.edge.process(packet, current_time=float(i) + 1.1)
        
        repr_str = repr(self.edge)
        self.assertIn('EdgeNode', repr_str)
        self.assertIn('af_counter=3', repr_str)


if __name__ == '__main__':
    unittest.main()
