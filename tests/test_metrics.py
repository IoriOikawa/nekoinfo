import unittest
from types import SimpleNamespace as NS
from nekoinfo.metrics import Sampler, History


class Provider:
    def __init__(self):
        self.cores = [20, 60]
        self.memory = NS(total=1000, available=400)
        self.net = {'eth0': NS(bytes_recv=100, bytes_sent=200), 'lo': NS(bytes_recv=10000, bytes_sent=10000)}
        self.fail = set()
    def cpu_percent(self, **kwargs):
        if 'cpu' in self.fail: raise OSError('cpu')
        return self.cores
    def virtual_memory(self):
        if 'memory' in self.fail: raise OSError('memory')
        return self.memory
    def net_io_counters(self, **kwargs):
        if 'network' in self.fail: raise OSError('network')
        return self.net
    def net_if_addrs(self):
        return {'lo': [NS(address='127.0.0.1')], 'eth0': [NS(address='192.0.2.1')]}


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.p = Provider()
        self.s = Sampler(self.p)
    def test_cpu_warmup_and_core_average(self):
        self.assertIsNone(self.s.sample(0).cpu_percent)
        sample = self.s.sample(2)
        self.assertEqual(sample.cpu_percent, 40)
        self.assertEqual(sample.per_cpu, (20, 60))
    def test_memory_uses_available(self):
        memory = self.s.sample(0).memory
        self.assertEqual((memory.used, memory.available, memory.percent), (600, 400, 60))
    def test_network_uses_actual_interval_excludes_loopback(self):
        self.s.sample(0)
        self.p.net['eth0'] = NS(bytes_recv=1124, bytes_sent=2248)
        network = self.s.sample(4).network
        self.assertEqual((network.received, network.sent), (256, 512))
    def test_network_resets_for_interface_changes_counter_resets_and_sleep(self):
        self.s.sample(0)
        self.p.net['tun0'] = NS(bytes_recv=50, bytes_sent=50)
        self.assertIsNone(self.s.sample(2).network)
        self.p.net.pop('tun0')
        self.assertIsNone(self.s.sample(4).network)
        self.p.net['eth0'] = NS(bytes_recv=0, bytes_sent=0)
        self.assertIsNone(self.s.sample(6).network)
        self.assertIsNone(self.s.sample(17).network)
        self.assertIsNone(self.s.sample(17).network)
    def test_metric_errors_are_isolated_and_recovery_warms_up(self):
        self.s.sample(0)
        self.p.fail = {'cpu', 'network'}
        sample = self.s.sample(2)
        self.assertIsNotNone(sample.memory)
        self.assertEqual(sample.errors, frozenset({'cpu', 'network'}))
        self.p.fail.clear()
        self.assertIsNone(self.s.sample(4).cpu_percent)
        self.assertIsNotNone(self.s.sample(6).cpu_percent)
    def test_memory_error_does_not_stop_cpu(self):
        self.s.sample(0)
        self.p.fail = {'memory'}
        sample = self.s.sample(2)
        self.assertIsNone(sample.memory)
        self.assertEqual(sample.cpu_percent, 40)
    def test_suspend_without_monotonic_advance_resets_history(self):
        wall = [100]
        sampler = Sampler(self.p, wall_clock=lambda: wall[0])
        history = History()
        history.append(sampler.sample(0))
        wall[0] = 102
        history.append(sampler.sample(2))
        wall[0] = 200
        resumed = sampler.sample(3)
        history.append(resumed)
        self.assertIsNone(resumed.cpu_percent)
        self.assertIsNone(resumed.network)
        self.assertEqual(len(history.samples), 1)

    def test_history_bounds_and_gaps(self):
        history = History(seconds=60, max_samples=40)
        for t in range(100): history.append(self.s.sample(t))
        self.assertEqual(len(history.samples), 40)
        history.append(self.s.sample(200))
        self.assertEqual(len(history.samples), 1)
        self.assertIsNone(history.samples[0].cpu_percent)


if __name__ == '__main__': unittest.main()
