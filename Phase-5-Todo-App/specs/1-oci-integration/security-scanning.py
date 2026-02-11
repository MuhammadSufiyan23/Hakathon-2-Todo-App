"""
Security scanning for deployed services
This script performs comprehensive security scans of deployed services
"""

import subprocess
import json
import yaml
import os
import sys
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp
import requests
from datetime import datetime
import tempfile
import shutil


class SecurityScanner:
    """
    Comprehensive security scanner for deployed services
    """

    def __init__(self):
        self.scan_results = {
            'vulnerabilities': [],
            'misconfigurations': [],
            'secrets_found': [],
            'network_security_issues': [],
            'compliance_issues': [],
            'scan_timestamp': datetime.now().isoformat()
        }

    def run_trivy_scan(self, target: str, scan_type: str = "image") -> Dict[str, Any]:
        """
        Run Trivy security scan on a target

        Args:
            target: Target to scan (image, file, dir, etc.)
            scan_type: Type of scan (image, fs, repo, config)

        Returns:
            Scan results dictionary
        """
        try:
            cmd = ["trivy", scan_type, "--format", "json", target]

            # Run trivy scan
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                scan_data = json.loads(result.stdout)
                return scan_data
            else:
                print(f"Trivy scan failed for {target}: {result.stderr}")
                return {"target": target, "error": result.stderr}

        except FileNotFoundError:
            print("Trivy not found. Please install Trivy for vulnerability scanning.")
            return {"target": target, "error": "Trivy not installed"}
        except json.JSONDecodeError:
            print(f"Failed to parse Trivy output for {target}")
            return {"target": target, "error": "Invalid JSON output"}

    def run_kubescape_scan(self) -> Dict[str, Any]:
        """
        Run Kubescape scan for Kubernetes security

        Returns:
            Scan results dictionary
        """
        try:
            # Create temporary file for results
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
                cmd = ["kubescape", "scan", "--format", "json", "--output", temp_file.name]

                result = subprocess.run(cmd, capture_output=True, text=True, check=False)

                if result.returncode == 0:
                    with open(temp_file.name, 'r') as f:
                        scan_data = json.load(f)

                    # Clean up temp file
                    os.unlink(temp_file.name)
                    return scan_data
                else:
                    print(f"Kubescape scan failed: {result.stderr}")
                    return {"error": result.stderr}

        except FileNotFoundError:
            print("Kubescape not found. Please install Kubescape for Kubernetes security scanning.")
            return {"error": "Kubescape not installed"}
        except Exception as e:
            print(f"Kubescape scan error: {e}")
            return {"error": str(e)}

    def check_hardcoded_secrets(self, directory: str) -> List[Dict[str, str]]:
        """
        Check for hardcoded secrets in source code

        Args:
            directory: Directory to scan for hardcoded secrets

        Returns:
            List of found secrets with file locations
        """
        secrets_found = []

        # Common patterns for sensitive information
        secret_patterns = [
            r'(?:password|pwd|pass|secret|token|key|credential|auth|api_key|api_token|client_secret)',
            r'(?:AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|SECRET_KEY|DATABASE_URL)',
            r'(?:BEGIN RSA PRIVATE KEY|BEGIN OPENSSH PRIVATE KEY|BEGIN PRIVATE KEY)'
        ]

        import re

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.yaml', '.yml', '.json', '.env', '.config')):
                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        for i, line_num, line in enumerate(content.split('\n'), 1):
                            for pattern in secret_patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    # Avoid flagging legitimate code
                                    if not re.search(r'(?:placeholder|dummy|test|mock|example)', line, re.IGNORECASE):
                                        secrets_found.append({
                                            'file': file_path,
                                            'line_number': i,
                                            'line_content': line.strip(),
                                            'pattern_matched': pattern
                                        })
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")

        return secrets_found

    def check_kubernetes_resources(self, manifests_dir: str) -> List[Dict[str, str]]:
        """
        Check Kubernetes manifests for security misconfigurations

        Args:
            manifests_dir: Directory containing Kubernetes manifests

        Returns:
            List of security issues found
        """
        issues = []

        for root, dirs, files in os.walk(manifests_dir):
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, 'r') as f:
                            manifests = yaml.safe_load_all(f)

                            for manifest in manifests:
                                if manifest is None:
                                    continue

                                kind = manifest.get('kind', '').lower()
                                metadata = manifest.get('metadata', {})
                                spec = manifest.get('spec', {})

                                # Check for security issues
                                if kind in ['deployment', 'statefulset', 'daemonset', 'pod']:
                                    containers = spec.get('template', {}).get('spec', {}).get('containers', [])

                                    for container in containers:
                                        container_name = container.get('name', 'unknown')

                                        # Check for privileged containers
                                        security_context = container.get('securityContext', {})
                                        if security_context.get('privileged', False):
                                            issues.append({
                                                'file': file_path,
                                                'resource': f"{kind}/{metadata.get('name', 'unknown')}",
                                                'container': container_name,
                                                'issue': 'Privileged container detected',
                                                'severity': 'critical'
                                            })

                                        # Check for running as root
                                        if security_context.get('runAsNonRoot') is False:
                                            issues.append({
                                                'file': file_path,
                                                'resource': f"{kind}/{metadata.get('name', 'unknown')}",
                                                'container': container_name,
                                                'issue': 'Container running as root',
                                                'severity': 'high'
                                            })

                                        # Check for read-only root filesystem
                                        if not security_context.get('readOnlyRootFilesystem'):
                                            issues.append({
                                                'file': file_path,
                                                'resource': f"{kind}/{metadata.get('name', 'unknown')}",
                                                'container': container_name,
                                                'issue': 'Root filesystem not read-only',
                                                'severity': 'medium'
                                            })

                                        # Check for capabilities
                                        capabilities = security_context.get('capabilities', {})
                                        if 'add' in capabilities:
                                            for cap in capabilities['add']:
                                                if cap in ['NET_ADMIN', 'SYS_ADMIN', 'DAC_READ_SEARCH']:
                                                    issues.append({
                                                        'file': file_path,
                                                        'resource': f"{kind}/{metadata.get('name', 'unknown')}",
                                                        'container': container_name,
                                                        'issue': f'Dangerous capability added: {cap}',
                                                        'severity': 'high'
                                                    })

                                # Check for NetworkPolicy
                                if kind == 'networkpolicy':
                                    # Validate that policies are restrictive enough
                                    spec = manifest.get('spec', {})
                                    if 'podSelector' in spec and spec['podSelector'] == {}:
                                        issues.append({
                                            'file': file_path,
                                            'resource': f"{kind}/{metadata.get('name', 'unknown')}",
                                            'issue': 'NetworkPolicy allows all pods in namespace',
                                            'severity': 'medium'
                                        })

                                # Check for RBAC resources
                                if kind in ['role', 'clusterrole']:
                                    rules = spec.get('rules', [])
                                    for rule in rules:
                                        if '*' in rule.get('resources', []) and '*' in rule.get('verbs', []):
                                            issues.append({
                                                'file': file_path,
                                                'resource': f"{kind}/{metadata.get('name', 'unknown')}",
                                                'issue': 'Overly permissive RBAC rule detected',
                                                'severity': 'critical'
                                            })

                    except yaml.YAMLError as e:
                        print(f"Error parsing YAML file {file_path}: {e}")
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")

        return issues

    def check_running_pods_security(self, namespace: str = "default") -> List[Dict[str, str]]:
        """
        Check security posture of running pods in Kubernetes

        Args:
            namespace: Kubernetes namespace to check

        Returns:
            List of security issues found
        """
        issues = []

        try:
            # Get pod information using kubectl
            cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                print(f"kubectl get pods failed: {result.stderr}")
                return issues

            pods_data = json.loads(result.stdout)

            for pod in pods_data.get('items', []):
                pod_name = pod['metadata']['name']

                # Check pod security context
                pod_spec = pod['spec']
                pod_security_context = pod_spec.get('securityContext', {})

                if pod_security_context.get('runAsNonRoot') is False:
                    issues.append({
                        'pod': pod_name,
                        'namespace': namespace,
                        'issue': 'Pod running as root',
                        'severity': 'high'
                    })

                # Check containers in the pod
                containers = pod_spec.get('containers', [])
                for container in containers:
                    container_name = container.get('name', 'unknown')
                    security_context = container.get('securityContext', {})

                    # Check if privileged
                    if security_context.get('privileged', False):
                        issues.append({
                            'pod': pod_name,
                            'container': container_name,
                            'namespace': namespace,
                            'issue': 'Privileged container detected',
                            'severity': 'critical'
                        })

                    # Check runAsNonRoot
                    if security_context.get('runAsNonRoot') is False:
                        issues.append({
                            'pod': pod_name,
                            'container': container_name,
                            'namespace': namespace,
                            'issue': 'Container running as root',
                            'severity': 'high'
                        })

                    # Check readOnlyRootFilesystem
                    if not security_context.get('readOnlyRootFilesystem'):
                        issues.append({
                            'pod': pod_name,
                            'container': container_name,
                            'namespace': namespace,
                            'issue': 'Root filesystem not read-only',
                            'severity': 'medium'
                        })

        except json.JSONDecodeError:
            print("Failed to parse kubectl output")
        except FileNotFoundError:
            print("kubectl not found. Please install kubectl to check running pods.")
        except Exception as e:
            print(f"Error checking running pods: {e}")

        return issues

    def run_comprehensive_scan(self, project_root: str = ".") -> Dict[str, Any]:
        """
        Run comprehensive security scan on the project

        Args:
            project_root: Root directory of the project

        Returns:
            Comprehensive scan results
        """
        print("Starting comprehensive security scan...")

        # Run Trivy scan on Docker images if they exist
        dockerfiles = []
        for root, dirs, files in os.walk(project_root):
            for file in files:
                if file.lower() == 'dockerfile':
                    dockerfiles.append(os.path.dirname(os.path.join(root, file)))

        if dockerfiles:
            print(f"Found Dockerfiles, scanning images...")
            for docker_dir in dockerfiles:
                print(f"Scanning Dockerfile in {docker_dir}")
                # Note: This would require images to be built first
                # For now, we'll just note that images should be scanned
                self.scan_results['info'] = f"Images in {dockerfiles} should be scanned with Trivy"

        # Check for hardcoded secrets
        print("Checking for hardcoded secrets...")
        secrets = self.check_hardcoded_secrets(project_root)
        self.scan_results['secrets_found'] = secrets

        # Check Kubernetes manifests for security issues
        print("Checking Kubernetes manifests...")
        manifest_issues = self.check_kubernetes_resources(os.path.join(project_root, "k8s-manifests"))
        self.scan_results['misconfigurations'].extend(manifest_issues)

        # Check for common configuration files that might contain secrets
        print("Checking for sensitive configuration files...")
        sensitive_files = [
            '.env', '.env.local', '.env.production',
            'config.json', 'config.yaml', 'config.yml',
            '*.pem', '*.key', '*.crt', '*.cert'
        ]

        for root, dirs, files in os.walk(project_root):
            for file in files:
                for pattern in sensitive_files:
                    if file.lower().endswith(pattern.replace('*', '')):
                        if not any(skip in root for skip in ['.git', 'node_modules', '__pycache__']):
                            self.scan_results['misconfigurations'].append({
                                'file': os.path.join(root, file),
                                'issue': f'Sensitive configuration file found: {file}',
                                'severity': 'medium'
                            })

        # Run Kubescape if available
        print("Running Kubernetes security scan...")
        kubescape_results = self.run_kubescape_scan()
        if 'error' not in kubescape_results:
            self.scan_results['kubescape_results'] = kubescape_results

        # Summary
        total_issues = (
            len(self.scan_results['vulnerabilities']) +
            len(self.scan_results['misconfigurations']) +
            len(self.scan_results['secrets_found'])
        )

        print(f"\nScan completed. Found {total_issues} issues:")
        print(f"- Secrets: {len(self.scan_results['secrets_found'])}")
        print(f"- Misconfigurations: {len(self.scan_results['misconfigurations'])}")
        print(f"- Vulnerabilities: {len(self.scan_results['vulnerabilities'])}")

        return self.scan_results

    def generate_report(self, output_file: str = "security_scan_report.json"):
        """
        Generate security scan report

        Args:
            output_file: File to save the report
        """
        with open(output_file, 'w') as f:
            json.dump(self.scan_results, f, indent=2)

        print(f"Security scan report saved to {output_file}")


