# fenrir/report_manager.py
import os
from datetime import datetime
from .logging_config import log

class ReportManager:
    """Handles the creation and writing of scan reports to files."""
    def __init__(self, output_dir: str, target: str):
        self.output_dir = output_dir
        self.target = target
        self.start_time = datetime.now()
        
        # Create a unique report file for this scan session
        filename = f"fenrir_report_{self.target}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.txt"
        self.report_path = os.path.join(self.output_dir, filename)
        
        log.info(f"Report will be saved to: {self.report_path}")
        self._write_header()

    def _write_header(self):
        """Writes the initial header to the report file."""
        with open(self.report_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write(f" Fenrir Security Scan Report\n")
            f.write("="*60 + "\n")
            f.write(f"Target: {self.target}\n")
            f.write(f"Scan Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")

    def add_section(self, title: str, content: list[str]):
        """Adds a new section with a title and content to the report."""
        if not content:
            return # Don't add empty sections
            
        with open(self.report_path, 'a') as f:
            f.write(f"--- {title.upper()} ---\n")
            for line in content:
                f.write(f"{line}\n")
            f.write("\n")
        log.info(f"Added '{title}' section to the report.")

