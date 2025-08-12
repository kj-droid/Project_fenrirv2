# fenrir/modules/tech_detector.py
import asyncio
import webtech
from ..logging_config import log

class TechDetector:
    """
    Identifies technologies used by a website.
    """
    def __init__(self):
        log.debug("Technology Detector module initialized.")

    async def run(self, target_ip: str, web_ports: list[int]):
        """
        Runs the technology detection scan against web servers on given ports.
        """
        log.info(f"Starting technology detection on {target_ip} for ports: {web_ports}")
        if not web_ports:
            log.warning("No web ports found or specified. Skipping technology detection.")
            return

        for port in web_ports:
            protocol = "https" if port == 443 else "http"
            base_url = f"{protocol}://{target_ip}:{port}"
            
            log.info(f"Analyzing technologies on {base_url}...")
            
            try:
                # The 'webtech' library is synchronous, so we run it in a thread.
                wt = await asyncio.to_thread(webtech.WebTech)
                results = await asyncio.to_thread(wt.start_from_url, base_url, timeout=10)
                
                if results:
                    log.info(f"Technologies found for {base_url}:")
                    # Sort results for consistent output
                    sorted_tech = sorted(results.items(), key=lambda item: item[0])
                    for tech, info in sorted_tech:
                        version = f" (Version: {info['version']})" if info['version'] else ""
                        log.info(f"  - {tech}{version}")
                else:
                    log.info(f"No specific technologies detected for {base_url}.")

            except Exception as e:
                log.error(f"An error occurred during technology detection for {base_url}: {e}")
        
        log.info("Technology detection finished.")

