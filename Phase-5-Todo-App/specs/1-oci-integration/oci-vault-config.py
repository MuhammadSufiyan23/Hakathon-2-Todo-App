"""
OCI Vault configuration for production secrets
This module provides configuration and utilities for OCI Vault integration
"""

import oci
import json
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class SecretType(Enum):
    """Enumeration of different secret types"""
    DATABASE_CREDENTIALS = "database_credentials"
    API_KEYS = "api_keys"
    ENCRYPTION_KEYS = "encryption_keys"
    SERVICE_ACCOUNTS = "service_accounts"


@dataclass
class SecretMetadata:
    """Metadata for secrets stored in OCI Vault"""
    name: str
    description: str
    secret_type: SecretType
    rotation_period_days: int = 90
    created_by: str = "system"
    tags: Optional[Dict[str, str]] = None


class OCIVaultManager:
    """
    Manager for OCI Vault operations
    Handles secret storage, retrieval, and lifecycle management
    """

    def __init__(self, config_file_path: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize OCI Vault manager

        Args:
            config_file_path: Path to OCI config file (~/.oci/config)
            config_dict: Direct configuration dictionary
        """
        if config_dict:
            self.config = config_dict
        else:
            self.config = oci.config.from_file(config_file_path)

        self.vault_client = oci.vault.VaultsClient(self.config)
        self.secret_client = oci.secrets.SecretsClient(self.config)
        self.encryption_client = oci.key_management.KmsVaultClient(self.config)

    def create_vault(self, compartment_id: str, vault_display_name: str,
                     vault_description: str = "") -> str:
        """
        Create a new vault in OCI

        Args:
            compartment_id: OCI compartment ID
            vault_display_name: Display name for the vault
            vault_description: Description for the vault

        Returns:
            Vault ID
        """
        create_vault_details = oci.vault.models.CreateVaultDetails(
            compartment_id=compartment_id,
            display_name=vault_display_name,
            description=vault_description,
            vault_type="SOFTWARE_VAULT"  # Using software vault for cost efficiency
        )

        response = self.vault_client.create_vault(create_vault_details)
        vault_id = response.data.id

        # Wait for vault to be active
        waiter = oci.wait_until(
            self.vault_client,
            self.vault_client.get_vault(vault_id),
            'lifecycle_state',
            'ACTIVE',
            max_wait_seconds=300
        )

        print(f"Created vault: {vault_id}")
        return vault_id

    def create_secret(self, vault_id: str, secret_metadata: SecretMetadata,
                      secret_content: str, compartment_id: str) -> str:
        """
        Create a new secret in OCI Vault

        Args:
            vault_id: Target vault ID
            secret_metadata: Metadata for the secret
            secret_content: Actual secret content (should be base64 encoded)
            compartment_id: OCI compartment ID

        Returns:
            Secret ID
        """
        # Encode secret content
        import base64
        encoded_content = base64.b64encode(secret_content.encode()).decode()

        create_secret_details = oci.vault.models.CreateSecretDetails(
            compartment_id=compartment_id,
            display_name=secret_metadata.name,
            description=secret_metadata.description,
            vault_id=vault_id,
            secret_content=oci.vault.models.Base64SecretContentDetails(
                content=encoded_content
            ),
            key_id=None  # Use default key
        )

        response = self.secret_client.create_secret(create_secret_details)
        secret_id = response.data.id

        print(f"Created secret: {secret_metadata.name} with ID: {secret_id}")
        return secret_id

    def get_secret(self, secret_id: str) -> str:
        """
        Retrieve a secret from OCI Vault

        Args:
            secret_id: ID of the secret to retrieve

        Returns:
            Decoded secret content
        """
        response = self.secret_client.get_secret_bundle(secret_id)
        secret_bundle = response.data

        # Decode the secret content
        import base64
        decoded_content = base64.b64decode(secret_bundle.secret_bundle_content.content).decode()

        return decoded_content

    def schedule_secret_deletion(self, secret_id: str, deletion_time: str = None):
        """
        Schedule a secret for deletion

        Args:
            secret_id: ID of the secret to delete
            deletion_time: ISO 8601 formatted time for deletion (default: 30 days from now)
        """
        if not deletion_time:
            from datetime import datetime, timedelta
            deletion_time = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')

        schedule_secret_deletion_details = oci.vault.models.ScheduleSecretDeletionDetails(
            time_of_deletion=deletion_time
        )

        self.secret_client.schedule_secret_deletion(
            secret_id,
            schedule_secret_deletion_details
        )

        print(f"Scheduled secret {secret_id} for deletion on {deletion_time}")


class DaprOCISecretStore:
    """
    Dapr component configuration for OCI Vault integration
    """

    @staticmethod
    def generate_dapr_component_config(compartment_id: str, vault_id: str,
                                    tenancy_id: str, user_id: str,
                                    signing_key_fingerprint: str,
                                    region: str = "us-sanjose-1") -> Dict[str, Any]:
        """
        Generate Dapr component configuration for OCI Vault

        Args:
            compartment_id: OCI compartment ID
            vault_id: OCI Vault ID
            tenancy_id: OCI tenancy ID
            user_id: OCI user ID
            signing_key_fingerprint: Fingerprint of the signing key
            region: OCI region

        Returns:
            Dapr component configuration dictionary
        """
        component_config = {
            "apiVersion": "dapr.io/v1alpha1",
            "kind": "Component",
            "metadata": {
                "name": "oci-secret-store"
            },
            "spec": {
                "type": "secretstores.oracle.vault",
                "version": "v1",
                "metadata": [
                    {
                        "name": "compartmentId",
                        "value": compartment_id
                    },
                    {
                        "name": "vaultId",
                        "value": vault_id
                    },
                    {
                        "name": "tenancyId",
                        "value": tenancy_id
                    },
                    {
                        "name": "userId",
                        "value": user_id
                    },
                    {
                        "name": "fingerprint",
                        "value": signing_key_fingerprint
                    },
                    {
                        "name": "region",
                        "value": region
                    },
                    {
                        "name": "privateKey",
                        "value": "{{PLACEHOLDER_FOR_PRIVATE_KEY}}"
                    }
                ]
            }
        }

        return component_config

    @staticmethod
    def save_dapr_component_config(config: Dict[str, Any], filepath: str):
        """
        Save Dapr component configuration to file

        Args:
            config: Dapr component configuration
            filepath: Path to save the configuration file
        """
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"Dapr component configuration saved to {filepath}")


class ProductionSecretsManager:
    """
    Manager for production secrets following security best practices
    """

    def __init__(self, oci_vault_manager: OCIVaultManager):
        self.vault_manager = oci_vault_manager

    def store_database_credentials(self, compartment_id: str, vault_id: str,
                                db_host: str, db_username: str, db_password: str) -> Dict[str, str]:
        """
        Store database credentials in OCI Vault

        Args:
            compartment_id: OCI compartment ID
            vault_id: OCI Vault ID
            db_host: Database host
            db_username: Database username
            db_password: Database password

        Returns:
            Dictionary mapping secret names to their IDs
        """
        secrets_mapping = {}

        # Store database host
        host_metadata = SecretMetadata(
            name="db-host",
            description="Database host address",
            secret_type=SecretType.DATABASE_CREDENTIALS
        )
        secrets_mapping["db_host_id"] = self.vault_manager.create_secret(
            vault_id, host_metadata, db_host, compartment_id
        )

        # Store database username
        username_metadata = SecretMetadata(
            name="db-username",
            description="Database username",
            secret_type=SecretType.DATABASE_CREDENTIALS
        )
        secrets_mapping["db_username_id"] = self.vault_manager.create_secret(
            vault_id, username_metadata, db_username, compartment_id
        )

        # Store database password
        password_metadata = SecretMetadata(
            name="db-password",
            description="Database password",
            secret_type=SecretType.DATABASE_CREDENTIALS
        )
        secrets_mapping["db_password_id"] = self.vault_manager.create_secret(
            vault_id, password_metadata, db_password, compartment_id
        )

        return secrets_mapping

    def store_api_keys(self, compartment_id: str, vault_id: str,
                      api_keys: Dict[str, str]) -> Dict[str, str]:
        """
        Store various API keys in OCI Vault

        Args:
            compartment_id: OCI compartment ID
            vault_id: OCI Vault ID
            api_keys: Dictionary of API key names to their values

        Returns:
            Dictionary mapping API key names to their secret IDs
        """
        secrets_mapping = {}

        for key_name, key_value in api_keys.items():
            metadata = SecretMetadata(
                name=f"api-key-{key_name.lower()}",
                description=f"API key for {key_name}",
                secret_type=SecretType.API_KEYS
            )
            secret_id = self.vault_manager.create_secret(
                vault_id, metadata, key_value, compartment_id
            )
            secrets_mapping[f"{key_name}_id"] = secret_id

        return secrets_mapping

    def create_encryption_keys(self, compartment_id: str, vault_id: str,
                             key_names: list) -> Dict[str, str]:
        """
        Create encryption keys in OCI Vault

        Args:
            compartment_id: OCI compartment ID
            vault_id: OCI Vault ID
            key_names: List of key names to create

        Returns:
            Dictionary mapping key names to their IDs
        """
        secrets_mapping = {}

        for key_name in key_names:
            # For simplicity, we'll store randomly generated keys
            import secrets
            import string
            key_value = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

            metadata = SecretMetadata(
                name=f"encryption-key-{key_name.lower()}",
                description=f"Encryption key for {key_name}",
                secret_type=SecretType.ENCRYPTION_KEYS
            )
            secret_id = self.vault_manager.create_secret(
                vault_id, metadata, key_value, compartment_id
            )
            secrets_mapping[f"{key_name}_id"] = secret_id

        return secrets_mapping


# Example usage
if __name__ == "__main__":
    # Example of how to use the OCI Vault manager
    print("OCI Vault Configuration Example")

    # This would normally be initialized with actual OCI credentials
    # config = {
    #     "user": "ocid1.user.oc1..aaaaaaa...",
    #     "key_file": "~/.oci/oci_api_key.pem",
    #     "fingerprint": "xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx",
    #     "tenancy": "ocid1.tenancy.oc1..aaaaaaa...",
    #     "region": "us-sanjose-1"
    # }
    #
    # vault_manager = OCIVaultManager(config_dict=config)
    #
    # # Create a vault
    # vault_id = vault_manager.create_vault(
    #     compartment_id="ocid1.compartment.oc1..aaaaaaa...",
    #     vault_display_name="todo-app-vault",
    #     vault_description="Vault for Todo App production secrets"
    # )
    #
    # # Create a secrets manager
    # secrets_manager = ProductionSecretsManager(vault_manager)
    #
    # # Store database credentials
    # db_secrets = secrets_manager.store_database_credentials(
    #     compartment_id="ocid1.compartment.oc1..aaaaaaa...",
    #     vault_id=vault_id,
    #     db_host="prod-db.todo-app.oracledb.com",
    #     db_username="todo_app_user",
    #     db_password="secure_db_password_here"
    # )
    #
    # # Store API keys
    # api_keys = {
    #     "notification_service": "notification_api_key_here",
    #     "payment_gateway": "payment_api_key_here"
    # }
    # api_secrets = secrets_manager.store_api_keys(
    #     compartment_id="ocid1.compartment.oc1..aaaaaaa...",
    #     vault_id=vault_id,
    #     api_keys=api_keys
    # )
    #
    # # Generate Dapr component configuration
    # dapr_config = DaprOCISecretStore.generate_dapr_component_config(
    #     compartment_id="ocid1.compartment.oc1..aaaaaaa...",
    #     vault_id=vault_id,
    #     tenancy_id="ocid1.tenancy.oc1..aaaaaaa...",
    #     user_id="ocid1.user.oc1..aaaaaaa...",
    #     signing_key_fingerprint="xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx"
    # )
    #
    # DaprOCISecretStore.save_dapr_component_config(
    #     dapr_config,
    #     "dapr-oci-secret-store.yaml"
    # )

    print("OCI Vault configuration classes created successfully!")
    print("Note: Actual vault operations require valid OCI credentials.")