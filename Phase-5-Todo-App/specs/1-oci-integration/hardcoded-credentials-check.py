"""
Hardcoded credentials verification script
This script checks for hardcoded credentials in code and configuration files
"""

import os
import re
import json
import yaml
from typing import List, Dict, Tuple
from pathlib import Path
import argparse


class HardcodedCredentialsChecker:
    """
    Checker for hardcoded credentials in code and configuration files
    """

    def __init__(self):
        # Regex patterns for various types of credentials
        self.patterns = {
            'api_key': r'(?i)(?:api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token)["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})["\']?',
            'password': r'(?i)(?:password|pwd|pass)["\']?\s*[:=]\s*["\']?([A-Za-z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]{6,})["\']?',
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'secret_key': r'(?i)secret["\']?\s*[:=]\s*["\']?([A-Za-z0-9+/=_-]{20,})["\']?',
            'database_url': r'(?i)(?:database[_-]?url|db[_-]?connection)["\']?\s*[:=]\s*["\']?(?:postgres|mysql|mariadb|mongodb)://[^"\']+[\'"]?',
            'private_key': r'-----BEGIN(?: (RSA|OPENSSH|DSA|EC))? PRIVATE KEY(?: BLOCK)?-----',
            'oauth_token': r'[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com',
            'slack_token': r'xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}',
            'ssh_key': r'ssh-(rsa|dss|ed25519) [A-Za-z0-9+\/]+[=]{0,3}(?:\s+.+@.+)?',
            'bearer_token': r'(?i)bearer\s+([A-Za-z0-9\._\-~]+)',
            'jwt_token': r'eyJ[A-Za-z0-9_=-]+\.[A-Za-z0-9_=-]+\.[A-Za-z0-9_=-]*',
            'generic_secret': r'(?i)(?:secret|token|key|credential|auth)["\']?\s*[:=]\s*["\']?([A-Za-z0-9+/=_-]{15,})["\']?'
        }

        # File extensions to scan
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs',
            '.php', '.rb', '.go', '.rs', '.scala', '.kt', '.sql', '.sh', '.bash',
            '.env', '.conf', '.cfg', '.ini', '.xml', '.json', '.yaml', '.yml', '.toml'
        }

        # Files and directories to exclude
        self.exclude_patterns = {
            '.git', '__pycache__', 'node_modules', '.vscode', '.idea', 'dist', 'build',
            'target', '.terraform', '.pytest_cache', '*.egg-info', '.tox', 'venv', 'env'
        }

    def is_excluded_path(self, path: str) -> bool:
        """
        Check if a path should be excluded from scanning

        Args:
            path: Path to check

        Returns:
            Boolean indicating if path should be excluded
        """
        path_parts = Path(path).parts
        for part in path_parts:
            if part in self.exclude_patterns or any(excl in part for excl in self.exclude_patterns if '*' in excl):
                return True
        return False

    def scan_file(self, file_path: str) -> List[Dict[str, any]]:
        """
        Scan a single file for hardcoded credentials

        Args:
            file_path: Path to the file to scan

        Returns:
            List of findings in the file
        """
        findings = []

        try:
            # Determine if file is binary by attempting to read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Skip if file appears to be binary
            if '\x00' in content:
                return []

            # Check each line for patterns
            lines = content.splitlines()
            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern in self.patterns.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Skip common false positives
                        if self.is_false_positive(match.group(0)):
                            continue

                        finding = {
                            'file': file_path,
                            'line_number': line_num,
                            'column_start': match.start(),
                            'column_end': match.end(),
                            'matched_text': match.group(0)[:100],  # Limit length
                            'pattern_type': pattern_name,
                            'line_content': line.strip()
                        }
                        findings.append(finding)

        except Exception as e:
            print(f"Error scanning file {file_path}: {str(e)}")

        return findings

    def is_false_positive(self, matched_text: str) -> bool:
        """
        Check if a matched pattern is likely a false positive

        Args:
            matched_text: The matched text to check

        Returns:
            Boolean indicating if it's a false positive
        """
        # Common false positive patterns
        false_positives = [
            r'^[0-9]+$',  # Just numbers
            r'password:\s*""',  # Empty password
            r'password:\s*\'\'',  # Empty password
            r'password:\s*null',  # Null password
            r'password:\s*undefined',  # Undefined password
            r'test',  # Contains 'test'
            r'dummy',  # Contains 'dummy'
            r'example',  # Contains 'example'
            r'placeholder',  # Contains 'placeholder'
            r'dev',  # Contains 'dev' (likely dev environment)
            r'sample',  # Contains 'sample'
        ]

        text_lower = matched_text.lower()
        for fp_pattern in false_positives:
            if re.search(fp_pattern, text_lower):
                return True

        return False

    def scan_directory(self, directory: str) -> List[Dict[str, any]]:
        """
        Scan a directory for hardcoded credentials

        Args:
            directory: Directory path to scan

        Returns:
            List of all findings in the directory
        """
        all_findings = []

        for root, dirs, files in os.walk(directory):
            # Remove excluded directories from walk
            dirs[:] = [d for d in dirs if not self.is_excluded_path(os.path.join(root, d))]

            for file in files:
                file_path = os.path.join(root, file)

                # Check if file extension is one we want to scan
                if Path(file_path).suffix.lower() in self.code_extensions:
                    if not self.is_excluded_path(file_path):
                        findings = self.scan_file(file_path)
                        all_findings.extend(findings)

        return all_findings

    def check_environment_variables_usage(self, directory: str) -> List[Dict[str, any]]:
        """
        Check for proper environment variable usage instead of hardcoded values

        Args:
            directory: Directory to scan

        Returns:
            List of files that might be missing environment variable usage
        """
        findings = []

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not self.is_excluded_path(os.path.join(root, d))]

            for file in files:
                if Path(file).suffix.lower() in {'.py', '.js', '.ts', '.java', '.go'}:
                    file_path = os.path.join(root, file)

                    if not self.is_excluded_path(file_path):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        # Look for hardcoded strings that should be environment variables
                        potential_issues = re.findall(r'["\']((?:password|secret|token|key|auth|api)[^"\']{0,50})["\']\s*[:=]', content, re.IGNORECASE)

                        for issue in potential_issues:
                            if not any(skip in issue.lower() for skip in ['test', 'dummy', 'example', 'placeholder']):
                                findings.append({
                                    'file': file_path,
                                    'issue': f'Possible hardcoded credential: {issue}',
                                    'recommendation': 'Consider using environment variables instead'
                                })

        return findings

    def generate_report(self, findings: List[Dict[str, any]], output_file: str = None):
        """
        Generate a report of findings

        Args:
            findings: List of findings to include in report
            output_file: Optional file to save report to
        """
        if not findings:
            print("✅ No hardcoded credentials found!")
            report = {
                'status': 'PASS',
                'findings_count': 0,
                'findings': [],
                'summary': 'No hardcoded credentials detected in scanned files.'
            }
        else:
            print(f"⚠️  Found {len(findings)} potential hardcoded credentials!")
            report = {
                'status': 'FAIL',
                'findings_count': len(findings),
                'findings': findings,
                'summary': f'{len(findings)} potential hardcoded credentials detected.'
            }

            for i, finding in enumerate(findings, 1):
                print(f"\n{i}. File: {finding['file']}")
                print(f"   Line: {finding['line_number']}")
                print(f"   Type: {finding['pattern_type']}")
                print(f"   Matched: {finding['matched_text']}")
                print(f"   Context: {finding['line_content'][:100]}...")

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to {output_file}")

        return report


