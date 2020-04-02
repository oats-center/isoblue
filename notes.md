# Ensure IPs don't clash

In a default deploy, both Wireguard and Docker use local networks in the private
IP range. You must be sure to not allow those networks to overlap with any
physical network's IP range. For example, the 10.0.0.0/8 range is often used in
modern WiFi networks and should be avoided in Wireguard and Docker.

# Wireguard as the control network

1. Set `ansible_host` to the desired wireguard network IP.

# Write down your secrets

NOTE: We can (and probably should) use vault for this as well.

All things secret to your deploy needs to be written in a protected file. We
suggest you use `ansible-vault` to protect the secrets and commit it to a
private repository for safe keeping (`$ ansible-vault create secrets.yml`).

Currently the secrets that need to be defined are:

- `ansible_become_pass` -- The password used when Ansible tries to become root.
  Effectively the password of the `remote_user` account.

# Ansible rules of thumb for Avena

- Prefer `templates` over `lineinfile` or `blockinfile`.

  Rendering the entire file at once avoids many idempotent bugs. The "core"
  Avena roles should exclusively use `templates`, refactoring the roles as
  needed. `lineinfile`, `blockinfile`, etc. should be used by Avena extensions
  which need to modify a core file. **Take advantage of Debian ".d" directories
  when possible.** Never modify a Debian default file when there is a ".d"
  directory available.
