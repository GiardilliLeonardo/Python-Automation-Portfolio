# Task: Golang Engineer — High-Performance Backend / Systems Project | $3000 Fixed

import concurrent.futures
import json
import logging
import statistics
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("GoBackendDebugger")


@dataclass
class ProfilingMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    latencies_ms: List[float] = field(default_factory=list)
    initial_goroutines: int = 0
    final_goroutines: int = 0
    initial_heap_alloc_bytes: int = 0
    final_heap_alloc_bytes: int = 0

    @property
    def p50(self) -> float:
        return statistics.median(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def p95(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_lats = sorted(self.latencies_ms)
        idx = int(0.95 * len(sorted_lats))
        return sorted_lats[min(idx, len(sorted_lats) - 1)]

    @property
    def p99(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_lats = sorted(self.latencies_ms)
        idx = int(0.99 * len(sorted_lats))
        return sorted_lats[min(idx, len(sorted_lats) - 1)]


class GoServiceDebugger:
    """Diagnostic harness for Go-based high-concurrency microservices.

    Monitors runtime metrics via expvar/pprof and benchmarks HTTP endpoints.
    """

    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _fetch_json(self, path: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{path}"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "PyGoDebugger/1.0"}
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
            logger.warning("Failed fetching %s: %s", url, e)
        return None

    def get_runtime_metrics(self) -> Dict[str, int]:
        """Scrapes standard Go `expvar` endpoint for memory & goroutines."""
        data = self._fetch_json("/debug/vars")
        if not data:
            return {"goroutines": -1, "heap_alloc": -1}

        goroutines = data.get("goroutines", data.get("NumGoroutine", -1))
        memstats = data.get("memstats", {})
        heap_alloc = memstats.get("Alloc", -1) if isinstance(memstats, dict) else -1

        return {"goroutines": goroutines, "heap_alloc": heap_alloc}

    def _probe_endpoint(self, path: str) -> Tuple[bool, float]:
        url = f"{self.base_url}{path}"
        start = time.perf_counter()
        try:
            req = urllib.request.Request(
                url, headers={"Connection": "keep-alive"}
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                elapsed = (time.perf_counter() - start) * 1000.0
                return resp.status == 200, elapsed
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000.0
            return False, elapsed

    def run_stress_diagnostics(
        self, endpoint: str, total_requests: int = 1000, concurrency: int = 20
    ) -> ProfilingMetrics:
        metrics = ProfilingMetrics(total_requests=total_requests)

        logger.info("Collecting pre-test Go runtime metrics...")
        init_stats = self.get_runtime_metrics()
        metrics.initial_goroutines = init_stats["goroutines"]
        metrics.initial_heap_alloc_bytes = init_stats["heap_alloc"]

        logger.info(
            "Firing %d requests across %d concurrent workers to: %s",
            total_requests,
            concurrency,
            endpoint,
        )

        with concurrent.futures.ThreadPoolExecutor
