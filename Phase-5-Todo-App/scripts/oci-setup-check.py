#!/usr/bin/env python3
"""
Simple OCI setup checker for the Todo App project
This script verifies OCI configuration and provides basic OCI functionality
without requiring the full OCI CLI installation.
"""

import os
import sys
import json
from pathlib import Path


def check_oci_config_exists():
    """Check if OCI configuration files exist in the project"""
    config_paths = [
        "specs/1-oci-integration/oci-config.json",
        "specs/1-oci-integration/oci-vault-config.py",
        "../specs/1-oci-integration/oci-config.json",
        "../specs/1-oci-integration/oci-vault-config.py"
    ]
    
    found_configs = []
    for config_path in config_paths:
        if os.path.exists(config_path):
            found_configs.append(config_path)
    
    return found_configs


def validate_oci_config(config_path):
    """Validate the OCI configuration file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_fields = ['compartmentId', 'region']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            print(f"Warning: Missing required fields in {config_path}: {missing_fields}")
            return False
        
        print(f"[OK] Validated OCI configuration in {config_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error validating {config_path}: {str(e)}")
        return False


def check_python_oci_sdk():
    """Check if OCI Python SDK is available"""
    try:
        import oci
        print(f"[OK] OCI Python SDK available, version: {oci.__version__}")
        return True
    except ImportError:
        print("[ERROR] OCI Python SDK not installed")
        print("  To install: pip install oci")
        return False


def show_oci_integration_info():
    """Show information about OCI integration in the project"""
    print("OCI Integration Information for Todo App Project:")
    print("="*50)
    
    # Check for existing configurations
    configs = check_oci_config_exists()
    if configs:
        print(f"Found {len(configs)} OCI configuration file(s):")
        for config in configs:
            print(f"  - {config}")
            
        # Validate the main config
        main_config = next((c for c in configs if "oci-config.json" in c), None)
        if main_config:
            validate_oci_config(main_config)
    else:
        print("No OCI configuration files found in the project")
    
    print()
    
    # Check for Python SDK
    sdk_available = check_python_oci_sdk()
    
    print()
    print("OCI Integration Status:")
    print("-" * 25)
    print(f"Configuration files: {'[OK]' if configs else '[MISSING]'}")
    print(f"Python SDK: {'[OK]' if sdk_available else '[MISSING]'}")

    if configs and sdk_available:
        print("\n[SUCCESS] OCI integration appears to be properly configured!")
        print("  You can proceed with OCI deployment using the specs in specs/1-oci-integration/")
    else:
        print("\n[WARNING] OCI integration requires setup:")
        if not configs:
            print("  - Create OCI configuration files")
        if not sdk_available:
            print("  - Install OCI Python SDK: pip install oci")


def main():
    """Main function to run the OCI setup check"""
    print("Todo App - OCI Setup Checker")
    print("="*30)
    print()
    
    show_oci_integration_info()
    
    print()
    print("Additional OCI Resources:")
    print("-" * 25)
    print("For full OCI CLI installation on Windows:")
    print("  1. Visit: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm")
    print("  2. Download the Windows installer")
    print("  3. Or use: pip install oci-cli (may require long path support)")
    print()
    print("For OCI authentication:")
    print("  1. Create API key pair in OCI Console")
    print("  2. Configure ~/.oci/config file")
    print("  3. Place private key in ~/.oci/oci_api_key.pem")


if __name__ == "__main__":
    main()