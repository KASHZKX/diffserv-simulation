"""Unit tests for Source class with focus on metrics calculation."""

import unittest
from src.source import Source
from src.packet import Packet


class TestSource(unittest.TestCase):
    """Test cases for Source class."""

    def test_source_type_normalization(self):
        """Test that source types are normalized correctly."""
        source_e = Source(0, 'E')
        source_a = Source(1, 'A')
        source_b = Source(2, 'B')
        source_ef = Source(3, 'EF')

        self.assertEqual(source_e.type, 'EF')
        self.assertEqual(source_a.type, 'AF')
        self.assertEqual(source_b.type, 'BE')
        self.assertEqual(source_ef.type, 'EF')

    def test_generate_packet(self):
        """Test packet generation increments counter."""
        source = Source(0, 'EF')
        self.assertEqual(source.packets_generated, 0)

        packet = source.generate_packet(current_time=10)
        self.assertEqual(source.packets_generated, 1)
        self.assertEqual(packet.source_id, 0)
        self.assertEqual(packet.gen_time, 10)

    def test_record_success_and_latency(self):
        """Test that successful packets are recorded with correct latency."""
        source = Source(0, 'EF')
        packet = Packet(0, 'EF', gen_time=10)

        source.record_success(packet, service_time=15)
        self.assertEqual(source.packets_success, 1)
        self.assertEqual(source.latencies, [5])  # 15 - 10 = 5

    def test_completion_time_set_at_1000(self):
        """Test that completion time is set when 1000th packet succeeds."""
        source = Source(0, 'EF')

        # Simulate 999 successful packets
        for i in range(999):
            packet = Packet(0, 'EF', gen_time=i)
            source.record_success(packet, service_time=i + 10)

        self.assertEqual(source.packets_success, 999)
        self.assertEqual(source.completion_time, 0)  # Not set yet

        # 1000th packet
        packet = Packet(0, 'EF', gen_time=999)
        source.record_success(packet, service_time=1050)

        self.assertEqual(source.packets_success, 1000)
        self.assertEqual(source.completion_time, 1050)

    def test_is_finished(self):
        """Test is_finished returns True after 1000 successful packets."""
        source = Source(0, 'EF')
        self.assertFalse(source.is_finished())

        # Simulate 1000 successful packets
        for i in range(1000):
            packet = Packet(0, 'EF', gen_time=i)
            source.record_success(packet, service_time=i)

        self.assertTrue(source.is_finished())

    def test_drop_rate_calculation_no_drops(self):
        """Test drop rate is 0 when no packets are dropped."""
        source = Source(0, 'EF')

        # Generate and succeed 1000 packets (no drops)
        for i in range(1000):
            source.generate_packet(i)
            packet = Packet(0, 'EF', gen_time=i)
            source.record_success(packet, service_time=i)

        self.assertEqual(source.packets_generated, 1000)
        self.assertEqual(source.packets_success, 1000)
        self.assertAlmostEqual(source.get_drop_rate(), 0.0)

    def test_drop_rate_calculation_with_drops(self):
        """Test drop rate calculation with some dropped packets."""
        source = Source(0, 'EF')

        # Generate 2000 packets, succeed only 1000
        for i in range(2000):
            source.generate_packet(i)

        for i in range(1000):
            packet = Packet(0, 'EF', gen_time=i)
            source.record_success(packet, service_time=i)

        self.assertEqual(source.packets_generated, 2000)
        self.assertEqual(source.packets_success, 1000)
        # Drop rate: (2000 - 1000) / 2000 * 100 = 50%
        self.assertAlmostEqual(source.get_drop_rate(), 50.0)

    def test_drop_rate_edge_case_25_percent(self):
        """Test drop rate calculation at 25%."""
        source = Source(0, 'EF')

        # Generate 4000 packets, succeed 3000 (25% drop rate)
        for i in range(4000):
            source.generate_packet(i)

        for i in range(3000):
            packet = Packet(0, 'EF', gen_time=i)
            source.record_success(packet, service_time=i)

        # Drop rate: (4000 - 3000) / 4000 * 100 = 25%
        self.assertAlmostEqual(source.get_drop_rate(), 25.0)

    def test_drop_rate_empty_source(self):
        """Test drop rate returns 0 when no packets generated."""
        source = Source(0, 'EF')
        self.assertAlmostEqual(source.get_drop_rate(), 0.0)

    def test_avg_latency_calculation(self):
        """Test average latency calculation."""
        source = Source(0, 'EF')

        # Packets with latencies: 10, 20, 30 (average = 20)
        latencies = [10, 20, 30]
        for i, lat in enumerate(latencies):
            packet = Packet(0, 'EF', gen_time=i)
            source.record_success(packet, service_time=i + lat)

        self.assertAlmostEqual(source.get_avg_latency(), 20.0)

    def test_avg_latency_single_packet(self):
        """Test average latency with a single packet."""
        source = Source(0, 'EF')
        packet = Packet(0, 'EF', gen_time=100)
        source.record_success(packet, service_time=150)

        self.assertAlmostEqual(source.get_avg_latency(), 50.0)

    def test_avg_latency_empty(self):
        """Test average latency returns 0 when no successful packets."""
        source = Source(0, 'EF')
        self.assertAlmostEqual(source.get_avg_latency(), 0.0)

    def test_avg_latency_zero_latency(self):
        """Test average latency when packets are served immediately."""
        source = Source(0, 'EF')

        for i in range(100):
            packet = Packet(0, 'EF', gen_time=i)
            source.record_success(packet, service_time=i)  # 0 latency

        self.assertAlmostEqual(source.get_avg_latency(), 0.0)


if __name__ == '__main__':
    unittest.main()
