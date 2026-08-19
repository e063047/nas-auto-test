import asyncio
import socket
import subprocess
import re
from typing import List, Dict, Optional

# Western Digital OUI prefixes (first 3 bytes of MAC)
WD_MAC_OUIS = {"00:90:a9", "00:14:ee", "00:1d:72", "08:62:66", "74:83:ef", "f4:8e:38"}

# Hostname patterns that indicate WD NAS
NAS_HOSTNAME_PATTERNS = re.compile(
    r'mycloud|wdmycloud|wd-mycloud|ex2|ex4|pr2100|pr4100|dl2100|dl4100|nas', re.IGNORECASE
)


def _mac_oui(mac: str) -> str:
    """Normalise MAC and return lowercase OUI (first 3 bytes)."""
    parts = mac.split(":")
    # Pad single-digit hex groups (macOS arp omits leading zeros)
    parts = [p.zfill(2) for p in parts]
    return ":".join(parts[:3]).lower()


def arp_scan() -> List[Dict]:
    """Parse macOS arp -a and return devices with resolved MAC addresses."""
    results = []
    try:
        out = subprocess.check_output(["arp", "-a"], text=True, timeout=5)
        for line in out.splitlines():
            # Match:  hostname (ip) at mac on ifname ...
            m = re.search(r'(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-f:]+)', line)
            if not m:
                continue
            hostname_raw, ip, mac_raw = m.group(1), m.group(2), m.group(3)
            # Normalise MAC (pad leading zeros)
            parts = [p.zfill(2) for p in mac_raw.split(":")]
            mac = ":".join(parts).lower()
            if mac in ("ff:ff:ff:ff:ff:ff",):
                continue
            results.append({
                "ip": ip,
                "mac": mac,
                "hostname_raw": hostname_raw,  # raw from arp table
            })
    except Exception:
        pass
    return results


def _is_wd_by_arp(entry: Dict) -> bool:
    """Identify WD NAS directly from ARP data (MAC OUI or hostname)."""
    if _mac_oui(entry["mac"]) in WD_MAC_OUIS:
        return True
    if NAS_HOSTNAME_PATTERNS.search(entry.get("hostname_raw", "")):
        return True
    return False


async def check_nas_web(ip: str) -> bool:
    """
    Confirm NAS by fetching port 80.
    Reads enough bytes to reach the HTML body where 'My Cloud' appears.
    """
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, 80), timeout=3
        )
        writer.write(
            f"GET / HTTP/1.0\r\nHost: {ip}\r\nConnection: close\r\n\r\n".encode()
        )
        await writer.drain()
        # Read up to 4 KB — enough to pass HTTP headers into the HTML body
        data = await asyncio.wait_for(reader.read(4096), timeout=3)
        writer.close()
        return (
            b"My Cloud" in data
            or b"Western Digital" in data
            or b"MyCloud" in data
            or b"mycloud" in data
            or b"WDMyCloud" in data
            or b"nas/v1/auth" in data      # WD NAS login API endpoint in JS
            or b"login_userName_text" in data  # WD NAS login form element
        )
    except Exception:
        return False


async def ping_host(ip: str, timeout: float = 0.8) -> bool:
    proc = await asyncio.create_subprocess_exec(
        "ping", "-c", "1", "-W", "800", "-t", "1", ip,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        await asyncio.wait_for(proc.wait(), timeout=timeout + 0.5)
        return proc.returncode == 0
    except asyncio.TimeoutError:
        proc.kill()
        return False


async def ping_sweep(subnet_prefix: str, concurrency: int = 60) -> List[str]:
    """Sweep subnet_prefix.1-254 concurrently."""
    sem = asyncio.Semaphore(concurrency)
    alive = []

    async def probe(ip):
        async with sem:
            if await ping_host(ip):
                alive.append(ip)

    await asyncio.gather(*[probe(f"{subnet_prefix}.{i}") for i in range(1, 255)])
    return sorted(alive, key=lambda x: int(x.split(".")[-1]))


async def discover_nas(subnet_prefix: Optional[str] = None) -> List[Dict]:
    """
    Discovery pipeline:
      1. ARP table — identify WD NAS instantly via MAC OUI / hostname
      2. Web signature check — confirm each candidate on port 80
      3. Ping sweep (if subnet_prefix given) — catch devices not yet in ARP
    """
    arp_results = arp_scan()
    arp_by_ip = {r["ip"]: r for r in arp_results}

    # Fast path: IPs that look like WD NAS from ARP alone
    wd_candidates = [r["ip"] for r in arp_results if _is_wd_by_arp(r)]

    # Slower path: all IPs with a valid MAC in the subnet (filter by prefix)
    prefix_filter = subnet_prefix + "." if subnet_prefix else None
    other_candidates = [
        r["ip"] for r in arp_results
        if not _is_wd_by_arp(r)
        and (prefix_filter is None or r["ip"].startswith(prefix_filter))
    ]

    # Ping sweep for hosts not in ARP yet
    sweep_ips: List[str] = []
    if subnet_prefix:
        alive = await ping_sweep(subnet_prefix)
        sweep_ips = [ip for ip in alive if ip not in arp_by_ip]

    all_to_check = list(dict.fromkeys(wd_candidates + other_candidates + sweep_ips))

    # Web-signature check (skip for confirmed WD OUI/hostname — already reliable)
    confirmed_fast = set(wd_candidates)

    async def _check(ip):
        if ip in confirmed_fast:
            return True
        return await check_nas_web(ip)

    web_checks = await asyncio.gather(*[_check(ip) for ip in all_to_check])

    results = []
    for ip, is_nas in zip(all_to_check, web_checks):
        if not is_nas and ip not in confirmed_fast:
            continue
        arp = arp_by_ip.get(ip, {})
        mac = arp.get("mac", "unknown")
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except Exception:
            hostname = arp.get("hostname_raw", ip)
        results.append({"ip": ip, "mac": mac, "hostname": hostname})

    return results
