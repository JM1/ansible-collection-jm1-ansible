# Ansible Role `jm1.ansible.execute_modules`

This role helps with executing Ansible action plugins and Ansible modules which have been defined in Ansible variables.

Role variable `duties` defines a list of tasks which will be run by this role. Each task calls an Ansible module similar
to tasks in roles or playbooks except that only few [keywords][playbooks-keywords] such as `register` and `when` are
supported. For example, to ensure the inventory name for the current Ansible host being iterated over in the play is in
`/etc/hosts` define variable `duties` in [`group_vars` or `host_vars`][ansible-inventory] as such:

```yml
duties:
- ansible.builtin.lineinfile:
    path: /etc/hosts
    regexp: '\.1\s+{{ hostname }}'
    line: "{{ '{ip} {fqdn} {hostname}'.format(ip='127.0.0.1', fqdn=fqdn, hostname=hostname) }}"
    owner: root
    group: root
    mode: '0644'
  when: distribution_id | first in ['CentOS', 'Red Hat Enterprise Linux']
        or distribution_id in [['Debian', '10']]
- ansible.builtin.lineinfile:
    path: /etc/hosts
    regexp: '\.1\s+{{ hostname }}'
    line: "{{ '{ip} {fqdn} {hostname}'.format(ip='127.0.1.1', fqdn=fqdn, hostname=hostname) }}"
    owner: root
    group: root
    mode: '0644'
  when: distribution_id | first not in ['CentOS', 'Red Hat Enterprise Linux']
        and distribution_id not in [['Debian', '10']]
```

[ansible-inventory]: https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html
[playbooks-keywords]: https://docs.ansible.com/ansible/latest/reference_appendices/playbooks_keywords.html

**Tested OS images**
- Cloud image of [`Debian 10 (Buster)` \[`amd64`\]](https://cdimage.debian.org/cdimage/openstack/current/)
- Cloud image of [`Debian 11 (Bullseye)` \[`amd64`\]](https://cdimage.debian.org/images/cloud/bullseye/latest/)
- Cloud image of [`Debian 12 (Bookworm)` \[`amd64`\]](https://cdimage.debian.org/images/cloud/bookworm/daily/)
- Generic cloud image of [`CentOS 7 (Core)` \[`amd64`\]](https://cloud.centos.org/centos/7/images/)
- Generic cloud image of [`CentOS 8 (Core)` \[`amd64`\]](https://cloud.centos.org/centos/8/x86_64/images/)
- Generic cloud image of [`CentOS 9 (Stream)` \[`amd64`\]](https://cloud.centos.org/centos/9-stream/x86_64/images/)
- Ubuntu cloud image of [`Ubuntu 18.04 LTS (Bionic Beaver)` \[`amd64`\]](https://cloud-images.ubuntu.com/bionic/current/)
- Ubuntu cloud image of [`Ubuntu 20.04 LTS (Focal Fossa)` \[`amd64`\]](https://cloud-images.ubuntu.com/focal/)
- Ubuntu cloud image of [`Ubuntu 22.04 LTS (Jammy Jellyfish)` \[`amd64`\]](https://cloud-images.ubuntu.com/jammy/)

Available on Ansible Galaxy in Collection [jm1.ansible](https://galaxy.ansible.com/jm1/ansible).

## Requirements

None.

## Variables

| Name     | Default value | Required | Description |
| -------- | ------------- | -------- | ----------- |
| `duties` | `[]`          | no       | List of tasks to run [^supported-keywords] [^supported-modules] |

[^supported-modules]: Tasks will be executed with [`jm1.ansible.execute_module`][jm1-ansible-execute-module] which
supports modules and action plugins only. Some Ansible modules such as [`ansible.builtin.meta`][ansible-builtin-meta]
and `ansible.builtin.{include,import}_{playbook,role,tasks}` are core features of Ansible, in fact not implemented as
modules and thus cannot be called from `jm1.ansible.execute_module`. Doing so causes Ansible to raise errors such as
`MODULE FAILURE\nSee stdout/stderr for the exact error`. In addition, Ansible does not support free-form parameters
for arbitrary modules, so for example, change from `- debug: msg=""` to `- debug: { msg: "" }`.

[^supported-keywords]: Tasks will be executed with [`jm1.ansible.execute_module`][jm1-ansible-execute-module] which
supports keywords `register` and `when` only.

[ansible-builtin-meta]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/meta_module.html
[jm1-ansible-execute-module]: https://github.com/JM1/ansible-collection-jm1-ansible/blob/master/plugins/modules/execute_module.py

## Dependencies

None.

## Example Playbook

```yml
- hosts: all
  become: yes
  vars:
    # Variables are listed here for convenience and illustration.
    # In a production setup, variables would be defined e.g. in
    # group_vars and/or host_vars of an Ansible inventory.
    # Ref.:
    # https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html
    # https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html
    duties:
    - name: Clone a git repository
      ansible.builtin.git:
        repo: https://github.com/ansible/ansible-examples.git
        dest: /src/ansible-examples
  roles:
  - name: Execute Ansible action plugins and modules defined in variables
    role: jm1.ansible.execute_modules
    tags: ["jm1.ansible.execute_modules"]
```

For instructions on how to run Ansible playbooks have look at Ansible's
[Getting Started Guide](https://docs.ansible.com/ansible/latest/network/getting_started/first_playbook.html).

## License

GNU General Public License v3.0 or later

See [LICENSE.md](../../LICENSE.md) to see the full text.

## Author

Jakob Meng
@jm1 ([github](https://github.com/jm1), [galaxy](https://galaxy.ansible.com/jm1), [web](http://www.jakobmeng.de))
