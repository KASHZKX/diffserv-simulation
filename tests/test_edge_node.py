"""Unit tests for EdgeNode class."""

import unittest
from src.edge_node import EdgeNode
from src.packet import Packet


class TestEdgeNode(unittest.TestCase):
    """Test cases for EdgeNode remarking logic."""

    def test_ef_packets_pass_unchanged(self):
        """Test that EF packets pass through without modification."""
        edge = EdgeNode()

        for i in range(10):
            packet = Packet(0, 'EF', gen_time=i)
            edge.process(packet)
            self.assertEqual(packet.current_type, 'EF')
            self.assertEqual(packet.original_type, 'EF')

    def test_be_packets_pass_unchanged(self):
        """Test that BE packets pass through without modification."""
        edge = EdgeNode()

        for i in range(10):
            packet = Packet(0, 'BE', gen_time=i)
            edge.process(packet)
            self.assertEqual(packet.current_type, 'BE')
            self.assertEqual(packet.original_type, 'BE')

    def test_af_remarking_every_5th(self):
        """Test that every 5th AF packet is downgraded to BE."""
        edge = EdgeNode()

        results = []
        for i in range(20):
            packet = Packet(0, 'AF', gen_time=i)
            edge.process(packet)
            results.append(packet.current_type)

        # Expected: AF, AF, AF, AF, BE, AF, AF, AF, AF, BE, ...
        expected = ['AF', 'AF', 'AF', 'AF', 'BE'] * 4
        self.assertEqual(results, expected)

    def test_af_counter_increments(self):
        """Test that AF counter increments correctly."""
        edge = EdgeNode()
        self.assertEqual(edge.af_counter, 0)

        for i in range(7):
            packet = Packet(0, 'AF', gen_time=i)
            edge.process(packet)

        self.assertEqual(edge.af_counter, 7)

    def test_mixed_traffic_af_counter(self):
        """Test AF counter only counts AF packets in mixed traffic."""
        edge = EdgeNode()

        # Mix of EF, AF, BE
        packets = [
            Packet(0, 'EF', 0),
            Packet(0, 'AF', 1),
            Packet(0, 'BE', 2),
            Packet(0, 'AF', 3),
            Packet(0, 'EF', 4),
        ]

        for pkt in packets:
            edge.process(pkt)

        # Only 2 AF packets
        self.assertEqual(edge.af_counter, 2)

    def test_original_type_preserved_after_remarking(self):
        """Test that original_type is preserved after remarking."""
        edge = EdgeNode()

        # Process 5 AF packets (5th will be remarked)
        for i in range(5):
            packet = Packet(0, 'AF', gen_time=i)
            edge.process(packet)
            self.assertEqual(packet.original_type, 'AF')

            if i == 4:  # 5th packet (index 4)
                self.assertEqual(packet.current_type, 'BE')
            else:
                self.assertEqual(packet.current_type, 'AF')


if __name__ == '__main__':
    unittest.main()
