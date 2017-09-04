#!/usr/bin/env python

# This is a collection of common functions that deal with containers
# in local environments
import docker

DOCKER_UNIX_SOCK = 'unix://var/run/docker.sock'


def filter_targets(self, obj, target):
    """ filter targets out of the found containers """
    result = []
    for container in obj:
        image = repr(container.image)
        if target in image:
            result.append(container.id)
    return result


def iterate_containers(self, obj, are_published=False):

    rawclient = docker.APIClient(base_url=DOCKER_UNIX_SOCK)

    result = {}
    for ID in obj:
        dic1 = rawclient.inspect_container(ID)
        ip = dic1.get('NetworkSettings').get('IPAddress')

        if are_published:
            extra = list((dic1.get('Config').get('ExposedPorts')).keys())
            prelist = dic1.get('NetworkSettings').get('Ports')
            port = prelist[extra[0]][0]['HostPort']

        else:
            # get exposed containers
            dport = list(dic1.get('Config').get('ExposedPorts').keys())
            port = dport[0].replace('/tcp', '')

        # CR: consider creating an Address object which has IP & port
        result[ip] = port

    return result


def get_exposed_addresses(self, obj):
    """ returns list of ip + port of exposed registries """

    return iterate_containers(self, obj, are_published=False)


def get_published_addresses(self, obj):
    """ returns list of ip + port of published registries """

    return iterate_containers(self, obj, are_published=True)


def get_ids(self, obj, target):
    """ get container's ids for exposed/published ports """

    client = docker.from_env()

    if 'exposed' == obj:
        running = client.containers.list(filters={'expose': '0-65535'})
        exposed = filter_targets(self, running, target)
        if not exposed:
            return 0
        else:
            return get_exposed_addresses(self, exposed)
    elif 'published' == obj:
        running = client.containers.list(filters={'publish': '0-65535'})
        published = filter_targets(self, running, target)
        if not published:
            return 0
        else:
            return get_published_addresses(self, published)
