"""Nonblocking sampling, independent of GTK. All rates use monotonic time."""
from collections import deque
from dataclasses import dataclass
import ipaddress
import time


@dataclass(frozen=True)
class Memory:
    total: int
    available: int
    used: int
    percent: float


@dataclass(frozen=True)
class Network:
    received: float
    sent: float


@dataclass(frozen=True)
class Sample:
    timestamp: float
    cpu_percent: float | None
    per_cpu: tuple[float, ...] | None
    memory: Memory | None
    network: Network | None
    errors: frozenset[str]
    discontinuity: bool = False


class Sampler:
    def __init__(self, provider=None, clock=time.monotonic, wall_clock=time.time):
        if provider is None:
            import psutil
            provider = psutil
        self.provider = provider
        self.clock = clock
        self.wall_clock = wall_clock
        self._last_wall = None
        self._cpu_ready = False
        self._network = None
        self._last_time = None

    def sample(self, timestamp=None):
        now = self.clock() if timestamp is None else timestamp
        wall = self.wall_clock()
        discontinuity = self._last_time is not None and (
            not 0 < now - self._last_time <= 10 or
            abs((wall - self._last_wall) - (now - self._last_time)) > 10)
        if discontinuity:
            self._cpu_ready = False
            self._network = None
        self._last_time, self._last_wall = now, wall
        errors = set()
        cpu = cores = memory = network = None
        try:
            values = tuple(self.provider.cpu_percent(interval=None, percpu=True))
            if self._cpu_ready and values:
                cores = values
                cpu = sum(values) / len(values)
            self._cpu_ready = True
        except (OSError, RuntimeError, ValueError):
            errors.add('cpu')
            self._cpu_ready = False
        try:
            value = self.provider.virtual_memory()
            memory = Memory(value.total, value.available, value.total - value.available,
                            100 * (value.total - value.available) / value.total)
        except (OSError, RuntimeError, ValueError, ZeroDivisionError):
            errors.add('memory')
        try:
            addresses = self.provider.net_if_addrs()
            counters = self.provider.net_io_counters(pernic=True)
            def loopback(name):
                if name == 'lo' or name.startswith('lo:'):
                    return True
                ips = []
                for address in addresses.get(name, ()):
                    try:
                        ips.append(ipaddress.ip_address(address.address.split('%')[0]))
                    except ValueError:
                        pass
                return bool(ips) and all(ip.is_loopback for ip in ips)
            current = {name: (value.bytes_recv, value.bytes_sent)
                       for name, value in counters.items() if not loopback(name)}
            if self._network is not None:
                before_time, before = self._network
                elapsed = now - before_time
                if current.keys() == before.keys() and 0 < elapsed <= 10:
                    deltas = [(current[n][0] - before[n][0], current[n][1] - before[n][1])
                              for n in current]
                    if all(rx >= 0 and tx >= 0 for rx, tx in deltas):
                        network = Network(sum(rx for rx, _ in deltas) / elapsed,
                                          sum(tx for _, tx in deltas) / elapsed)
            self._network = now, current
        except (OSError, RuntimeError, ValueError):
            errors.add('network')
            self._network = None
        return Sample(now, cpu, cores, memory, network, frozenset(errors), discontinuity)


class History:
    def __init__(self, seconds=60, max_samples=128):
        self.seconds = seconds
        self.samples = deque(maxlen=max_samples)

    def append(self, sample):
        if sample.discontinuity:
            self.samples.clear()
        self.samples.append(sample)
        while self.samples and sample.timestamp - self.samples[0].timestamp > self.seconds:
            self.samples.popleft()