def main():
    """
    Main function to run the hardcoded credentials checker
    """
    parser = argparse.ArgumentParser(description='Check for hardcoded credentials in code and config files')
    parser.add_argument('directory', nargs='?', default='.',
                       help='Directory to scan (default: current directory)')
    parser.add_argument('-o', '--output',
                       help='Output file for JSON report')
    parser.add_argument('--exclude', nargs='*',
                       help='Additional patterns to exclude')

    args = parser.parse_args()

    print(f"Starting hardcoded credentials scan in: {args.directory}")

    checker = HardcodedCredentialsChecker()

    # Add any additional exclusions
    if args.exclude:
        checker.exclude_patterns.update(args.exclude)

    # Scan the directory
    findings = checker.scan_directory(args.directory)

    # Also check for environment variable usage patterns
    env_findings = checker.check_environment_variables_usage(args.directory)

    # Combine findings
    all_findings = findings + env_findings

    # Generate report
    report = checker.generate_report(all_findings, args.output)

    # Check for configuration files that might contain secrets
    config_files_to_check = [
        'config.json', 'config.yaml', 'config.yml', 'settings.json',
        '.env', '.env.local', '.env.production', '.env.development',
        'secrets.yaml', 'secrets.yml', 'application.properties',
        'values.yaml', 'helm-values.yaml'
    ]

    print(f"\nChecking for sensitive configuration files...")
    sensitive_files = []

    for root, dirs, files in os.walk(args.directory):
        dirs[:] = [d for d in dirs if not checker.is_excluded_path(os.path.join(root, d))]

        for file in files:
            if file.lower() in [cf.lower() for cf in config_files_to_check]:
                file_path = os.path.join(root, file)
                if not checker.is_excluded_path(file_path):
                    sensitive_files.append(file_path)

    if sensitive_files:
        print(f"⚠️  Found {len(sensitive_files)} potentially sensitive configuration files:")
        for sf in sensitive_files:
            print(f"  - {sf}")
        print("  Please review these files manually for hardcoded credentials.")
    else:
        print("✅ No sensitive configuration files found.")

    # Final summary
    print(f"\n{'='*60}")
    print("HARDCODED CREDENTIALS CHECK COMPLETE")
    print(f"{'='*60}")

    if report['status'] == 'PASS':
        print("🎉 No hardcoded credentials detected!")
        print("✅ Your codebase appears to be free of hardcoded credentials.")
        exit_code = 0
    else:
        print("❌ Hardcoded credentials detected!")
        print("🚨 Please remove all hardcoded credentials before deployment.")
        print("💡 Recommended: Use environment variables or secure secret stores.")
        exit_code = 1

    print(f"{'='*60}")

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)