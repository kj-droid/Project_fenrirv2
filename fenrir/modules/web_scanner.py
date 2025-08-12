# fenrir/modules/web_scanner.py
import asyncio
import httpx
from ..logging_config import log

class WebScanner:
    """
    Performs basic web server reconnaissance, including header fetching
    and directory brute-forcing.
    """
    def __init__(self):
        log.debug("Web Scanner module initialized.")
        # A small list of common directories/files to check for.
        # This can be expanded or loaded from a file in the future.
        self.common_paths = [
            "/", "/robots.txt", "/admin", "/login", "/dashboard",
            "/wp-admin", "/administrator", "/.git/config", "/.env"
        ]

    async def fetch_headers(self, client: httpx.AsyncClient, base_url: str):
        """Fetches and displays HTTP headers from the target URL."""
        try:
            log.info(f"Fetching headers from {base_url}...")
            response = await client.get(base_url, follow_redirects=True)
            log.info(f"Status Code: {response.status_code} at {response.url}")
            for key, value in response.headers.items():
                log.info(f"  {key}: {value}")
        except httpx.RequestError as e:
            log.warning(f"Could not fetch headers from {base_url}: {e}")

    async def check_path(self, client: httpx.AsyncClient, base_url: str, path: str) -> tuple[str, int] | None:
        """Checks if a specific path exists on the web server."""
        url_to_check = f"{base_url.rstrip('/')}{path}"
        try:
            response = await client.head(url_to_check, follow_redirects=True, timeout=5.0)
            # We consider anything other than a 404 as potentially interesting.
            if response.status_code != 404:
                return (url_to_check, response.status_code)
        except httpx.RequestError:
            # Ignore connection errors for individual paths
            pass
        return None

    async def run(self, target_ip: str, web_ports: list[int]):
        """
        Runs the web scan against a list of ports known to host web services.
        """
        log.info(f"Starting web scan on {target_ip} for ports: {web_ports}")
        if not web_ports:
            log.warning("No web ports (80, 443, 8080) found or specified. Skipping web scan.")
            return

        async with httpx.AsyncClient(verify=False) as client: # verify=False ignores SSL certificate errors
            for port in web_ports:
                protocol = "https" if port == 443 else "http"
                base_url = f"{protocol}://{target_ip}:{port}"
                
                await self.fetch_headers(client, base_url)

                log.info(f"Starting directory brute-force on {base_url}...")
                tasks = [self.check_path(client, base_url, path) for path in self.common_paths]
                results = await asyncio.gather(*tasks)

                found_paths = [res for res in results if res is not None]

                if found_paths:
                    log.info("Found the following interesting paths:")
                    for url, status_code in found_paths:
                        log.info(f"  - {url} (Status: {status_code})")
                else:
                    log.info("No common paths discovered.")
        
        log.info("Web scan finished.")

