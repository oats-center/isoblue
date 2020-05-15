# Ansible role: ca

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

- `avena_ca_get_client_pubkey` - The **local** command to call for fetching the
  CA's client public key. The command output should be nothing but the public
  key.

  - For example, the command for [Hashicorp
    Vault](https://www.hashicorp.com/products/vault) with the `ssh` module
    mounted at `avena-client-signer` is:

    `vault read --field=public_key avena-client-signer/config/ca`

- `avena_ca_sign_host_key` - The **local** command to call for CA signing the
  Avena host's public key (generate a certificate). The command output should be
  nothing but the certificate. The command is run such that the public key to be
  signed is stored in `item.pubkey`.

  - For example, the command for [Hashicorp
    Vault](https://www.hashicorp.com/products/vault) using role `deploy` with
    the `ssh` module mounted at `avena-host-signer` is

    `vault write -field=signed_key avena-host-signer/sign/deploy public_key="{{ item.pubkey }}" cert_type=host`
