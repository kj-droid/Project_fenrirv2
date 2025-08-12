# fenrir/cli.py
import argparse
import asyncio
from .logging_config import log
from .modules.port_scanner import PortScanner
from .modules.vulnerability_scanner import VulnerabilityScanner
from .modules.web_scanner import WebScanner
from .modules.subdomain_scanner import SubdomainScanner
from .modules.dir_brute_forcer import DirBruteForcer
from .modules.dns_scanner import DnsScanner
from .modules.whois_scanner import WhoisScanner
from .modules.tech_detector import TechDetector
from .modules.threat_intel_scanner import ThreatIntelScanner
from .modules.osint_scanner import OsintScanner
from .modules.exploit_scanner import ExploitScanner

async def run_scans(
    target: str,
    ports_to_scan: list[int] | None,
    scan_vulns: bool,
    scan_web: bool,
    scan_subdomains: bool,
    scan_dirs: bool,
    scan_dns: bool,
    scan_whois: bool,
    scan_tech: bool,
    scan_intel: bool,
    scan_osint: bool,
    exploit_query: str | None,
):
    """
    Orchestrates the execution of different scan modules based on arguments.
    """
    # Standalone scans that don't depend on port scans
    if scan_subdomains:
        await SubdomainScanner().run(target)
    if scan_dns:
        await DnsScanner().run(target)
    if scan_whois:
        await WhoisScanner().run(target)
    if scan_intel:
        await ThreatIntelScanner().run(target)
    if scan_osint:
        await OsintScanner().run(target)
    if exploit_query:
        await ExploitScanner().run(exploit_query)

    # Port-based scans
    if any([ports_to_scan, scan_vulns, scan_web, scan_dirs, scan_tech]):
        if not ports_to_scan:
            ports_to_scan = [
                21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
                3000, 3001, 3306, 3389, 5000, 5001, 8000, 8008, 8080, 8443, 8888
            ]
            log.info(f"No ports specified with -p. Using default list for scans.")
        
        open_ports = await PortScanner().run(target, ports_to_scan)

        if scan_vulns:
            await VulnerabilityScanner().run(target, open_ports)
        
        web_ports = [p for p in open_ports if p in [
            80, 443, 3000, 3001, 5000, 5001, 8000, 8008, 8080, 8443, 8888
        ]]

        if scan_web:
            await WebScanner().run(target, web_ports)
        if scan_dirs:
            await DirBruteForcer().run(target, web_ports)
        if scan_tech:
            await TechDetector().run(target, web_ports)


def main():
    """Main entry point for the Fenrir CLI."""
    parser = argparse.ArgumentParser(
        description="Fenrir Security Scanner",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # Target is now optional for scans that don't require it (like exploit search)
    parser.add_argument("target", nargs='?', default=None, help="The target IP address or hostname to scan.")
    
    # Group for different scan types
    scan_group = parser.add_argument_group("Scan Modules")
    scan_group.add_argument("-p", "--ports", help="Comma-separated list of ports to scan.")
    scan_group.add_argument("-sV", "--scan-vulns", action="store_true", help="Run vulnerability scan on open ports.")
    scan_group.add_argument("-sW", "--scan-web", action="store_true", help="Run web reconnaissance on open HTTP/S ports.")
    scan_group.add_argument("-sD", "--scan-dirs", action="store_true", help="Run directory/file brute-force scan.")
    scan_group.add_argument("-sS", "--scan-subdomains", action="store_true", help="Run subdomain enumeration.")
    scan_group.add_argument("-sN", "--scan-dns", action="store_true", help="Run DNS record enumeration.")
    scan_group.add_argument("-sH", "--scan-whois", action="store_true", help="Run WHOIS lookup on the target domain.")
    scan_group.add_argument("-sT", "--scan-tech", action="store_true", help="Run web technology detection.")
    scan_group.add_argument("-sI", "--scan-intel", action="store_true", help="Run threat intelligence scan (e.g., VirusTotal).")
    scan_group.add_argument("-sO", "--scan-osint", action="store_true", help="Run OSINT scan for public documents and emails.")
    scan_group.add_argument("-sE", "--scan-exploits", metavar="QUERY", help="Search for exploits using a query (e.g., 'Apache 2.4.49').")
    
    args = parser.parse_args()
    
    # Check if a target is required but not provided
    if not args.target and not args.scan_exploits:
        log.error("A target is required for this scan type. Please specify an IP or hostname.")
        parser.print_help()
        return

    ports_to_scan = None
    if args.ports:
        try:
            ports_to_scan = [int(p.strip()) for p in args.ports.split(',')]
        except ValueError:
            log.error("Invalid port format. Please use comma-separated numbers.")
            return

    if not any([args.ports, args.scan_vulns, args.scan_web, args.scan_subdomains, args.scan_dirs, args.scan_dns, args.scan_whois, args.scan_tech, args.scan_intel, args.scan_osint, args.scan_exploits]):
        log.info("No scan type specified. Use --help to see available scan options.")
        parser.print_help()
        return

    try:
        asyncio.run(run_scans(
            args.target, ports_to_scan, args.scan_vulns, args.scan_web,
            args.scan_subdomains, args.scan_dirs, args.scan_dns, args.scan_whois,
            args.scan_tech, args.scan_intel, args.scan_osint, args.scan_exploits
        ))
    except KeyboardInterrupt:
        log.warning("\nScan interrupted by user.")
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
