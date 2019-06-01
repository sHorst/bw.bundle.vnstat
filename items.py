svc_systemv = {}
svc_systemd = {}

if node.metadata.get('distro_release') == '16.04':
    svc_systemd["vnstat"] = {
        'needs': ['pkg_apt:vnstat'],
    }
else:
    svc_systemv["vnstat"] = {
        'needs': ['pkg_apt:vnstat'],
    }

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
        'command': 'vnstat -u -i {}'.format(interface),
        'unless': 'test -f /var/lib/vnstat/{}'.format(interface),
        'needs': ["pkg_apt:vnstat", ],
    }


files = {
    '/etc/vnstat.conf': {
        'source': "vnstat.conf",
        'content_type': 'mako',
        'owner': "root",
        'mode': "0644",
        'needs': [
            "pkg_apt:vnstat",
        ],
        'triggers': [
            "svc_systemd:vnstat:restart" if node.metadata.get('distro_release') == '16.04' else "svc_systemv:vnstat:restart"
        ],
    },
}

directories = {
    "/var/lib/vnstat": {
        'mode': "0755",
        'needs': [
            "pkg_apt:vnstat",
        ],
        'triggers': [
            "svc_systemd:vnstat:restart" if node.metadata.get('distro_release') == '16.04' else "svc_systemv:vnstat:restart"
        ],
    }
}
