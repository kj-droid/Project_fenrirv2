# fenrir/modules/dir_brute_forcer.py
import asyncio
import httpx
from ..logging_config import log

class DirBruteForcer:
    """
    Performs directory and file brute-forcing using a wordlist.
    """
    def __init__(self):
        log.debug("Directory Brute-Forcer module initialized.")
        # A more extensive wordlist for directories and files.
        # This should be loaded from an external file in a future version.
        self.wordlist = [
            "admin", "login", "dashboard", "test", "dev", "staging", "api",
            "backup", "backups", "old", "temp", "tmp", "files", "assets",
            "images", "img", "css", "js", "scripts", "includes", "lib",
            "vendor", "uploads", "downloads", "config", "system", "logs",
            "phpmyadmin", "pma", "webadmin", "sql", "db", "database",
            "robots.txt", "sitemap.xml", ".htaccess", ".htpasswd", ".env",
            "config.php", "config.json", "package.json", "Dockerfile",
            "docker-compose.yml", "README.md", "CHANGELOG.md", "LICENSE"
        ]

    async def check_path(self, client: httpx.AsyncClient, base_url: str, path: str) -> tuple[str, int] | None:
        """Checks a single path for existence."""
        url_to_check = f"{base_url.rstrip('/')}/{path}"
        try:
            response = await client.head(url_to_check, follow_redirects=True, timeout=5.0)
            if response.status_code != 404:
                log.info(f"Found Path: {url_to_check} (Status: {response.status_code})")
                return (url_to_check, response.status_code)
        except httpx.RequestError:
            pass
        return None

    async def run(self, target_ip: str, web_ports: list[int], concurrency: int = 50):
        """
        Runs the directory brute-force scan against web servers on given ports.
        """
        log.info(f"Starting directory brute-force on {target_ip} for ports: {web_ports}")
        if not web_ports:
            log.warning("No web ports found or specified. Skipping directory brute-force.")
            return

        async with httpx.AsyncClient(verify=False) as client:
            for port in web_ports:
                protocol = "https" if port == 443 else "http"
                base_url = f"{protocol}://{target_ip}:{port}"
                
                log.info(f"Brute-forcing {len(self.wordlist)} paths on {base_url}...")
                
                semaphore = asyncio.Semaphore(concurrency)
                
                async def bounded_check(path):
                    async with semaphore:
                        return await self.check_path(client, base_url, path)

                tasks = [bounded_check(path) for path in self.wordlist]
                results = await asyncio.gather(*tasks)

                found_paths = [res for res in results if res is not None]

                if not found_paths:
                    log.info(f"No common directories or files discovered on {base_url}.")
        
        log.info("Directory and file brute-force scan finished.")
