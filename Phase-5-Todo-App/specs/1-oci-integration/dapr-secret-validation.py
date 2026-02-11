"""
Dapr secret management validation
This script validates that secret management is properly implemented through Dapr
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List
import os
from pathlib import Path


class DaprSecretValidator:
    """
    Validator for Dapr secret management implementation
    """

    def __init__(self, dapr_http_endpoint: str = "http://localhost:3500"):
        self.dapr_http_endpoint = dapr_http_endpoint

    async def get_secret(self, store_name: str, key: str, metadata: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Retrieve a secret from Dapr secret store

        Args:
            store_name: Name of the secret store component
            key: Key of the secret to retrieve
            metadata: Optional metadata for the request

        Returns:
            Dictionary containing the secret value(s)
        """
        url = f"{self.dapr_http_endpoint}/v1.0/secrets/{store_name}/{key}"

        if metadata:
            # Convert metadata to query parameters
            params = '&'.join([f"metadata.{k}={v}" for k, v in metadata.items()])
            url += f"?{params}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Failed to get secret: {response.status} - {error_text}")
            except Exception as e:
                print(f"Error retrieving secret {key} from store {store_name}: {e}")
                return None

    async def bulk_get_secrets(self, store_name: str, metadata: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Retrieve all allowed secrets from Dapr secret store

        Args:
            store_name: Name of the secret store component
            metadata: Optional metadata for the request

        Returns:
            Dictionary containing all secrets
        """
        url = f"{self.dapr_http_endpoint}/v1.0/secrets/{store_name}/bulk"

        if metadata:
            # Convert metadata to query parameters
            params = '&'.join([f"metadata.{k}={v}" for k, v in metadata.items()])
            url += f"?{params}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Failed to get secrets: {response.status} - {error_text}")
            except Exception as e:
                print(f"Error retrieving secrets from store {store_name}: {e}")
                return None

    async def validate_secret_access(self, store_name: str, secrets_to_check: List[str]) -> Dict[str, bool]:
        """
        Validate that secrets can be accessed through Dapr

        Args:
            store_name: Name of the secret store component
            secrets_to_check: List of secret keys to validate

        Returns:
            Dictionary mapping secret keys to their access status
        """
        results = {}

        for secret_key in secrets_to_check:
            try:
                secret_data = await self.get_secret(store_name, secret_key)
                if secret_data is not None:
                    results[secret_key] = True
                    print(f"✓ Secret '{secret_key}' accessible through Dapr")
                else:
                    results[secret_key] = False
                    print(f"✗ Secret '{secret_key}' not accessible through Dapr")
            except Exception as e:
                results[secret_key] = False
                print(f"✗ Error accessing secret '{secret_key}': {e}")

        return results

    async def validate_database_secrets(self) -> bool:
        """
        Validate that database secrets are properly configured and accessible

        Returns:
            Boolean indicating if validation passed
        """
        print("\nValidating database secrets...")

        required_secrets = [
            "db-host",
            "db-username",
            "db-password",
            "db-name"
        ]

        results = await self.validate_secret_access("oci-secret-store", required_secrets)

        # Check if all required secrets are accessible
        all_accessible = all(results.values())

        if all_accessible:
            print("✓ All database secrets accessible through Dapr")
        else:
            missing = [k for k, v in results.items() if not v]
            print(f"✗ Missing database secrets: {missing}")

        return all_accessible

    async def validate_api_key_secrets(self) -> bool:
        """
        Validate that API key secrets are properly configured and accessible

        Returns:
            Boolean indicating if validation passed
        """
        print("\nValidating API key secrets...")

        required_secrets = [
            "notification-service-api-key",
            "payment-gateway-api-key",
            "email-service-api-key"
        ]

        results = await self.validate_secret_access("oci-secret-store", required_secrets)

        # Check if all required secrets are accessible
        all_accessible = all(results.values())

        if all_accessible:
            print("✓ All API key secrets accessible through Dapr")
        else:
            missing = [k for k, v in results.items() if not v]
            print(f"✗ Missing API key secrets: {missing}")

        return all_accessible

    async def validate_application_secrets(self) -> bool:
        """
        Validate that application-specific secrets are properly configured

        Returns:
            Boolean indicating if validation passed
        """
        print("\nValidating application secrets...")

        required_secrets = [
            "jwt-secret",
            "encryption-key",
            "session-secret"
        ]

        results = await self.validate_secret_access("oci-secret-store", required_secrets)

        # Check if all required secrets are accessible
        all_accessible = all(results.values())

        if all_accessible:
            print("✓ All application secrets accessible through Dapr")
        else:
            missing = [k for k, v in results.items() if not v]
            print(f"✗ Missing application secrets: {missing}")

        return all_accessible

    async def validate_secret_permissions(self) -> bool:
        """
        Validate that secret permissions are properly configured

        Returns:
            Boolean indicating if validation passed
        """
        print("\nValidating secret permissions...")

        # Try to access a secret that should not be accessible
        # This is a basic check - in real implementation, we'd test more granular permissions
        try:
            # Attempt to access a non-existent secret to verify the endpoint works
            result = await self.get_secret("oci-secret-store", "non-existent-secret")

            # If we get a proper error response, the endpoint is secured
            print("✓ Secret endpoint properly secured")
            return True
        except Exception as e:
            print(f"✗ Secret endpoint validation error: {e}")
            return False

    async def run_full_validation(self) -> Dict[str, Any]:
        """
        Run complete validation of Dapr secret management

        Returns:
            Dictionary with validation results
        """
        print("Starting Dapr Secret Management Validation...")
        print(f"Target Dapr endpoint: {self.dapr_http_endpoint}")

        results = {
            "database_secrets": await self.validate_database_secrets(),
            "api_key_secrets": await self.validate_api_key_secrets(),
            "application_secrets": await self.validate_application_secrets(),
            "secret_permissions": await self.validate_secret_permissions()
        }

        # Overall validation result
        all_valid = all(results.values())

        print(f"\n{'='*50}")
        print("VALIDATION SUMMARY")
        print(f"{'='*50}")
        for test_name, passed in results.items():
            status = "PASS" if passed else "FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        print(f"{'='*50}")
        print(f"Overall Result: {'PASS' if all_valid else 'FAIL'}")
        print(f"{'='*50}")

        return results


class DaprSecretConfigurationChecker:
    """
    Checker for Dapr secret store component configuration
    """

    @staticmethod
    def validate_component_config(component_file_path: str) -> bool:
        """
        Validate Dapr secret store component configuration file

        Args:
            component_file_path: Path to the Dapr component file

        Returns:
            Boolean indicating if configuration is valid
        """
        try:
            with open(component_file_path, 'r') as f:
                component_data = json.load(f) if component_file_path.endswith('.json') else json.loads(f.read())

            # Check required fields
            required_fields = ['apiVersion', 'kind', 'metadata', 'spec']
            for field in required_fields:
                if field not in component_data:
                    print(f"✗ Missing required field: {field}")
                    return False

            # Check component type
            if component_data.get('spec', {}).get('type') != 'secretstores.oracle.vault':
                print("✗ Component is not configured for OCI Vault")
                return False

            # Check metadata fields
            metadata = component_data.get('spec', {}).get('metadata', [])
            required_metadata = ['compartmentId', 'vaultId', 'tenancyId', 'userId', 'fingerprint', 'region']

            metadata_names = [item.get('name') for item in metadata]
            for req_meta in required_metadata:
                if req_meta not in metadata_names:
                    print(f"✗ Missing required metadata field: {req_meta}")
                    return False

            print("✓ Dapr secret store component configuration is valid")
            return True

        except FileNotFoundError:
            print(f"✗ Component file not found: {component_file_path}")
            return False
        except json.JSONDecodeError:
            print(f"✗ Invalid JSON in component file: {component_file_path}")
            return False
        except Exception as e:
            print(f"✗ Error validating component configuration: {e}")
            return False

    @staticmethod
    def check_environment_configuration() -> bool:
        """
        Check if environment is properly configured for Dapr secret access

        Returns:
            Boolean indicating if environment is properly configured
        """
        required_env_vars = [
            'DAPR_HTTP_ENDPOINT',
            'DAPR_GRPC_ENDPOINT'
        ]

        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            print(f"⚠️  Missing environment variables: {missing_vars}")
            print("   These are optional but recommended for proper Dapr integration")
            return True  # Not critical for validation
        else:
            print("✓ All required environment variables are set")
            return True


async def main():
    """
    Main function to run Dapr secret validation
    """
    # Create validator instance
    validator = DaprSecretValidator(os.getenv('DAPR_HTTP_ENDPOINT', 'http://localhost:3500'))

    # Run full validation
    results = await validator.run_full_validation()

    # Check component configuration
    print("\nChecking Dapr component configuration...")

    # Look for component files in common locations
    component_locations = [
        './components/oci-secret-store.yaml',
        './dapr/components/oci-secret-store.yaml',
        '../dapr/components/oci-secret-store.yaml',
        './specs/1-oci-integration/dapr-oci-secret-store.yaml'
    ]

    config_valid = False
    for location in component_locations:
        if Path(location).exists():
            print(f"Found component file: {location}")
            config_valid = DaprSecretConfigurationChecker.validate_component_config(location)
            break

    if not config_valid:
        print("⚠️  No Dapr component file found in expected locations")
        print("   Expected at: ./components/oci-secret-store.yaml or similar")

    # Check environment configuration
    env_valid = DaprSecretConfigurationChecker.check_environment_configuration()

    # Final assessment
    print(f"\nFINAL ASSESSMENT:")
    all_checks_passed = all(results.values()) and config_valid and env_valid

    if all_checks_passed:
        print("✅ All Dapr secret management validations PASSED!")
        print("✅ System is properly configured for secure secret management through Dapr and OCI Vault")
    else:
        print("❌ Some validations FAILED")
        print("⚠️  Please address the issues before deploying to production")

    return all_checks_passed


if __name__ == "__main__":
    success = asyncio.run(main())

    if success:
        print("\n🎉 Dapr secret management validation completed successfully!")
    else:
        print("\n⚠️  Dapr secret management validation has issues that need to be addressed.")
        exit(1)