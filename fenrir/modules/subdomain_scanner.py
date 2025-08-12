# fenrir/modules/subdomain_scanner.py
import asyncio
import socket
from ..logging_config import log

class SubdomainScanner:
    """
    Performs subdomain enumeration using a wordlist to find valid hostnames.
    """
    def __init__(self):
        log.debug("Subdomain Scanner module initialized.")
        # A small, common wordlist for subdomain brute-forcing.
        # In a future version, this could be loaded from a user-specified file.
        self.wordlist = [
            "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1",
            "webdisk", "ns2", "cpanel", "whm", "autodiscover", "autoconfig",
            "m", "test", "dev", "staging", "api", "blog", "shop"
        ]

    async def resolve_subdomain(self, target_domain: str, subdomain: str) -> str | None:
        """
        Tries to resolve a single subdomain. Returns the subdomain if found.
        """
        hostname = f"{subdomain}.{target_domain}"
        try:
            # Run the blocking socket.gethostbyname in a separate thread
            # to avoid blocking the asyncio event loop.
            await asyncio.to_thread(socket.gethostbyname, hostname)
            log.info(f"Found subdomain: {hostname}")
            return hostname
        except socket.gaierror:
            # This means the subdomain does not exist.
            log.debug(f"Subdomain not found: {hostname}")
            return None

    async def run(self, target_domain: str, concurrency: int = 50):
        """
        Runs the subdomain enumeration scan.

        Args:
            target_domain: The root domain to scan (e.g., example.com).
        """
        log.info(f"Starting subdomain scan on {target_domain} with {len(self.wordlist)} common names.")
        
        tasks = [
            self.resolve_subdomain(target_domain, sub) for sub in self.wordlist
        ]
        
        results = await asyncio.gather(*tasks)
        
        found_subdomains = sorted([res for res in results if res is not None])
        
        if found_subdomains:
            log.info(f"Subdomain scan complete. Found {len(found_subdomains)} subdomain(s):")
            for sub in found_subdomains:
                log.info(f"  - {sub}")
        else:
            log.info("Subdomain scan complete. No common subdomains found.")

        log.info("Subdomain scan finished.")
