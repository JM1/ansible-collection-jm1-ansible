#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim:set fileformat=unix shiftwidth=4 softtabstop=4 expandtab:
# kate: end-of-line unix; space-indent on; indent-width 4; remove-trailing-spaces modified;

# Copyright: (c) 2022, Jakob Meng <jakobmeng@web.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleActionFail, AnsibleError
from ansible.module_utils._text import to_native
from ansible.module_utils.common.validation \
    import check_type_dict, check_type_str
from ansible.playbook.conditional import Conditional
from ansible.plugins.action import ActionBase
from ansible.utils.vars import isidentifier, merge_hash
import importlib


class ActionModule(ActionBase):

    _VALID_ARGS = frozenset(('args', 'name', 'register', 'when'))

    def run(self, tmp=None, task_vars=None):
        # Inspired by Ansible's 'normal' action plugin
        # Ref.:
        # https://docs.ansible.com/ansible/latest/plugins/action.html
        # https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/action/normal.py

        self._supports_check_mode = True
        self._supports_async = True

        result = super(ActionModule, self).run(tmp, task_vars)
        # tmp will not be deleted because it might be passed
        # to an action plugin and might get deleted there

        if not result.get('skipped'):

            # Return early if 'when' conditional evaluates to False
            whens = self._task.args.get('when', None)

            if isinstance(whens, bool) and not whens:
                result['changed'] = False
                result['skipped'] = True
                result['skip_reason'] = 'Conditional result was False'
                return result

            elif not isinstance(whens, bool) and whens:
                # make sure the 'when' items are a list
                if not isinstance(whens, list):
                    whens = [whens]

                cond = Conditional(loader=self._loader)

                for when in whens:
                    cond.when = [when]
                    evaluated = cond.evaluate_conditional(
                        templar=self._templar, all_vars=task_vars)
                    if not evaluated:
                        # Ref.: https://github.com/ansible/ansible/blob/
                        #       cb2e434dd2359a9fe1c00e75431f4abeff7381e8/
                        #       lib/ansible/executor/task_executor.py#L455
                        result['changed'] = False
                        result['skipped'] = True
                        result['skip_reason'] = 'Conditional result was False'
                        return result

            if result.get('invocation', {}).get('plugin_args'):
                # avoid passing to modules in case of no_log
                # should not be set anymore but here for backward compatibility
                del result['invocation']['plugin_args']

            wrap_async = self._task.async_val and \
                not self._connection.has_native_async

            # self._task.args['_raw_params'] is reserved to modules
            # listed in ansible.parsing.mod_args.RAW_PARAM_MODULES

            plugin_name = self._task.args.get('name', None)
            if not plugin_name:
                raise AnsibleActionFail("name is required")

            try:
                plugin_name = check_type_str(plugin_name,
                                             allow_conversion=False)
            except TypeError as e:
                raise AnsibleActionFail("Invalid value given for 'name': %s."
                                        % to_native(e))

            # Resolve Ansible module redirects
            # Ref.: https://github.com/ansible/ansible/blob/devel/lib/ansible/
            #       plugins/action/__init__.py
            resolved_plugin_name = None
            for mod_type in self._connection.module_implementation_preferences:
                if getattr(self._shared_loader_obj.module_loader,
                           'find_plugin_with_context', None):
                    # Ansible 2.10+
                    context = self._shared_loader_obj.module_loader.\
                        find_plugin_with_context(
                            plugin_name, mod_type,
                            collection_list=self._task.collections)

                    if not context.resolved \
                       and context.redirect_list \
                       and len(context.redirect_list) > 1:
                        # take the last one in the redirect list, we may
                        # have successfully jumped through N other
                        # redirects
                        target_module_name = context.redirect_list[-1]

                        raise AnsibleError("The module {0} was redirected to"
                                           " {1}, which could not be loaded."
                                           .format(plugin_name,
                                                   target_module_name))

                    # context.plugin_resolved_name is e.g.
                    # ansible_collections.ansible.builtin.plugins.modules.\
                    # package for both modules and action plugins
                    resolved_plugin_name = '.'.join(
                        [context.plugin_resolved_collection,
                         context.plugin_resolved_name.split('.')[-1]])
                else:
                    # Ansible 2.9
                    resolved_plugin_name, resolved_plugin_path = \
                        self._shared_loader_obj.module_loader.\
                        find_plugin_with_name(
                            plugin_name, mod_type,
                            collection_list=self._task.collections)
                    # resolved_plugin_name is e.g. ansible_collections.\
                    # openstack.cloud.plugins.modules.server
                    if resolved_plugin_name:
                        if '.' in resolved_plugin_name:
                            splitted = resolved_plugin_name.split('.')
                            resolved_plugin_name = \
                                '.'.join(splitted[1:3] + [splitted[-1]])
                        else:
                            resolved_plugin_name = \
                                'ansible.builtin.%s' % resolved_plugin_name
                if resolved_plugin_name:
                    break
            else:  # This is a for-else: http://bit.ly/1ElPkyg
                raise AnsibleError("The module %s was not found in configured"
                                   " module paths" % (plugin_name))

            assert resolved_plugin_name is not None
            plugin_name = resolved_plugin_name

            # Several modules are partially or completely implemented as
            # action plugins. Instead of calling them with
            # self._execute_module(), action plugins have to be imported
            # and run manually.
            if '.' in plugin_name \
               or plugin_name.startswith('ansible.builtin.') \
               or plugin_name.startswith('ansible.legacy.'):
                plugin_name_short = plugin_name.split('.')[-1]
                if plugin_name_short in ['block', 'import_playbook',
                                         'import_role', 'import_tasks',
                                         'include_role', 'include_tasks',
                                         'meta']:
                    raise AnsibleError(
                        "{0} is a core feature of Ansible and is not"
                        " implemented as a regular Ansible module. It cannot"
                        " be called from module jm1.ansible.execute_module."
                        .format(plugin_name))

                plugin_import_name = ('ansible.plugins.action.%s'
                                      % plugin_name_short)
            else:
                collection_name = plugin_name.split('.')[0:1].join('.')
                plugin_name_short = plugin_name.split('.')[-1]
                plugin_import_name = (
                    'ansible_collections.%s.plugins.action.%s'
                    % (collection_name, plugin_name_short))

            # Try to load action plugin
            try:
                action_type = importlib.import_module(
                    plugin_import_name).ActionModule
            except ImportError:
                # No action plugin found, so assume it is a module
                action_type = None

            plugin_args = self._task.args.get('args', None)
            if plugin_args:
                try:
                    plugin_args = check_type_dict(plugin_args)
                except TypeError as e:
                    raise AnsibleActionFail("Invalid value given for 'args':"
                                            " %s." % to_native(e))

            plugin_register = self._task.args.get('register', None)
            if plugin_register:
                try:
                    plugin_register = check_type_str(plugin_register,
                                                     allow_conversion=False)
                except TypeError as e:
                    raise AnsibleActionFail("Invalid value given for"
                                            " 'register': %s." % to_native(e))

                plugin_register = self._templar.template(plugin_register)

                if not isidentifier(plugin_register):
                    raise AnsibleActionFail(
                        "The variable name '%s' is not valid. Variables must"
                        " start with a letter or underscore character,"
                        " and contain only letters, numbers and underscores."
                        % plugin_register)

            if action_type is not None:
                # Run action plugin
                original_task_args = self._task.args
                self._task.args = plugin_args

                action = action_type(
                    task=self._task,
                    connection=self._connection,
                    play_context=self._play_context,
                    loader=self._loader,
                    templar=self._templar,
                    shared_loader_obj=self._shared_loader_obj)

                plugin_result = action.run(tmp, task_vars)
                result.update(plugin_result)

                # restore previous task args to not confuse users
                self._task.args = original_task_args
            else:
                # Run regular module
                module_result = self._execute_module(module_name=plugin_name,
                                                     module_args=plugin_args,
                                                     task_vars=task_vars,
                                                     wrap_async=wrap_async)

                result = merge_hash(result, module_result)

            if plugin_register:
                # This overwrites ansible_facts which
                # are returned from action plugins
                result['ansible_facts'] = {plugin_register: plugin_result}

        if not wrap_async:
            # remove a temporary path we created
            self._remove_tmp_path(self._connection._shell.tmpdir)

        return result
