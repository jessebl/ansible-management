#!/usr/bin/env python
# Copyright (c) 2018 Jesse Bulson-Lewis
# Copyright (c) 2017 Ansible Project
# https://github.com/ansible/ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import argparse
from distutils.version import LooseVersion
import json
import os
import sys
from ipalib import api, errors, __version__ as IPA_VERSION
from six import u


def initialize():
    '''
    This function initializes the FreeIPA/IPA API. This function requires
    no arguments. A kerberos key must be present in the users keyring in
    order for this to work. IPA default configuration directory is /etc/ipa,
    this path could be overridden with IPA_CONFDIR environment variable.
    '''

    api.bootstrap(context='cli')

    if not os.path.isdir(api.env.confdir):
        print("WARNING: IPA configuration directory (%s) is missing. "
              "Environment variable IPA_CONFDIR could be used to override "
              "default path." % api.env.confdir)

    if LooseVersion(IPA_VERSION) >= LooseVersion('4.6.2'):
        # With ipalib < 4.6.0 'server' and 'domain' have default values
        # ('localhost:8888', 'example.com'), newer versions don't and
        # DNS autodiscovery is broken, then one of jsonrpc_uri / xmlrpc_uri is
        # required.
        # ipalib 4.6.0 is unusable (https://pagure.io/freeipa/issue/7132)
        # that's why 4.6.2 is explicitely tested.
        if 'server' not in api.env or 'domain' not in api.env:
            sys.exit("ERROR: ('jsonrpc_uri' or 'xmlrpc_uri') or 'domain' are not "
                     "defined in '[global]' section of '%s' nor in '%s'." %
                     (api.env.conf, api.env.conf_default))

    api.finalize()
    try:
        api.Backend.rpcclient.connect()
    except AttributeError:
        # FreeIPA < 4.0 compatibility
        api.Backend.xmlclient.connect()

    return api


def list_groups(api):
    '''
    This function prints a list of all host groups. This function requires
    one argument, the FreeIPA/IPA API object.
    '''

    inventory = {}
    hostvars = {}

    result = api.Command.hostgroup_find(all=True)['result']

    for hostgroup in result:
        # Get direct and indirect members (nested hostgroups) of hostgroup
        members = []

        if 'member_host' in hostgroup:
            members = [host for host in hostgroup['member_host']]
        if 'memberindirect_host' in hostgroup:
            members += (host for host in hostgroup['memberindirect_host'])
        inventory[hostgroup['cn'][0]] = {'hosts': [host for host in members]}

        for member in members:
            hostvars[member] = {}

    inventory['_meta'] = {'hostvars': hostvars}

    return inventory


def parse_args():
    '''
    This function parses the arguments that were passed in via the command line.
    This function expects no arguments.
    '''

    parser = argparse.ArgumentParser(description='Ansible FreeIPA/IPA '
                                     'inventory module')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true',
                       help='List active servers')
    group.add_argument('--host', help='List details about the specified host')

    return parser.parse_args()


def get_host_attributes(api, host):
    """
    This function expects one string, this hostname to lookup variables for.
    Args:
        api: FreeIPA API Object
        host: Name of Hostname

    Returns: Dict of Host vars if found else None
    """
    try:
        result = api.Command.host_show(u(host))['result']
        if 'usercertificate' in result:
            del result['usercertificate']
        return json.dumps(result, indent=1)
    except errors.NotFound as e:
        return {}

def filter_inventory(inventory, group):
    if not inventory.has_key(group):
        raise ValueError('"%s" group not found in FreeIPA' % group)
    group_hosts = inventory[group]['hosts']
    for group in inventory:
        if group is not '_meta':
            hosts = inventory[group]['hosts']
            inventory[group]['hosts'] =\
                    [host for host in hosts if host in group_hosts]
        else:
            hostvars = {}
            for host in group_hosts:
                hostvars[host] = inventory['_meta']['hostvars'][host]
            inventory['_meta']['hostvars'] = hostvars

    return inventory

def filter_main(group):
    args = parse_args()
    api = initialize()

    if args.host:
        print(get_host_attributes(api, args.host))
    elif args.list:
        inventory = list_groups(api)
        filtered_inventory = filter_inventory(inventory, group)
        print_inventory(filtered_inventory)

def print_inventory(inventory):
    inv_string = json.dumps(inventory, indent=1, sort_keys=True)
    print(inv_string)

if __name__ == '__main__':
    args = parse_args()
    api = initialize()

    if args.host:
        print(get_host_attributes(api, args.host))
    elif args.list:
        inventory = list_groups(api)
        print_inventory(inventory)
