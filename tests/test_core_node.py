"""Unit tests for CoreNode class."""

import unittest
from src.core_node import CoreNode
from src.packet import Packet


class TestCoreNode(unittest.TestCase):
    """Test cases for CoreNode queuing and scheduling."""

    def test_default_capacities(self):
        """Test default queue capacities."""
        core = CoreNode()
        self.assertEqual(core.capacity_ef, 40)
        self.assertEqual(core.capacity_af, 30)
        self.assertEqual(core.capacity_be, 30)

    def test_custom_capacities(self):
        """Test custom queue capacities."""
        core = CoreNode(capacity_ef=10, capacity_af=20, capacity_be=15)
        self.assertEqual(core.capacity_ef, 10)
        self.assertEqual(core.capacity_af, 20)
        self.assertEqual(core.capacity_be, 15)

    def test_enqueue_ef_packet(self):
        """Test enqueueing EF packets."""
        core = CoreNode()
        packet = Packet(0, 'EF', gen_time=0)

        result = core.enqueue(packet)
        self.assertTrue(result)
        self.assertEqual(len(core.q_ef), 1)

    def test_enqueue_af_packet(self):
        """Test enqueueing AF packets."""
        core = CoreNode()
        packet = Packet(0, 'AF', gen_time=0)

        result = core.enqueue(packet)
        self.assertTrue(result)
        self.assertEqual(len(core.q_af), 1)

    def test_enqueue_be_packet(self):
        """Test enqueueing BE packets."""
        core = CoreNode()
        packet = Packet(0, 'BE', gen_time=0)

        result = core.enqueue(packet)
        self.assertTrue(result)
        self.assertEqual(len(core.q_be), 1)

    def test_tail_drop_ef_queue_full(self):
        """Test tail drop when EF queue is full."""
        core = CoreNode(capacity_ef=2, capacity_af=2, capacity_be=2)

        # Fill EF queue
        for i in range(2):
            packet = Packet(0, 'EF', gen_time=i)
            result = core.enqueue(packet)
            self.assertTrue(result)

        # Next packet should be dropped
        packet = Packet(0, 'EF', gen_time=2)
        result = core.enqueue(packet)
        self.assertFalse(result)
        self.assertEqual(len(core.q_ef), 2)

    def test_tail_drop_af_queue_full(self):
        """Test tail drop when AF queue is full."""
        core = CoreNode(capacity_ef=2, capacity_af=2, capacity_be=2)

        # Fill AF queue
        for i in range(2):
            packet = Packet(0, 'AF', gen_time=i)
            core.enqueue(packet)

        # Next packet should be dropped
        packet = Packet(0, 'AF', gen_time=2)
        result = core.enqueue(packet)
        self.assertFalse(result)

    def test_tail_drop_be_queue_full(self):
        """Test tail drop when BE queue is full."""
        core = CoreNode(capacity_ef=2, capacity_af=2, capacity_be=2)

        # Fill BE queue
        for i in range(2):
            packet = Packet(0, 'BE', gen_time=i)
            core.enqueue(packet)

        # Next packet should be dropped
        packet = Packet(0, 'BE', gen_time=2)
        result = core.enqueue(packet)
        self.assertFalse(result)

    def test_strict_priority_ef_first(self):
        """Test that EF packets are served first (strict priority)."""
        core = CoreNode()

        # Add packets in reverse priority order
        be_pkt = Packet(0, 'BE', gen_time=0)
        af_pkt = Packet(1, 'AF', gen_time=0)
        ef_pkt = Packet(2, 'EF', gen_time=0)

        core.enqueue(be_pkt)
        core.enqueue(af_pkt)
        core.enqueue(ef_pkt)

        # Should serve EF first
        served = core.serve()
        self.assertEqual(served.source_id, 2)
        self.assertEqual(served.current_type, 'EF')

    def test_strict_priority_order(self):
        """Test complete strict priority ordering (EF > AF > BE)."""
        core = CoreNode()

        # Add one of each type
        be_pkt = Packet(0, 'BE', gen_time=0)
        af_pkt = Packet(1, 'AF', gen_time=0)
        ef_pkt = Packet(2, 'EF', gen_time=0)

        core.enqueue(be_pkt)
        core.enqueue(af_pkt)
        core.enqueue(ef_pkt)

        # Serve order should be: EF, AF, BE
        served1 = core.serve()
        served2 = core.serve()
        served3 = core.serve()

        self.assertEqual(served1.current_type, 'EF')
        self.assertEqual(served2.current_type, 'AF')
        self.assertEqual(served3.current_type, 'BE')

    def test_serve_empty_queues(self):
        """Test serving when all queues are empty."""
        core = CoreNode()
        served = core.serve()
        self.assertIsNone(served)

    def test_serve_only_be_available(self):
        """Test serving BE when EF and AF queues are empty."""
        core = CoreNode()

        be_pkt = Packet(0, 'BE', gen_time=0)
        core.enqueue(be_pkt)

        served = core.serve()
        self.assertEqual(served.current_type, 'BE')

    def test_fifo_within_queue(self):
        """Test FIFO ordering within each queue."""
        core = CoreNode()

        # Add 3 EF packets
        for i in range(3):
            packet = Packet(i, 'EF', gen_time=i)
            core.enqueue(packet)

        # Should serve in order 0, 1, 2
        for i in range(3):
            served = core.serve()
            self.assertEqual(served.source_id, i)

    def test_get_queue_sizes(self):
        """Test queue size reporting."""
        core = CoreNode()

        # Add packets
        core.enqueue(Packet(0, 'EF', 0))
        core.enqueue(Packet(0, 'EF', 0))
        core.enqueue(Packet(0, 'AF', 0))
        core.enqueue(Packet(0, 'BE', 0))
        core.enqueue(Packet(0, 'BE', 0))
        core.enqueue(Packet(0, 'BE', 0))

        sizes = core.get_queue_sizes()
        self.assertEqual(sizes['EF'], 2)
        self.assertEqual(sizes['AF'], 1)
        self.assertEqual(sizes['BE'], 3)


if __name__ == '__main__':
    unittest.main()
