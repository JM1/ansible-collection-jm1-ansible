#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim:set fileformat=unix shiftwidth=4 softtabstop=4 expandtab:
# kate: end-of-line unix; space-indent on; indent-width 4; remove-trailing-spaces modified;

# Copyright: (c) 2022, Jakob Meng <jakobmeng@web.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---

module: execute_module

short_description: Execute an Ansible module

description:
    - Execute an Ansible module whose I(name) and I(args) options can be
      expanded from Jinja2 templates.
    - Results of the module call will be passed back to the caller.
    - Ansible offers several modules to dynamically and statically load tasks
      from files, e.g. with M(ansible.builtin.include_tasks) and
      M(ansible.builtin.import_tasks). But Ansible does not offer any module
      to load tasks from variables without this indirection through files.
    - Ansible's C(block) statement does not support Jinja2 templates, so
      Ansible does not allow to define tasks in a variable and pass this
      variable to C(block).
    - "The implementation is inspired by Ansible's M(normal) action plugin
       which unfortunately cannot be called directly:
       U(https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/action/normal.py)"
    - "The C(when) support is inspired by Ansible's M(assert) action plugin:
       U(https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/action/assert.py)"

options:
    name:
        description:
            - Name of module to execute.
            - Both fully qualified collection names (FQCN) such as
              M(ansible.builtin.copy) and short names such as M(copy) are
              supported.
        type: str
        required: true
    args:
        description:
            - Arguments which will be passed to the module.
        type: dict
    register:
        description:
            - Name of a registered variable to create
              which contains the output of the module.
        type: str
    when:
        description:
            - Basic conditional, similar to Ansible's C(when) keyword, which
              must evaluate to C(True) for Ansible to execute this module.
        type: list

extends_documentation_fragment:
    - action_common_attributes
    - action_common_attributes.conn
    - action_common_attributes.flow
    - action_core

notes:
    - Some Ansible modules such as M(ansible.builtin.meta) and
      M(ansible.builtin.{include,import}_{playbook,role,tasks}) are core
      features of Ansible and not implemented as regular Ansible modules. Those
      fake Ansible modules cannot be called from M(execute_module). Calling
      them causes Ansible to raise errors such as
      B(MODULE FAILURE\nSee stdout/stderr for the exact error).

    - "Ansible's free-form parameters are not supported because Ansible does
       not allow arbitrary modules to use free-form parameters. So please
       change statements such as C(- debug: msg='') to use non-free-form
       parameters such as C(- debug: { msg: '' })."

    - Several Ansible modules such as M(ansible.builtin.debug) are partially or
      completely implemented as Action plugins, but are fully supported.
      For a list of Ansible modules with Action plugin counterparts refer to
      U(https://github.com/ansible/ansible/tree/devel/lib/ansible/plugins/action).

    - Redirects for Ansible action plugins and modules are fully supported.
      For example, M(ansible.netcommon.cli_parse) has been migrated to
      M(ansible.utils.cli_parse) and redirects have been added to the
      B(ansible.netcommon) collection to keep backward compatibility.
      Both names M(ansible.netcommon.cli_parse) and M(ansible.utils.cli_parse)
      can be used for I(name).

seealso:
    - module: ansible.builtin.include_tasks
    - module: ansible.builtin.import_tasks

author: "Jakob Meng (@jm1)"
'''

EXAMPLES = r'''
- name: Define a module call
  set_fact:
    slurp_proc_mounts:
      name: ansible.builtin.slurp
      args:
        src: /proc/mounts
      register: slurp_output

- name: Run a module defined in a variable
  jm1.ansible.execute_module: '{{ slurp_proc_mounts }}'

- name: Print registered variable
  debug:
    var: slurp_output
'''

RETURN = r'''
'''
