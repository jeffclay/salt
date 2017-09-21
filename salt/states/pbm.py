# -*- coding: utf-8 -*-
'''
Manages VMware storage policies
(called pbm because the vCenter endpoint is /pbm)

Examples
========

Storage policy
--------------

.. code-block:: python

{
    "name": "salt_storage_policy"
    "description": "Managed by Salt. Random capability values.",
    "resource_type": "STORAGE",
    "subprofiles": [
        {
            "capabilities": [
                {
                    "setting": {
                        "type": "scalar",
                        "value": 2
                    },
                    "namespace": "VSAN",
                    "id": "hostFailuresToTolerate"
                },
                {
                    "setting": {
                        "type": "scalar",
                        "value": 2
                    },
                    "namespace": "VSAN",
                    "id": "stripeWidth"
                },
                {
                    "setting": {
                        "type": "scalar",
                        "value": true
                    },
                    "namespace": "VSAN",
                    "id": "forceProvisioning"
                },
                {
                    "setting": {
                        "type": "scalar",
                        "value": 50
                    },
                    "namespace": "VSAN",
                    "id": "proportionalCapacity"
                },
                {
                    "setting": {
                        "type": "scalar",
                        "value": 0
                    },
                    "namespace": "VSAN",
                    "id": "cacheReservation"
                }
            ],
            "name": "Rule-Set 1: VSAN",
            "force_provision": null
        }
    ],
}

Dependencies
============


- pyVmomi Python Module


pyVmomi
-------

PyVmomi can be installed via pip:

.. code-block:: bash

    pip install pyVmomi

.. note::

    Version 6.0 of pyVmomi has some problems with SSL error handling on certain
    versions of Python. If using version 6.0 of pyVmomi, Python 2.6,
    Python 2.7.9, or newer must be present. This is due to an upstream dependency
    in pyVmomi 6.0 that is not supported in Python versions 2.7 to 2.7.8. If the
    version of Python is not in the supported range, you will need to install an
    earlier version of pyVmomi. See `Issue #29537`_ for more information.

.. _Issue #29537: https://github.com/saltstack/salt/issues/29537
'''

# Import Python Libs
from __future__ import absolute_import
import sys
import logging
import json
import time
import copy

# Import Salt Libs
from salt.exceptions import CommandExecutionError, ArgumentValueError
import salt.modules.vsphere as vsphere
from salt.utils import is_proxy
from salt.utils.dictdiffer import recursive_diff
from salt.utils.listdiffer import list_diff

# External libraries
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# Get Logging Started
log = logging.getLogger(__name__)
# TODO change with vcenter
ALLOWED_PROXY_TYPES = ['esxcluster', 'vcenter']
LOGIN_DETAILS = {}

def __virtual__():
    if HAS_JSONSCHEMA:
        return True
    return False


def mod_init(low):
    '''
    Init function
    '''
    return True


