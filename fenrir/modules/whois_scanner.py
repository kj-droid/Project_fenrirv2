# fenrir/modules/whois_scanner.py
import asyncio
import whois
from ..logging_config import log

class WhoisScanner:
    """
    Performs a WHOIS lookup to retrieve domain registration information.
    """
    def __init__(self):
        log.debug("WHOIS Scanner module initialized.")

    async def run(self, target_domain: str):
        """
        Runs the WHOIS lookup for the target domain.
        """
        log.info(f"Starting WHOIS lookup for {target_domain}...")
        
        try:
            # The 'whois' library is synchronous, so we run it in a separate
            # thread to avoid blocking our async application.
            domain_info = await asyncio.to_thread(whois.whois, target_domain)

            if domain_info.registrar:
                log.info("WHOIS information found:")
                # Log key details if they exist in the response
                if domain_info.registrar:
                    log.info(f"  - Registrar: {domain_info.registrar}")
                if domain_info.creation_date:
                    log.info(f"  - Creation Date: {domain_info.creation_date}")
                if domain_info.expiration_date:
                    log.info(f"  - Expiration Date: {domain_info.expiration_date}")
                if domain_info.name_servers:
                    log.info(f"  - Name Servers: {', '.join(domain_info.name_servers)}")
            else:
                log.warning(f"No WHOIS information found for {target_domain}. It may be a private or non-existent domain.")

        except Exception as e:
            log.error(f"An error occurred during WHOIS lookup for {target_domain}: {e}")
        
        log.info("WHOIS lookup finished.")
