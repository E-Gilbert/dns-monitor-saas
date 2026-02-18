import time
from typing import Tuple, Optional

import dns.resolver
import dns.exception

GOOGLE_NAMESERVERS = ["8.8.8.8", "8.8.4.4"]

def resolve_a(domain: str, timeout_seconds: float = 3.0) -> Tuple[Optional[str], int]:
    """
    Resolve A record for a domain.
    Returns (ip_or_none, latency_ms)
    """
    resolver = dns.resolver.Resolver()
    resolver.nameservers = GOOGLE_NAMESERVERS
    resolver.lifetime = timeout_seconds
    resolver.timeout = timeout_seconds

    start = time.perf_counter()
    try:
        answer = resolver.resolve(domain, "A")
        latency_ms = int((time.perf_counter() - start) * 1000)
        ip = str(next(iter(answer)))
        return ip, latency_ms

    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        latency_ms = int((time.perf_counter() - start) * 1000)
        return None, latency_ms

    except (dns.exception.Timeout, dns.resolver.NoNameservers) as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        raise RuntimeError(f"DNS lookup failed: {e}") from e
