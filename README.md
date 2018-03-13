# Ansible Management

Collected playbooks and inventories for my own use.

## Inventories

`<group>.py` (e.g. `production.py`) are dynamic inventories that provide all
the hosts from `<group>` along with their group membership.

## Playbooks

### `upgrade_packages.yml`

Upgrade yum and apt packages, and pin `iputils` versions inside CentOS
containers.

### `baseline.yml`

Performs base configurations for all systems. Standardizes locale, timezone,
and some package installation.
