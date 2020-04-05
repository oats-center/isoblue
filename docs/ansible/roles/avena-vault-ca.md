# Ansible role: avena-vault-ca

## Description

This role configures `sshd` for host and user CA authentication. It uses
[Hashicorp Vault](https://www.hashicorp.com/products/vault/) as the CA.

Benefits:

1. CA controlled, fleet wide authorization
2. Easy host verification (ISOBlue verification).

## Assumptions

1. Access to a working `vault` server configured as SSH CA.

## Variables

### Required

- `avena_ca_vault_client_pubkey` - The Vault path for the client
  (user) CA public key. For example: `avena-client-signer/config/ca`, where
  `avena-client-signer` is the mount point of the `ssh` secrets engine for
  client (user) keys.

- `avena_ca_vault_host_signer` - The Vault path for signing (creating a
  certificate) host key. For example, `avena-host-signer/sign/deploy`, where
  `avena-host-signer` is the mount point of the `ssh` secrets engine for the
  host keys and `deploy` is the role to use when signing.
