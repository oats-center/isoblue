# Ansible role: wireguard

## Description

This role will establish a Wireguard VPN connection between an Avena node and
Wireguard bounce server.

TODO: Route all traffic over the Wireguard interface

Benefits:

1. Simple, yet secure connection -- Its hard to know what is between ISOBlue and
   your backend.
2. Cryptography routed -- roaming between primary IPs / interfaces is seamless.
3. NAT breaker -- Using Wireguard keepalives, Avena node are always accessible
   by any other node within the same Wireguard VPN, even when behind a private
   NAT.

## Assumptions

1. Debian Buster (or newer) OR an `apt` based distribution with a modern
   `wireguard` package available.
2. The nodes `ansible_host` value is set to the desired Wireguard VPN IP.

## Variables

### Required

- `avena_wg_endpoint` - The Wireguard bounce server.
- `avena_wg_pubkey` - The public key of Wireguard bounce server.
- `avena_wg_network` - The network address space for the Wireguard VPN

### Optional

- `avena_wg_apt_repo` - The apt source which contains the `wireguard` package. -
  Leaving this variable undefined means your host distribution already has a
  `wireguard` package available.
  - Default: undefined, but role will assume buster-backports for Debian Buster
    hosts.
- `avena_wg_apt_repo_release` - The apt `default release` (`-t`) name if needed
  for the given `avena_wg_apt_repo` setting.
  - Default: undefined, but role will assume `buster-backports` for Debian
    Buster hosts.
- `avena_wg_interface` - Name of Wireguard interface on node.
  - Default: `wgAvena`
- `avena_wg_listen` - UDP port for Wireguard to listen on
  - Default: `51820`
- `avena_wg_keepalive` - The number of seconds between Wireguard keepalive
  messages (to pierce a private NAT: WiFi router, LTE gateway, etc.)
  - Default: `25`
