# Using Avena to manage your fleet

The latest release of the Avena collections can be downloaded using the
`ansible-galaxy` command. But first, you must create an Ansible project for your
fleet and define the inventory. This guide will walk you through our recommend
setup.

Much of this is based on Jeff Geerling's excellent "[Ansible best practices:
using project-local collections and roles][geerling-best-practice]" article. We
think you should read it.

**TODO:** _Make an open-source version of `oats-fleet` as an example._

## Create a project folder

We recommend that you create a folder of ansible configurations, galaxy
collections, roles, and playbooks for your fleet. Ansible has several folder
structures that they support, our favorite is something like:

```
.
├── ansible.cfg
├── ansible_collections
│   └── oats
│       └── avena
├── inventory
│   ├── group_vars
│   │   └── fleet.yml
│   ├── hosts
│   └── host_vars
│       ├── device-1.yml
│       ├── device-2.yml
│       └── device-3.yml
├── isoblue.yml
├── isoblue-hd.yml
├── roles
│   └── custom-tests
│       ├── files
│       ├── templates
│       ├── defaults
│       └── custom-tests.yml
└── requirements.yml
```

Where:

- `isoblue.yml` and `isoblue-hd.yml` are examples of playbooks that depend
  on Avena collection roles, but also contain custom tasks for each specific
  device type in your fleet.
- `device-1.yml`, `device-2.yml`, and `device-3.yml`
  are example host variable files for the hostnames (defined in `hosts`)
  `device-1`, `device-2`, and `device-3`, respectfully.
- `fleet.yml` are group variables for the hosts within the `fleet` group as
  defined in the `hosts` file.

This folder may also contain any standard Ansible file, e.g., `roles` and used
within playbooks like any Ansible project.

For more details, check out Ansible's [content organization
documentation][ansible-content-org].

## Create an ansible.cfg

We recommend Jeff Geerling's minimal default ([source][geerling-best-practice]).

This configuration forces galaxy installed collections and roles to live within
the project, rather then your home directory. This improves repeatable
builds/runs. We also strongly recommend that you consider committing
`ansible_collections` to version control (as Jeff also suggests), at least until
`ansible-galaxy` has a true version locking scheme.

```ini
[defaults]

nocows = True
collections_paths = ./
roles_path = ./roles
```

## Creating a requirements.yml

`requirements.yml` defines what Ansible Galaxy dependencies are needed for the
project. For a basic Avena deployment, only the `oats.avena` collection is
needed. If you don't know what version you need, then you should probably use
whatever is newest.

```yml
---
collections:
  - name: oats.avena
    version: 0.1.0
```

## Installing ansible requirements

#### From Galaxy (typical)

```console
$ ansible-galaxy install -r requirements.yml
```

#### From a build

```console
$ ansible-galaxy collection install oats-avena-0.1.0.tar.gz
```

#### From git

**Note:** _This method ignores requirements.yml for the Avena collection. Be
sure to properly release your changes and update requirements.yml when your
done._

I find it easiest to clone this repo locally and link it into your projects
`ansible_collections` folder. Something like

```console
$ ln -rs ../isoblue-avena/ansible/avena ./ansible_collections/oats/`
```

when at the root of your project and `isoblue-avena` is cloned into the path
`../isoblue-avena` relative your project.

## Create a fleet playbook

If you don't already have one, create a playbook for your fleet. Here you can
add any type of custom tasks and roles as you would like. To deploy Avena, you
must include at least the `oats.avena.core` role.

For example, the below playbook would deploy the Avena core along with GPS time
synchronization, enable a cell modem, use CA based SSH authentication, and a
wireguard VPN.

```yml
- hosts: fleet
  roles:
    - oats.avena.core
    - oats.avena.gps_time
    - oats.avena.cell
    - oats.avena.ca
    - oats.avena.wireguard
```

## Vault (if using `avena-ca`)

#### Connecting to Vault

_Note: There are other ways to connect / authenticate with vault. This is an
example of `userpass`._

```console
$ export VAULT_ADDR="http://172.16.0.1:8200"
$ vault login -method=userpass username=avena
Password (will be hidden): <enter-password>
```

#### Obtaining a certificate

A certificate is only need after the initial deploy. A plain password is used to
authenticate until the `avena-ca` role completes. However, if the deploy
fails, you may also need one to restart the process.

```console
$ vault write -field=signed_key avena-client-signer/sign/admin public_key=@$HOME/.ssh/id_ed25519.pub > ~/.ssh/id_ed25519-cert.pub
```

Where a Vault CA signer is mounted at `avena-client-signer` with sufficient
permissions for the `admin` role and an ed25519 SSH user key.

# Deploying a new node

1. Install Debian using your hardware platform's [installation
   guide](../hardware/).
2. Add the node to your fleet's inventory and configure variables as needed.
3. Update your systems Vault CA certificate (if needed) using the Vault section
   above.
4. Complete the initial deploy by running the following from within your project
   folder:

   ```console
   ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook isoblue.yml -i inventory --limit device-1 -e "ansible_ssh_host=10.0.0.2" -k
   ```

   Where,

   - `ANSIBLE_HOST_KEY_CHECKING=False`: _Optional_. Disable host key checking because it is
     unlikely that you have already manually approved the installation's default
     host key. The default key will be replaced by an ed25519 key. You will need
     to locally trust that key before any future Ansible commands.

     - Note: If using `avena-ca`, then all you need to trust on your local
       computer is the CA key. After that, all fleet nodes are trusted.

   - `-e - "ansible_ssh_host=<host-ip>"`: _Optional_. Temporarily overrides the
     host address. Ansible variables will still be set by the hostfile
     defination, but Ansible will SSH into the provided IP address. This is
     useful:

     - The node deployed is being deployed on a local network, but the final
       public IP is already known.
     - The node will use a Wireguard (or similar) VPN and the hostfile
       reflects the VPN address.

   - `-k`: _Optional_. Enter the SSH password at runtime. This is useful when
     using `avena-ca` (or some other password less based authentication). The
     initial deploy is authenticated by password, but all following Ansible
     commands are password less.
     - If passwords will always be used, then you could securely store each
       node's password in the inventory with Ansible vault (not to be
       confused with Hashicorp Vault from above).

# Updating nodes

1. Update your systems Vault CA certificate (if needed) using the Vault section above.
2. Run the playbook of intrest

```console
   $ ansible-playbook isoblue.yml -i inventory/
```

_Note: You can include the `--limit` flag if you want to work on some nodes_

[geerling-best-practice]: https://www.jeffgeerling.com/blog/2020/ansible-best-practices-using-project-local-collections-and-roles
[ansible-content-org]: https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html#content-organization
