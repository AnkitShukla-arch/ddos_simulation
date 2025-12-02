#!/usr/bin/env python3
import asyncio
import argparse
import yaml
import httpx
import time
import signal

from utils.ip_generator import generate_ip
from utils.traffic_modes import MALICIOUS_WEIGHTS
from dataclasses import dataclass, field

@dataclass
class Stats:
    sent: int = 0
    succeeded: int = 0
    failed: int = 0
    malicious: int = 0
    normal: int = 0
    latencies: list = field(default_factory=list)

    def summary(self):
        avg = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        return {
            "sent": self.sent,
            "ok": self.succeeded,
            "failed": self.failed,
            "malicious_sent": self.malicious,
            "normal_sent": self.normal,
            "avg_latency_ms": round(avg * 1000, 2)
        }


class TrafficEngine:

    def __init__(self, cfg):
        self.endpoint = cfg["endpoint"]
        self.rps = cfg["rps"]
        self.duration = cfg["duration"]
        self.mode = cfg["mode"]
        self.concurrency = cfg["concurrency"]
        self.ipv4_ratio = cfg["ipv4_ratio"]
        self.log_interval = cfg["log_interval"]

        self.stats = Stats()
        self.stop = False
        self.client = httpx.AsyncClient(timeout=5)

    async def start(self):
        queue = asyncio.Queue(maxsize=self.rps * 4)

        producer = asyncio.create_task(self._producer(queue))
        consumers = [asyncio.create_task(self._consumer(queue)) for _ in range(self.concurrency)]
        logger = asyncio.create_task(self._logger())

        if self.duration:
            await asyncio.sleep(self.duration)
            self.stop = True

        await producer
        await queue.join()

        for c in consumers:
            c.cancel()

        logger.cancel()
        await self.client.aclose()

    async def _producer(self, queue):
        interval = 1 / self.rps
        next_time = time.time()

        while not self.stop:
            ip, is_mal = generate_ip(self.mode, self.ipv4_ratio)
            await queue.put((ip, is_mal))
            next_time += interval
            delay = next_time - time.time()
            if delay > 0:
                await asyncio.sleep(delay)

    async def _consumer(self, queue):
        while True:
            ip, is_malicious = await queue.get()

            try:
                start = time.time()
                r = await self.client.post(self.endpoint, json={"ip": ip})
                latency = time.time() - start

                self.stats.sent += 1
                self.stats.latencies.append(latency)

                if 200 <= r.status_code < 300:
                    self.stats.succeeded += 1
                else:
                    self.stats.failed += 1

                if is_malicious:
                    self.stats.malicious += 1
                else:
                    self.stats.normal += 1

            except:
                self.stats.failed += 1

            queue.task_done()

    async def _logger(self):
        while not self.stop:
            await asyncio.sleep(self.log_interval)
            print("[BOT]", self.stats.summary())


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    engine = TrafficEngine(cfg)

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: setattr(engine, "stop", True))

    loop.run_until_complete(engine.start())


if __name__ == "__main__":
    main()

