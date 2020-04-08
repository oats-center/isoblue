# Connecting to vault

_Note: This is not needed if you are not using `avena-ca` with vault._

_Note: There are many ways to connect / authenticate with vault. This is an
example `userpass` flow for a remote Vault server. Any method is sufficient as
log as you end up with an authenticated `vault` common on the machine running
the Ansible playbook._

```bash
$ export VAULT_ADDR="http://172.16.0.1:8200"
$ vault login -method=userpass username=avena
Password (will be hidden): <enter-password>
```

# Creating a fleet playbook

If you don't already have one, you must create a playbook for your fleet. This
is where you will configure which hosts in your fleet, have what roles. At the
time of this writing, the OATS fleet is managed by the following playbook,
called `oats-fleet.yml`:

```yml
- hosts: oats_fleet
  roles:
    - role: avena
    - role: avena-gps-time
    - role: avena-cell
    - role: avena-ca
    - role: avena-wireguard
```

# Deploying a new node

1. Install the base Avena distribution using the correct [installation
   guide](../hardware/) for your hardware platform.
2. Add the node to your fleet's inventory `hosts` file and configure any group
   and host level variables as needed.
3. Run the initial deploy:

   ```bash
   $ ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook oats-fleet.yml -i inventory/ --limit avena-apalis-dev01 -e "ansible_ssh_host=10.0.0.112" -k
   ```

   - `ANSIBLE_HOST_KEY_CHECKING=False` removes the need to externally (and -
     manually) approve the node's SSH host key. It will be replaced in the
     deploy anyway.
   - If the hostname in the inventory is the same as the hostname in which it is
     currently accessible, e.g., Ansible has a static public IP, then
     `-e - "ansible_ssh_host=<host-ip>"`
     is not needed. For the OATS fleet, we use `avena-wireguard` to connect with
     Avena nodes. Therefore, the inventory IP is the Wireguard IP and we use
     this flag to enable the initial deployment.
   - `-k` allows you enter the SSH password at runtime. This is mostly useful
     when `avena-ca` is to be used. Otherwise, you could store this password in
     your inventory using Ansible vault.

# Updating a new

1. Get the auth certificate
   `vault write -field=signed_key avena-client-signer/sign/admin public_key=@$HOME/.ssh/id_ed25519.pub > ~/.ssh/id_ed25519-cert.pub`

Updating a
