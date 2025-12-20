"""Unit tests for Packet class."""

import unittest
from src.packet import Packet


class TestPacket(unittest.TestCase):
    """Test cases for Packet class."""

    def test_packet_creation(self):
        """Test packet initialization with correct attributes."""
        packet = Packet(source_id=0, packet_type='EF', gen_time=10)
        self.assertEqual(packet.source_id, 0)
        self.assertEqual(packet.original_type, 'EF')
        self.assertEqual(packet.current_type, 'EF')
        self.assertEqual(packet.gen_time, 10)

    def test_packet_type_modification(self):
        """Test that current_type can be modified while original_type is preserved."""
        packet = Packet(source_id=1, packet_type='AF', gen_time=5)
        self.assertEqual(packet.original_type, 'AF')
        self.assertEqual(packet.current_type, 'AF')

        # Simulate remarking
        packet.current_type = 'BE'
        self.assertEqual(packet.original_type, 'AF')  # Original preserved
        self.assertEqual(packet.current_type, 'BE')   # Current modified

    def test_packet_repr(self):
        """Test string representation of packet."""
        packet = Packet(source_id=2, packet_type='BE', gen_time=100)
        repr_str = repr(packet)
        self.assertIn('source=2', repr_str)
        self.assertIn('type=BE', repr_str)
        self.assertIn('gen_time=100', repr_str)


if __name__ == '__main__':
    unittest.main()
