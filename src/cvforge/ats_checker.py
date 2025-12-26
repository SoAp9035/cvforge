"""
ATS (Applicant Tracking System) Friendliness Checker for CVForge.

This module analyzes PDF files to determine if they are ATS-friendly.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Try to import pypdf, but make it optional
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


# Standard fonts that are known to be ATS-friendly
ATS_FRIENDLY_FONTS = {
    # Sans-serif fonts
    "arial", "helvetica", "calibri", "verdana", "tahoma",
    "trebuchet", "trebuchet ms", "lucida", "lucida sans",
    # Serif fonts
    "times", "times new roman", "georgia", "garamond",
    "cambria", "palatino",
    # Monospace (sometimes used for technical CVs)
    "courier", "courier new",
    # Common open-source alternatives
    "noto sans", "noto serif", "roboto", "liberation sans",
    "liberation serif", "dejavu sans", "dejavu serif",
    "inter", "source sans", "source sans pro", "open sans",
    "lato", "montserrat", "raleway", "ubuntu",
}

# Expected CV sections (both English and Turkish)
EXPECTED_SECTIONS = {
    "summary", "özet", "professional summary", "profile", "profil",
    "experience", "work experience", "deneyim", "iş deneyimi",
    "education", "eğitim",
    "skills", "technical skills", "yetenekler", "teknik yetenekler",
    "projects", "projeler",
    "certifications", "sertifikalar", "certificates",
    "languages", "diller",
    "awards", "ödüller",
    "interests", "ilgi alanları",
}

# Maximum recommended file size (1MB)
MAX_FILE_SIZE_MB = 1.0
MAX_FILE_SIZE_BYTES = int(MAX_FILE_SIZE_MB * 1024 * 1024)

# CV-specific limits
MAX_PAGES = 5  # CVs should be 1-2 pages, max 5 for senior roles
MAX_TEXT_LENGTH = 15000  # CVs rarely exceed 15k characters
MIN_SECTIONS = 3  # A CV should have at least 3 recognizable sections


@dataclass
class ATSCheck:
    """Represents a single ATS check result."""
    name: str
    passed: bool
    message: str
    severity: str = "info"  # info, warning, error
    is_critical: bool = False  # If True, failing this check fails the whole report


@dataclass
class ATSReport:
    """Complete ATS analysis report."""
    file_path: str
    checks: list[ATSCheck] = field(default_factory=list)
    overall_verdict: str = "Unknown"
    score: int = 0
    max_score: int = 0
    
    def add_check(self, check: ATSCheck):
        """Add a check result to the report."""
        self.checks.append(check)
    
    def calculate_score(self):
        """Calculate overall score based on checks."""
        self.max_score = len(self.checks)
        self.score = sum(1 for c in self.checks if c.passed)
        
        # If any critical check failed, mark as not a CV
        critical_failed = any(c.is_critical and not c.passed for c in self.checks)
        
        if critical_failed:
            self.overall_verdict = "Not a CV"
        elif self.score == self.max_score:
            self.overall_verdict = "Excellent"
        elif self.score >= self.max_score * 0.8:
            self.overall_verdict = "Good"
        elif self.score >= self.max_score * 0.6:
            self.overall_verdict = "Fair"
        else:
            self.overall_verdict = "Needs Improvement"


class ATSChecker:
    """Analyzer for PDF ATS-friendliness."""
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.reader: Optional[PdfReader] = None
        self.extracted_text: Optional[str] = None
        self.fonts_used: set[str] = set()
    
    def load_pdf(self) -> bool:
        """Load the PDF file. Returns True if successful."""
        if not PYPDF_AVAILABLE:
            return False
        
        try:
            self.reader = PdfReader(str(self.pdf_path))
            return True
        except Exception:
            return False
    
    def extract_text(self) -> Optional[str]:
        """Extract all text from the PDF."""
        if not self.reader:
            return None
        
        try:
            text_parts = []
            for page in self.reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            self.extracted_text = "\n".join(text_parts)
            return self.extracted_text
        except Exception:
            return None
    
    def get_fonts(self) -> set[str]:
        """Extract font names used in the PDF."""
        if not self.reader:
            return set()
        
        fonts = set()
        try:
            for page in self.reader.pages:
                if "/Resources" in page:
                    resources = page["/Resources"]
                    if "/Font" in resources:
                        font_dict = resources["/Font"]
                        for font_key in font_dict:
                            font = font_dict[font_key]
                            if "/BaseFont" in font:
                                font_name = str(font["/BaseFont"]).lstrip("/")
                                # Clean up font name (remove subset prefix like ABCDEF+)
                                if "+" in font_name:
                                    font_name = font_name.split("+", 1)[1]
                                fonts.add(font_name.lower())
        except Exception:
            pass
        
        self.fonts_used = fonts
        return fonts
    
    def check_file_size(self) -> ATSCheck:
        """Check if file size is within ATS limits."""
        try:
            size_bytes = os.path.getsize(self.pdf_path)
            size_mb = size_bytes / (1024 * 1024)
            
            if size_bytes <= MAX_FILE_SIZE_BYTES:
                return ATSCheck(
                    name="File Size",
                    passed=True,
                    message=f"File size is {size_mb:.2f}MB (under {MAX_FILE_SIZE_MB}MB limit)",
                    severity="info"
                )
            else:
                return ATSCheck(
                    name="File Size",
                    passed=False,
                    message=f"File size is {size_mb:.2f}MB (over {MAX_FILE_SIZE_MB}MB recommended limit)",
                    severity="warning"
                )
        except Exception as e:
            return ATSCheck(
                name="File Size",
                passed=False,
                message=f"Could not determine file size: {e}",
                severity="error"
            )
    
    def check_text_extraction(self) -> ATSCheck:
        """Check if text can be extracted from the PDF."""
        text = self.extract_text()
        
        if text is None:
            return ATSCheck(
                name="Text Extraction",
                passed=False,
                message="Could not extract text from PDF (may be image-based or corrupted)",
                severity="error"
            )
        
        if len(text.strip()) < 50:
            return ATSCheck(
                name="Text Extraction",
                passed=False,
                message="Very little text extracted - PDF may be image-based",
                severity="error"
            )
        
        return ATSCheck(
            name="Text Extraction",
            passed=True,
            message=f"Successfully extracted {len(text)} characters of text",
            severity="info"
        )
    
    def check_fonts(self) -> ATSCheck:
        """Check if fonts used are ATS-friendly."""
        fonts = self.get_fonts()
        
        if not fonts:
            return ATSCheck(
                name="Font Analysis",
                passed=True,
                message="No embedded fonts detected (using standard fonts)",
                severity="info"
            )
        
        # Normalize and check fonts
        non_friendly = []
        for font in fonts:
            # Check if any ATS-friendly font name is contained in the font name
            font_lower = font.lower()
            is_friendly = any(
                friendly in font_lower 
                for friendly in ATS_FRIENDLY_FONTS
            )
            if not is_friendly:
                non_friendly.append(font)
        
        if not non_friendly:
            return ATSCheck(
                name="Font Analysis",
                passed=True,
                message=f"All {len(fonts)} fonts are ATS-friendly",
                severity="info"
            )
        else:
            return ATSCheck(
                name="Font Analysis",
                passed=True,  # Still pass, just warn
                message=f"Found fonts: {', '.join(fonts)}. Some may not be standard.",
                severity="warning"
            )
    
    def check_structure(self) -> ATSCheck:
        """Check if CV has expected sections."""
        if not self.extracted_text:
            self.extract_text()
        
        if not self.extracted_text:
            return ATSCheck(
                name="Structure",
                passed=False,
                message="Cannot analyze structure - no text extracted",
                severity="error"
            )
        
        text_lower = self.extracted_text.lower()
        found_sections = []
        
        for section in EXPECTED_SECTIONS:
            if section in text_lower:
                found_sections.append(section)
        
        if len(found_sections) >= MIN_SECTIONS:
            return ATSCheck(
                name="Structure",
                passed=True,
                message=f"Found {len(found_sections)} recognizable CV sections",
                severity="info"
            )
        elif len(found_sections) >= 1:
            return ATSCheck(
                name="Structure",
                passed=False,
                message=f"Only found {len(found_sections)} CV section(s). Expected at least {MIN_SECTIONS}.",
                severity="warning"
            )
        else:
            return ATSCheck(
                name="Structure",
                passed=False,
                message="No standard CV section headings found (e.g., Experience, Education, Skills)",
                severity="error",
                is_critical=True
            )
    
    def check_page_count(self) -> ATSCheck:
        """Check if CV has reasonable page count."""
        if not self.reader:
            return ATSCheck(
                name="Page Count",
                passed=False,
                message="Could not determine page count",
                severity="error"
            )
        
        num_pages = len(self.reader.pages)
        
        if num_pages <= 2:
            return ATSCheck(
                name="Page Count",
                passed=True,
                message=f"CV has {num_pages} page(s) (ideal: 1-2 pages)",
                severity="info"
            )
        elif num_pages <= MAX_PAGES:
            return ATSCheck(
                name="Page Count",
                passed=True,
                message=f"CV has {num_pages} pages (recommended: 1-2 pages)",
                severity="warning"
            )
        else:
            return ATSCheck(
                name="Page Count",
                passed=False,
                message=f"Document has {num_pages} pages - this is not a CV (max {MAX_PAGES} pages)",
                severity="error",
                is_critical=True
            )
    
    def check_text_length(self) -> ATSCheck:
        """Check if text length is reasonable for a CV."""
        if not self.extracted_text:
            self.extract_text()
        
        if not self.extracted_text:
            return ATSCheck(
                name="Content Length",
                passed=False,
                message="Cannot analyze content - no text extracted",
                severity="error"
            )
        
        text_len = len(self.extracted_text)
        
        if text_len <= MAX_TEXT_LENGTH:
            return ATSCheck(
                name="Content Length",
                passed=True,
                message=f"Content length ({text_len:,} chars) is appropriate for a CV",
                severity="info"
            )
        else:
            return ATSCheck(
                name="Content Length",
                passed=False,
                message=f"Content length ({text_len:,} chars) exceeds typical CV length ({MAX_TEXT_LENGTH:,} chars)",
                severity="error",
                is_critical=True
            )
    
    def analyze(self) -> ATSReport:
        """Run all ATS checks and return a complete report."""
        report = ATSReport(file_path=str(self.pdf_path))
        
        # Load PDF
        if not self.load_pdf():
            report.add_check(ATSCheck(
                name="PDF Load",
                passed=False,
                message="Could not load PDF file. Install 'pypdf' for ATS analysis.",
                severity="error"
            ))
            report.calculate_score()
            return report
        
        # Run checks
        report.add_check(self.check_file_size())
        report.add_check(self.check_page_count())
        report.add_check(self.check_text_extraction())
        report.add_check(self.check_text_length())
        report.add_check(self.check_structure())
        report.add_check(self.check_fonts())
        
        report.calculate_score()
        return report


def format_report(report: ATSReport) -> str:
    """Format the ATS report for console output."""
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("  ATS-Friendliness Report")
    lines.append("=" * 60)
    lines.append(f"  File: {report.file_path}")
    lines.append("-" * 60)
    lines.append("")
    
    for check in report.checks:
        if check.passed:
            icon = "✓"
        elif check.severity == "warning":
            icon = "⚠"
        else:
            icon = "✗"
        
        lines.append(f"  {icon} {check.name}")
        lines.append(f"    {check.message}")
        lines.append("")
    
    lines.append("-" * 60)
    lines.append(f"  Overall: {report.overall_verdict} ({report.score}/{report.max_score} checks passed)")
    lines.append("=" * 60)
    
    # Add verdict message
    if report.overall_verdict == "Not a CV":
        lines.append("  ✗ This document does not appear to be a CV/Resume.")
    elif report.overall_verdict == "Excellent":
        lines.append("  ✓ This PDF is ATS-friendly!")
    elif report.overall_verdict == "Good":
        lines.append("  ✓ This PDF should work well with most ATS systems.")
    elif report.overall_verdict == "Fair":
        lines.append("  ⚠ This PDF may have some ATS compatibility issues.")
    else:
        lines.append("  ✗ This PDF may not be parsed correctly by ATS systems.")
    
    lines.append("")
    
    return "\n".join(lines)


def check_ats(pdf_path: Path) -> tuple[ATSReport, str]:
    """
    Analyze a PDF for ATS-friendliness.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Tuple of (ATSReport, formatted string output)
    """
    checker = ATSChecker(pdf_path)
    report = checker.analyze()
    output = format_report(report)
    return report, output