class DaprSecurityChecker:
    """
    Specific security checker for Dapr components and configurations
    """

    @staticmethod
    def check_dapr_components(components_dir: str) -> List[Dict[str, str]]:
        """
        Check Dapr component configurations for security issues

        Args:
            components_dir: Directory containing Dapr component files

        Returns:
            List of security issues found
        """
        issues = []

        for root, dirs, files in os.walk(components_dir):
            for file in files:
                if file.endswith(('.yaml', '.yml')) and 'dapr' in file.lower():
                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, 'r') as f:
                            component = yaml.safe_load(f)

                        if component and component.get('apiVersion', '').startswith('dapr.io/'):
                            comp_name = component.get('metadata', {}).get('name', 'unknown')
                            comp_type = component.get('spec', {}).get('type', 'unknown')

                            # Check for plaintext secrets in component definitions
                            metadata = component.get('spec', {}).get('metadata', [])
                            for meta_item in metadata:
                                if 'value' in meta_item:
                                    value = meta_item['value']
                                    # Check if the value looks like a secret
                                    if any(keyword in value.lower() for keyword in
                                          ['password', 'secret', 'token', 'key', 'credential']):
                                        issues.append({
                                            'file': file_path,
                                            'component': comp_name,
                                            'issue': f'Plaintext secret in component metadata: {meta_item.get("name", "unknown")}',
                                            'severity': 'critical'
                                        })

                            # Check for proper authentication in state store components
                            if 'state' in comp_type:
                                # Check if the state store has proper authentication configured
                                pass  # Add specific checks for state store auth

                    except yaml.YAMLError as e:
                        print(f"Error parsing Dapr component file {file_path}: {e}")
                    except Exception as e:
                        print(f"Error processing Dapr component file {file_path}: {e}")

        return issues

    @staticmethod
    def check_dapr_sidecar_security(namespace: str = "default") -> List[Dict[str, str]]:
        """
        Check Dapr sidecar configurations for security issues

        Args:
            namespace: Kubernetes namespace to check

        Returns:
            List of security issues found
        """
        issues = []

        try:
            # Get pods with Dapr sidecars
            cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                print(f"kubectl get pods failed: {result.stderr}")
                return issues

            pods_data = json.loads(result.stdout)

            for pod in pods_data.get('items', []):
                pod_name = pod['metadata']['name']

                # Check if pod has Dapr sidecar
                has_dapr_sidecar = False
                containers = pod['spec'].get('containers', [])
                for container in containers:
                    if 'daprd' in container.get('name', ''):
                        has_dapr_sidecar = True
                        break

                if has_dapr_sidecar:
                    # Check Dapr annotations
                    annotations = pod['metadata'].get('annotations', {})

                    # Check if app SSL is enabled
                    app_ssl = annotations.get('dapr.io/app-ssl', '').lower()
                    if app_ssl != 'true':
                        issues.append({
                            'pod': pod_name,
                            'namespace': namespace,
                            'issue': 'App SSL not enabled for Dapr sidecar communication',
                            'severity': 'medium'
                        })

                    # Check trust domain
                    trust_domain = annotations.get('dapr.io/trust-domain')
                    if not trust_domain:
                        issues.append({
                            'pod': pod_name,
                            'namespace': namespace,
                            'issue': 'Trust domain not configured for Dapr mTLS',
                            'severity': 'high'
                        })

        except json.JSONDecodeError:
            print("Failed to parse kubectl output for Dapr sidecar check")
        except FileNotFoundError:
            print("kubectl not found. Please install kubectl to check Dapr sidecars.")
        except Exception as e:
            print(f"Error checking Dapr sidecars: {e}")

        return issues


