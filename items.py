svc_systemd = {
    "vnstat": {
        'needs': ['pkg_apt:vnstat'],
    }
}

version = '1.16'
update_script = 'vnstat -u -i {interface}'
test = 'test -f /var/lib/vnstat/{interface}'

if node.os == 'debian':
    if node.os_version[0] == 10:
        version = '1.18'
    elif node.os_version[0] == 11:
        version = '2.6'
        update_script = 'vnstat -i {interface} --add'
        test = 'vnstat -i {interface}'
    elif node.os_version[0] >= 12:
        version = '2.10'
        update_script = 'vnstat -i {interface} --add'
        test = 'vnstat -i {interface}'

pkg_apt = {
    'vnstat': {},
}

actions = {}
for interface in sorted(node.metadata['interfaces'].keys()):
    if ":" in interface:
        # only "real" interfaces
        continue

    actions["initialize_backup_for_"+interface] = {
        'command': 'touch /var/lib/vnstat/.{i} && chown vnstat:vnstat /var/lib/vnstat/.{i}'.format(i=interface),
        'unless': 'test -f /var/lib/vnstat/.{}'.format(interface),
        'needs': ["pkg_apt:vnstat", ],
    }

    actions["initialize_database_for_"+interface] = {
        # will not fail if interface does not exist
        'command': update_script.format(interface=interface),
        'unless': ('test ! -f /sys/class/net/{interface}/operstate || ' + test).format(interface=interface),
        'needs': ["pkg_apt:vnstat", ],
    }


files = {
    '/etc/vnstat.conf': {
        'source': "vnstat.conf",
        'content_type': 'mako',
        'owner': "root",
        'group': 'vnstat',
        'mode': "0644",
        'context': {
            'version': version,
        },
        'needs': [
            "pkg_apt:vnstat",
        ],
        'triggers': [
            "svc_systemd:vnstat:restart"
        ],
    },
}

directories = {
    "/var/lib/vnstat": {
        'mode': "0755",
        'owner': 'vnstat',
        'group': 'vnstat',
        'needs': [
            "pkg_apt:vnstat",
        ],
        'triggers': [
            "svc_systemd:vnstat:restart"
        ],
    }
}
