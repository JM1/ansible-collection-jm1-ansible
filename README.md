# Ansible Collection for Ansible power users

This repo hosts Ansible collection [`jm1.ansible`](https://galaxy.ansible.com/jm1/ansible).

The collection includes content which extends Ansible's core features.

For example, action plugin [`jm1.ansible.execute_module`][jm1-ansible-execute-module] allows to execute an arbitrary
Ansible module whose name and parameters are expanded from Jinja2 templates:

```yml
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
```

Role [`jm1.ansible.execute_modules`][jm1-ansible-execute-modules] builds upon said action plugin to allow executing
tasks which have been defined with variable `duties` in [`group_vars` or `host_vars`][ansible-inventory] as such:

```yml
duties:
- ansible.builtin.lineinfile:
    path: /etc/hosts
    regexp: '\.1\s+{{ hostname }}'
    line: "{{ '{ip} {fqdn} {hostname}'.format(ip='127.0.0.1', fqdn=fqdn, hostname=hostname) }}"
    owner: root
    group: root
    mode: '0644'
```

By default, Ansible offers several modules like [`ansible.builtin.import_tasks`][ansible-builtin-import-tasks] and
[`ansible.builtin.include_tasks`][ansible-builtin-include-tasks] to dynamically and statically load tasks from files.
But Ansible does not offer any module to load tasks from variables without this indirection through files. Ansible's
[`block`][ansible-block] statement does not support Jinja2 templates, so Ansible does not allow to define tasks in a
variable and pass this variable to `block`.

[ansible-block]: https://docs.ansible.com/ansible/latest/user_guide/playbooks_blocks.html
[ansible-builtin-import-tasks]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/import_tasks_module.html
[ansible-builtin-include-tasks]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/include_tasks_module.html
[ansible-inventory]: https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html
[jm1-ansible-execute-module]: plugins/modules/execute_module.py
[jm1-ansible-execute-modules]: roles/execute_modules/README.md

## Included content

Click on the name of a module or role to view that content's documentation:

- **Modules**:
    * [execute_module][jm1-ansible-execute-module]
- **Roles**:
    * [execute_modules][jm1-ansible-execute-modules]

## Requirements and Installation

### Installing the Collection from Ansible Galaxy

Before using the `jm1.ansible` collection, you need to install it with the Ansible Galaxy CLI:

```sh
ansible-galaxy collection install jm1.ansible
```

You can also include it in a `requirements.yml` file and install it via
`ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: jm1.ansible
    version: 2023.2.22
```

## Usage and Playbooks

You can either call modules by their Fully Qualified Collection Name (FQCN), like `jm1.ansible.execute_module`, or you
can call modules by their short name if you list the `jm1.ansible` collection in the playbook's `collections`, like so:

```yaml
---
- name: Using jm1.ansible collection
  hosts: localhost

  collections:
    - jm1.ansible

  tasks:
    - name: Define a module call
      set_fact:
        slurp_proc_mounts:
          name: ansible.builtin.slurp
          args:
            src: /proc/mounts

    - name: Run a module defined in a variable
      execute_module: '{{ slurp_proc_mounts }}'
```

For documentation on how to use individual modules and other content included in this collection, please see the links
in the 'Included content' section earlier in this README.

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more
details.

## Contributing

There are many ways in which you can participate in the project, for example:

- Submit bugs and feature requests, and help us verify them
- Submit pull requests for new modules, roles and other content

We're following the general Ansible contributor guidelines;
see [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html).

If you want to develop new content for this collection or improve what is already here, the easiest way to work on the
collection is to clone this repository (or a fork of it) into one of the configured [`ANSIBLE_COLLECTIONS_PATHS`](
https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths) and work on it there:
1. Create a directory `ansible_collections/jm1`;
2. In there, checkout this repository (or a fork) as `ansible`;
3. Add the directory containing `ansible_collections` to your
   [`ANSIBLE_COLLECTIONS_PATHS`](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths).

Helpful tools for developing collections are `ansible`, `ansible-doc`, `ansible-galaxy`, `ansible-lint`, `flake8`,
`make` and `yamllint`.

| OS                                           | Install Instructions                                                |
| -------------------------------------------- | ------------------------------------------------------------------- |
| Debian 10 (Buster)                           | Enable [Backports](https://backports.debian.org/Instructions/). `apt install ansible ansible-doc ansible-lint flake8 make yamllint` |
| Debian 11 (Bullseye)                         | `apt install ansible ansible-lint flake8 make yamllint` |
| Debian 12 (Bookworm)                         | `apt install ansible ansible-lint flake8 make yamllint` |
| Red Hat Enterprise Linux (RHEL) 7 / CentOS 7 | Enable [EPEL](https://fedoraproject.org/wiki/EPEL). `yum install ansible ansible-lint ansible-doc  python-flake8 make yamllint` |
| Red Hat Enterprise Linux (RHEL) 8 / CentOS 8 | Enable [EPEL](https://fedoraproject.org/wiki/EPEL). `yum install ansible                          python3-flake8 make yamllint` |
| Red Hat Enterprise Linux (RHEL) 9 / CentOS 9 | Enable [EPEL](https://fedoraproject.org/wiki/EPEL). `yum install ansible                          python3-flake8 make yamllint` |
| Ubuntu 18.04 LTS (Bionic Beaver)             | Enable [Launchpad PPA Ansible by Ansible, Inc.](https://launchpad.net/~ansible/+archive/ubuntu/ansible). `apt install ansible ansible-doc ansible-lint flake8 make yamllint` |
| Ubuntu 20.04 LTS (Focal Fossa)               | Enable [Launchpad PPA Ansible by Ansible, Inc.](https://launchpad.net/~ansible/+archive/ubuntu/ansible). `apt install ansible ansible-doc ansible-lint flake8 make yamllint` |
| Ubuntu 22.04 LTS (Jammy Jellyfish)           | `apt install ansible             ansible-lint flake8 make yamllint` |

Have a look at the included [`Makefile`](Makefile) for
several frequently used commands, to e.g. build and lint a collection.

## More Information

- [Ansible Collection Overview](https://github.com/ansible-collections/overview)
- [Ansible User Guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer Guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## License

GNU General Public License v3.0 or later

See [LICENSE.md](LICENSE.md) to see the full text.

## Author

Jakob Meng
@jm1 ([github](https://github.com/jm1), [galaxy](https://galaxy.ansible.com/jm1), [web](http://www.jakobmeng.de))
