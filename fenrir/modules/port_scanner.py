# fenrir/modules/port_scanner.py
import asyncio
from ..logging_config import log

class PortScanner:
    """An asynchronous TCP port scanner."""
    def __init__(self):
        log.debug("Port Scanner module initialized.")

    async def scan_port(self, target_ip: str, port: int, timeout: float = 1.0) -> tuple[int, bool]:
        """Scans a single TCP port."""
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(target_ip, port), timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            return port, True
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return port, False

    async def run(self, target_ip: str, ports: list[int], concurrency: int = 100) -> list[int]:
        """Runs a concurrent scan on a list of ports."""
        log.info(f"Starting port scan on {target_ip} for {len(ports)} ports...")
        semaphore = asyncio.Semaphore(concurrency)
        
        async def bounded_scan(port):
            async with semaphore:
                return await self.scan_port(target_ip, port)

        tasks = [asyncio.create_task(bounded_scan(port)) for port in ports]
        results = await asyncio.gather(*tasks)
        
        open_ports = sorted([port for port, is_open in results if is_open])
        
        log.info(f"Scan complete. Found {len(open_ports)} open port(s).")
        if open_ports:
            log.info(f"Open ports: {', '.join(map(str, open_ports))}")
            
        return open_ports