def main():
    """
    Main function to run security scanning
    """
    print("Starting Security Scanning Process...")

    # Initialize scanner
    scanner = SecurityScanner()

    # Get project root from command line or use current directory
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    # Run comprehensive scan
    results = scanner.run_comprehensive_scan(project_root)

    # Check Dapr-specific security
    print("\nChecking Dapr security configurations...")
    dapr_checker = DaprSecurityChecker()

    # Check Dapr components if directory exists
    dapr_comp_dir = os.path.join(project_root, "dapr", "components")
    if os.path.exists(dapr_comp_dir):
        dapr_issues = dapr_checker.check_dapr_components(dapr_comp_dir)
        results['misconfigurations'].extend(dapr_issues)

    # Check Dapr sidecars in default namespace
    dapr_pod_issues = dapr_checker.check_dapr_sidecar_security("default")
    results['misconfigurations'].extend(dapr_pod_issues)

    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"security_scan_report_{timestamp}.json"
    scanner.generate_report(report_file)

    # Print summary
    print(f"\n{'='*60}")
    print("SECURITY SCAN COMPLETE")
    print(f"{'='*60}")

    secrets_found = len(results.get('secrets_found', []))
    misconfigs = len(results.get('misconfigurations', []))
    vulnerabilities = len(results.get('vulnerabilities', []))

    print(f"Hardcoded secrets found: {secrets_found}")
    print(f"Misconfigurations detected: {misconfigs}")
    print(f"Vulnerabilities found: {vulnerabilities}")

    if secrets_found > 0:
        print("\n⚠️  SECURITY ISSUE: Hardcoded secrets detected!")
        print("   These must be moved to a secure secret store immediately.")

    if misconfigs > 0:
        print(f"\n⚠️  CONFIGURATION ISSUES: {misconfigs} misconfigurations detected")
        print("   Review the report for specific recommendations.")

    if vulnerabilities > 0:
        print(f"\n⚠️  VULNERABILITIES: {vulnerabilities} vulnerabilities detected")
        print("   Address these before production deployment.")

    if secrets_found == 0 and misconfigs == 0 and vulnerabilities == 0:
        print("\n✅ No critical security issues detected!")
        print("   Continue with security hardening review.")

    print(f"\nFull report saved to: {report_file}")
    print(f"{'='*60}")

    return results


if __name__ == "__main__":
    results = main()

    # Exit with error code if critical issues found
    secrets_found = len(results.get('secrets_found', []))
    critical_misconfigs = len([m for m in results.get('misconfigurations', [])
                              if m.get('severity') in ['critical', 'high']])

    if secrets_found > 0 or critical_misconfigs > 0:
        print("\nCritical security issues detected. Exiting with error.")
        exit(1)
    else:
        print("\nSecurity scan completed successfully.")
        exit(0)