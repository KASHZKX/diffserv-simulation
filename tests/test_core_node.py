"""Unit tests for CoreNode class."""

import unittest
from src.core_node import CoreNode
from src.packet import Packet
from src.source import Source
from src import config


class TestCoreNode(unittest.TestCase):
    """Test cases for CoreNode queuing and scheduling."""

    def setUp(self):
        """Set up test fixtures."""
        self.core = CoreNode()
        self.sources = [Source(i, 'EF') for i in range(3)]

    def test_default_capacities(self):
        """Test default queue capacities from config."""
        core = CoreNode()
        self.assertEqual(core.capacity_ef, config.CORE_QUEUE_CAPACITY_EF)
        self.assertEqual(core.capacity_af, config.CORE_QUEUE_CAPACITY_AF)
        self.assertEqual(core.capacity_be, config.CORE_QUEUE_CAPACITY_BE)

    def test_custom_capacities(self):
        """Test custom queue capacities."""
        core = CoreNode(capacity_ef=10, capacity_af=20, capacity_be=15)
        self.assertEqual(core.capacity_ef, 10)
        self.assertEqual(core.capacity_af, 20)
        self.assertEqual(core.capacity_be, 15)

    def test_initial_state(self):
        """Test initial state of core node."""
        self.assertEqual(len(self.core.q_ef), 0)
        self.assertEqual(len(self.core.q_af), 0)
        self.assertEqual(len(self.core.q_be), 0)
        self.assertIsNone(self.core.serving_packet)
        self.assertIsNone(self.core.service_complete_time)

    def test_enqueue_ef_packet(self):
        """Test enqueueing EF packets."""
        packet = Packet(0, 'EF', gen_time=0.0)
        result = self.core.enqueue(packet)
        
        self.assertTrue(result)
        self.assertEqual(len(self.core.q_ef), 1)
        self.assertIn(packet, self.core.q_ef)

    def test_enqueue_af_packet(self):
        """Test enqueueing AF packets."""
        packet = Packet(0, 'AF', gen_time=0.0)
        result = self.core.enqueue(packet)
        
        self.assertTrue(result)
        self.assertEqual(len(self.core.q_af), 1)
        self.assertIn(packet, self.core.q_af)

    def test_enqueue_be_packet(self):
        """Test enqueueing BE packets."""
        packet = Packet(0, 'BE', gen_time=0.0)
        result = self.core.enqueue(packet)
        
        self.assertTrue(result)
        self.assertEqual(len(self.core.q_be), 1)
        self.assertIn(packet, self.core.q_be)

    def test_tail_drop_ef_queue_full(self):
        """Test tail drop when EF queue is full."""
        core = CoreNode(capacity_ef=2, capacity_af=2, capacity_be=2)

        # Fill EF queue
        for i in range(2):
            packet = Packet(0, 'EF', gen_time=float(i))
            result = core.enqueue(packet)
            self.assertTrue(result)

        # Next packet should be dropped
        packet = Packet(0, 'EF', gen_time=2.0)
        result = core.enqueue(packet)
        self.assertFalse(result)
        self.assertEqual(len(core.q_ef), 2)

    def test_tail_drop_af_queue_full(self):
        """Test tail drop when AF queue is full."""
        core = CoreNode(capacity_ef=2, capacity_af=2, capacity_be=2)

        # Fill AF queue
        for i in range(2):
            packet = Packet(0, 'AF', gen_time=float(i))
            core.enqueue(packet)

        # Next packet should be dropped
        packet = Packet(0, 'AF', gen_time=2.0)
        result = core.enqueue(packet)
        self.assertFalse(result)
        self.assertEqual(len(core.q_af), 2)

    def test_tail_drop_be_queue_full(self):
        """Test tail drop when BE queue is full."""
        core = CoreNode(capacity_ef=2, capacity_af=2, capacity_be=2)

        # Fill BE queue
        for i in range(2):
            packet = Packet(0, 'BE', gen_time=float(i))
            core.enqueue(packet)

        # Next packet should be dropped
        packet = Packet(0, 'BE', gen_time=2.0)
        result = core.enqueue(packet)
        self.assertFalse(result)
        self.assertEqual(len(core.q_be), 2)

    def test_start_service_ef_priority(self):
        """Test that EF packets are served first (strict priority)."""
        # Add packets to all queues
        pkt_be = Packet(0, 'BE', gen_time=0.0)
        pkt_af = Packet(1, 'AF', gen_time=0.0)
        pkt_ef = Packet(2, 'EF', gen_time=0.0)
        
        self.core.enqueue(pkt_be)
        self.core.enqueue(pkt_af)
        self.core.enqueue(pkt_ef)

        # Start service should get EF first
        served = self.core.start_service(0.0, self.sources)
        self.assertIsNotNone(served)
        self.assertEqual(served.source_id, 2)
        self.assertEqual(served.current_type, 'EF')

    def test_start_service_af_priority_over_be(self):
        """Test that AF packets are served before BE."""
        pkt_be = Packet(0, 'BE', gen_time=0.0)
        pkt_af = Packet(1, 'AF', gen_time=0.0)
        
        self.core.enqueue(pkt_be)
        self.core.enqueue(pkt_af)

        # Start service should get AF first
        served = self.core.start_service(0.0, self.sources)
        self.assertIsNotNone(served)
        self.assertEqual(served.source_id, 1)
        self.assertEqual(served.current_type, 'AF')

    def test_start_service_only_be(self):
        """Test serving BE when no higher priority packets."""
        pkt_be = Packet(0, 'BE', gen_time=0.0)
        self.core.enqueue(pkt_be)

        served = self.core.start_service(0.0, self.sources)
        self.assertIsNotNone(served)
        self.assertEqual(served.current_type, 'BE')

    def test_start_service_empty_queues(self):
        """Test start_service with empty queues."""
        served = self.core.start_service(0.0, self.sources)
        self.assertIsNone(served)

    def test_start_service_sets_times(self):
        """Test that start_service sets correct timing fields."""
        packet = Packet(0, 'EF', gen_time=0.0)
        self.core.enqueue(packet)

        current_time = 10.0
        served = self.core.start_service(current_time, self.sources)
        
        self.assertIsNotNone(served)
        self.assertEqual(served.core_service_start_time, current_time)
        expected_reach = current_time + config.CORE_TO_DST_TRANSMISSION_DELAY + config.CORE_TO_DST_PROPAGATION_DELAY
        self.assertEqual(served.reach_time, expected_reach)

    def test_start_service_updates_serving_packet(self):
        """Test that serving_packet is updated correctly."""
        packet = Packet(0, 'EF', gen_time=0.0)
        self.core.enqueue(packet)

        served = self.core.start_service(0.0, self.sources)
        self.assertEqual(self.core.serving_packet, served)
        self.assertIsNotNone(self.core.service_complete_time)

    def test_start_service_blocks_when_serving(self):
        """Test that start_service blocks when already serving."""
        pkt1 = Packet(0, 'EF', gen_time=0.0)
        pkt2 = Packet(1, 'EF', gen_time=0.0)
        self.core.enqueue(pkt1)
        self.core.enqueue(pkt2)

        # Start first service
        served1 = self.core.start_service(0.0, self.sources)
        self.assertIsNotNone(served1)

        # Try to start again before completion
        served2 = self.core.start_service(0.5, self.sources)
        self.assertIsNone(served2)

    def test_start_service_allows_after_completion_time(self):
        """Test that start_service allows new packet after completion time."""
        core = CoreNode()
        core.capacity_ef = 10 
        sources = [Source(i, 'EF') for i in range(2)]
        
        pkt1 = Packet(0, 'EF', gen_time=0.0)
        pkt2 = Packet(1, 'EF', gen_time=0.0)
        core.enqueue(pkt1)
        core.enqueue(pkt2)

        # Start first service at time 0
        served1 = core.start_service(0.0, sources)
        self.assertIsNotNone(served1)
        completion_time = core.service_complete_time

        # Complete the first service
        core.complete_service(completion_time)
        
        # Try to start at completion time (should succeed)
        served2 = core.start_service(completion_time, sources)
        self.assertIsNotNone(served2)

    def test_start_service_skips_finished_sources(self):
        """Test that start_service skips packets from finished sources."""
        core = CoreNode()
        core.capacity_ef = 10
        # Create sources where source 0 is finished
        sources = [Source(i, 'EF') for i in range(2)]
        sources[0].packets_success = config.TARGET_SUCCESS_PACKETS
        sources[0].packets_generated = config.TARGET_SUCCESS_PACKETS + 2  # Has extra packets
        
        pkt1 = Packet(0, 'EF', gen_time=0.0)  # From finished source
        pkt2 = Packet(1, 'EF', gen_time=0.0)  # From active source
        
        core.enqueue(pkt1)
        core.enqueue(pkt2)

        # Should skip pkt1 and serve pkt2
        served = core.start_service(0.0, sources)
        self.assertIsNotNone(served)
        self.assertEqual(served.source_id, 1)
        # Check that pkt1's source had packets_generated decreased
        self.assertEqual(sources[0].packets_generated, config.TARGET_SUCCESS_PACKETS + 1)

    def test_complete_service_not_serving(self):
        """Test complete_service when not serving."""
        result = self.core.complete_service(0.0)
        self.assertFalse(result)

    def test_complete_service_before_time(self):
        """Test complete_service before service completion time."""
        packet = Packet(0, 'EF', gen_time=0.0)
        self.core.enqueue(packet)
        self.core.start_service(0.0, self.sources)

        # Try to complete before time
        result = self.core.complete_service(0.5)
        self.assertFalse(result)
        self.assertIsNotNone(self.core.serving_packet)

    def test_complete_service_at_time(self):
        """Test complete_service at completion time."""
        packet = Packet(0, 'EF', gen_time=0.0)
        self.core.enqueue(packet)
        self.core.start_service(0.0, self.sources)
        completion_time = self.core.service_complete_time

        # Complete at the right time
        result = self.core.complete_service(completion_time)
        self.assertTrue(result)
        self.assertIsNone(self.core.serving_packet)
        self.assertIsNone(self.core.service_complete_time)

    def test_get_queue_sizes(self):
        """Test get_queue_sizes method."""
        # Use a fresh core node to avoid state from previous tests
        core = CoreNode()
        core.capacity_af = 10  
        core.capacity_be = 10
        core.capacity_ef = 10

        core.enqueue(Packet(0, 'EF', 0.0))
        core.enqueue(Packet(0, 'EF', 0.0))
        core.enqueue(Packet(0, 'AF', 0.0))
        core.enqueue(Packet(0, 'BE', 0.0))
        core.enqueue(Packet(0, 'BE', 0.0))
        core.enqueue(Packet(0, 'BE', 0.0))

        sizes = core.get_queue_sizes()
        self.assertEqual(sizes['EF'], 2)
        self.assertEqual(sizes['AF'], 1)
        self.assertEqual(sizes['BE'], 3)

    def test_repr(self):
        """Test string representation."""
        self.core.enqueue(Packet(0, 'EF', 0.0))
        self.core.enqueue(Packet(0, 'AF', 0.0))
        
        repr_str = repr(self.core)
        self.assertIn('CoreNode', repr_str)
        self.assertIn('EF=1', repr_str)
        self.assertIn('AF=1', repr_str)


if __name__ == '__main__':
    unittest.main()
