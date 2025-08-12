# fenrir/modules/dns_scanner.py
import asyncio
import aiodns
from ..logging_config import log

class DnsScanner:
    """
    Performs DNS enumeration to find common records for a domain.
    """
    def __init__(self):
        log.debug("DNS Scanner module initialized.")
        self.record_types = ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]
        self.resolver = aiodns.DNSResolver()

    async def query_record(self, target_domain: str, record_type: str):
        """Queries for a specific type of DNS record."""
        try:
            results = await self.resolver.query(target_domain, record_type)
            log.info(f"Found {record_type} records for {target_domain}:")
            
            # Handle each record type according to its specific attributes
            for res in results:
                if record_type == "MX":
                    log.info(f"  - {res.host} (priority {res.priority})")
                elif record_type == "TXT":
                    # TXT records can be a list of bytes, so we decode and join them
                    log.info(f"  - {' '.join(t.decode('utf-8') for t in res.text)}")
                elif record_type == "CNAME":
                    log.info(f"  - {res.cname}")
                elif hasattr(res, 'host'):
                    # Handles A, AAAA, NS records which all have a 'host' attribute
                    log.info(f"  - {res.host}")
                else:
                    # Fallback for any other record types
                    log.info(f"  - {res}")

        except aiodns.error.DNSError:
            log.debug(f"No {record_type} records found for {target_domain}.")
        except Exception as e:
            log.error(f"An error occurred querying {record_type} for {target_domain}: {e}")

    async def run(self, target_domain: str):
        """
        Runs the DNS enumeration scan.
        """
        log.info(f"Starting DNS enumeration for {target_domain}...")
        
        tasks = [
            self.query_record(target_domain, rec_type) for rec_type in self.record_types
        ]
        await asyncio.gather(*tasks)
        
        log.info("DNS enumeration finished.")
