# SSH Central Authority (CA) Authentication

Avena fleet deployments may leverage SSH central authority (CA) keys. CA keys
apply to both host and user authentication. While slightly more complicated
upfront, managing a fleet of nodes based on a CA is much easier and more secure
then dealing with each node individually.

Avena CA authentication is enabled by Ansible `ca-*` role(s).

## What is SSH CA authentication

In short, CA based authentication is where the central authorities' key is
trusted by all things within the domain for the purposes of authentication.
Sometimes the CA will use a different key for authenticating hosts vs users, but
not always.

## The nominal CA authentication flow

### Background

- **Alice** is someone/something that wants access to a system.
  - Alice could be a person wanting shell access, an automated process
    updating the system, etc.
- **Node** is a remote resource. In our case it is likely an ISOBlue Avena
  host, but could be anything running a SSH server.

### Flow

_Note: This flow simplifies the SSH process, but is logically consistent. Also,
remember this flow happens automatically. From the users perspective they do
nothing but request a certificate followed by the typical `ssh` commands._

1. Alice requests authorization to certain node(s)

   We use the open source [HashiCorp Vault](https://www.vaultproject.io/)
   software for OATS fleets.

2. If the central authority approves, it provides Alice a certificate of
   authorization signed by the CA's user key. The certificate essentially
   contains:

   - A valid date and time range.
   - A description of the allowed access (via `principals` and `extensions`)
   - Reference to Alice's public key.

   Note: A certificate is "public" in the sense that it not useful without
   Alice's private key (which should be strongly protected by Alice). That said,
   there may not be a good reason to be intensionally publicly share
   certificates.

   **In short**: Alice has a "ticket" into the system.

3. Alice connects to the node and collects the node's host public key and
   certificate. Alice verifies that:

   - the node's public key and certificate match
   - the certificate originated from the CA's host key.

   **In short**: Alice verifies that the node is trusted by the CA.

4. Alice presents her certificate and her part of the session key, encrypted by
   her public key.

   **In short**: Alice provides proof that she is authorized and starts
   authentication process.

5. The node verifies that:

   - Alice's public key and certificate match
   - Alice's certificate originated from the CA's user key.

   If everything is valid, the node sends Alice its part of the session key,
   encrypted by the node's host private key.

   **In short**: The node accepts Alice's certificate of authorization and
   completes the authentication process.

6. Both Alice and node decrypt the parts of the session key that they received,
   using the peer's public key. Each generates the complete session key. The
   rest of the session will be encrypted using only this session key. Therefore,
   both sides will only be able to successfully decrypt the session if each
   computed the same key. When this happens, they can both be sure each side
   is who they say they are, because the parts of the session key were
   encrypted by each side's private key, known only to them.

   **In short**: Both the node and Alice trust each and have verified each
   others identify.

7. The node will maintain a session which provides Alice with whatever access
   the certificate allows for.

   **In short**: Alice is authorized, authenticated, and has access. Success!

## The primary take aways

- The CA is in charge of **authorizing** user access to resources.
- Remote resources do not have prior knowledge of users and users do not have
  prior knowledge of resources.
- The remote resources and users all only know about the CA -- no local
  maintenance is required to extend the fleet.

### So, what do I gain?

There are many good reasons to use a SSH CA when managing a fleet of many nodes.
Here are just a few:

1. Deploying (and removing) user's public key to every node whenever there is
   a policy and/or access change is difficult. Even more so with ISOBlue because
   they are not necessarily on when you need them to be.

2. CA certificates can be generated to give specific types of access, e.g.,
   assess to only certain user names, (dis-)allow SSH port forwarding, etc.

## So, what is this "host" certificate mentioned in the flow?

The host certificate is essentially the same thing as Alice's user certificate,
expect that authenticates the host to Alice rather then Alice to the host.

### All Avena nodes should have their SSH host key signed by your CA host key

Machines that access Avena based nodes should be setup to trust the CA public
host key. This bypasses the need for every user to manually verify every Avena
host. Additionally, when connecting to a known member of the fleet the host key
should automatically verify. **If SSH complains about the host key, then you
must assume the node has been tampered with.**

### All this is great, but "what" is the CA

Well, that is up to you. A CA is anything that can provide proper certificates
to hosts and users after verifying a request is authorized. Determining what
authorization is acceptable is a "business" decision within your fleet and not
something ISOBlue Avena can determine for you.

To manage [OATS](https://oatscenter.org) fleets, we use [HashiCorp
Vault](https://www.vaultproject.io/) as our CA software. In general, our access
policy is to create `vault` users that have full rights to certain nodes. We
trust those users and allow them to self-create short lived certificates as
needed. This seems similar to just putting user public keys onto each node in
the `authorized_keys` file, but keep in mind using the `vault` CA we can easily
add/remove access, regardless if the node is currently available or not.
Finally, `vault` is able to manage significantly more complex policies then that
if needed.

Note: ISOBlue Avena provides an Ansible `ca` role that automatically gives each
deployed ISOBlue a host certificate as well as configures it to trust the CA, as
long as the user running the Ansible playbook is authenticated against the
`vault` CA and has permissions to create host certificates.

#### There as lots of CA options

We use `vault` for ease, but you have many options. You could:

- [Use a simple cli based tool](https://github.com/cloudtools/ssh-cert-authority)
- [Leverage the open source step certificates project](https://github.com/smallstep/certificates)
- [Run the CA by hand](https://jameshfisher.com/2018/03/16/how-to-create-an-ssh-certificate-authority/)
- Or take these concepts and build you own set of scripts.

### Where can I find more about CA based SSH

Here are some useful sources:

- [Facebook engineering: Scalable and secure access with SSH](https://engineering.fb.com/security/scalable-and-secure-access-with-ssh/)
- [Smallstep: If you're not using SSH certificates you're doing SSH wrong](https://smallstep.com/blog/use-ssh-certificates/)
- [Uber: Introducing the Uber SSH Certificate
  Authority](https://medium.com/uber-security-privacy/introducing-the-uber-ssh-certificate-authority-4f840839c5cc)