def default_vsan_policy_configured(name, policy):
    '''
    Configures the default VSAN policy on a vCenter.
    The state assumes there is only one default VSAN policy on a vCenter.

    policy
        Dict representation of a policy
    '''
    # TODO Refactor when recurse_differ supports list_differ
    # It's going to make the whole thing much easier
    policy_copy = copy.deepcopy(policy)
    proxy_type = __salt__['vsphere.get_proxy_type']()
    log.trace('proxy_type = {0}'.format(proxy_type))
    # All allowed proxies have a shim execution module with the same
    # name which implementes a get_details function
    # All allowed proxies have a vcenter detail
    vcenter = __salt__['{0}.get_details'.format(proxy_type)]()['vcenter']
    log.info('Running {0} on vCenter '
             '\'{1}\''.format(name, vcenter))
    log.trace('policy = {0}'.format(policy))
    changes_required = False
    ret = {'name': name, 'changes': {}, 'result': None, 'comment': None,
           'pchanges': {}}
    comments = []
    changes = {}
    changes_required = False
    si = None

    try:
        #TODO policy schema validation
        si = __salt__['vsphere.get_service_instance_via_proxy']()
        current_policy = __salt__['vsphere.list_default_vsan_policy'](si)
        log.trace('current_policy = {0}'.format(current_policy))
        # Building all diffs between the current and expected policy
        # XXX We simplify the comparison by assuming we have at most 1
        # sub_profile
        if policy.get('subprofiles'):
            if len(policy['subprofiles']) > 1:
                raise ArgumentValueError('Multiple sub_profiles ({0}) are not '
                                         'supported in the input policy')
            subprofile = policy['subprofiles'][0]
            current_subprofile = current_policy['subprofiles'][0]
            capabilities_differ = list_diff(current_subprofile['capabilities'],
                                            subprofile.get('capabilities', []),
                                            key='id')
            del policy['subprofiles']
            if subprofile.get('capabilities'):
                del subprofile['capabilities']
            del current_subprofile['capabilities']
            # Get the subprofile diffs without the capability keys
            subprofile_differ = recursive_diff(current_subprofile,
                                               dict(subprofile))

        del current_policy['subprofiles']
        policy_differ = recursive_diff(current_policy, policy)
        if policy_differ.diffs or capabilities_differ.diffs or \
           subprofile_differ.diffs:

            if 'name' in policy_differ.new_values or \
               'description' in policy_differ.new_values:

                raise ArgumentValueError(
                    '\'name\' and \'description\' of the default VSAN policy '
                    'cannot be updated')
            changes_required = True
            if __opts__['test']:
                str_changes = []
                if policy_differ.diffs:
                    str_changes.extend([change for change in
                                        policy_differ.changes_str.split('\n')])
                if subprofile_differ.diffs or capabilities_differ.diffs:
                    str_changes.append('subprofiles:')
                    if subprofile_differ.diffs:
                        str_changes.extend(
                            ['  {0}'.format(change) for change in
                             subprofile_differ.changes_str.split('\n')])
                    if capabilities_differ.diffs:
                        str_changes.append('  capabilities:')
                        str_changes.extend(
                            ['  {0}'.format(change) for change in
                             capabilities_differ.changes_str2.split('\n')])
                comments.append(
                    'State {0} will update the default VSAN policy on '
                    'vCenter \'{1}\':\n{2}'
                    ''.format(name, vcenter, '\n'.join(str_changes)))
            else:
                __salt__['vsphere.update_storage_policy'](
                    policy=current_policy['name'],
                    policy_dict=policy_copy,
                    service_instance=si)
                comments.append('Updated the default VSAN policy in vCenter '
                                '\'{0}\''.format(vcenter))
            log.info(comments[-1])

            new_values = policy_differ.new_values
            new_values['subprofiles'] = [subprofile_differ.new_values]
            new_values['subprofiles'][0]['capabilities'] = \
                    capabilities_differ.new_values
            if not new_values['subprofiles'][0]['capabilities']:
                del new_values['subprofiles'][0]['capabilities']
            if not new_values['subprofiles'][0]:
                del new_values['subprofiles']
            old_values = policy_differ.old_values
            old_values['subprofiles'] = [subprofile_differ.old_values]
            old_values['subprofiles'][0]['capabilities'] = \
                    capabilities_differ.old_values
            if not old_values['subprofiles'][0]['capabilities']:
                del old_values['subprofiles'][0]['capabilities']
            if not old_values['subprofiles'][0]:
                del old_values['subprofiles']
            changes.update({'default_vsan_policy':
                            {'new': new_values,
                             'old': old_values}})
            log.trace(changes)
        __salt__['vsphere.disconnect'](si)
    except CommandExecutionError as exc:
        log.error('Error: {}'.format(exc))
        if si:
            __salt__['vsphere.disconnect'](si)
        if not __opts__['test']:
            ret['result'] = False
        ret.update({'comment': exc.strerror,
                    'result': False if not __opts__['test'] else None})
        return ret
    if not changes_required:
        # We have no changes
        ret.update({'comment': ('Default VSAN policy in vCenter '
                                '\'{0}\' is correctly configured. '
                                'Nothing to be done.'.format(vcenter)),
                    'result': True})
    else:
        ret.update({'comment': '\n'.join(comments)})
        if __opts__['test']:
            ret.update({'pchanges': changes,
                        'result': None})
        else:
            ret.update({'changes': changes,
                        'result': True})
    return ret
