#!/usr/bin/env python

# This is a plugin that scanns docker registries for authentication.
# it is able to scan local registries with the help of docker deamon
# and remote registries by utilizing docker registry API.

import abstract
import optparse
from utils import containers

import docker
import requests
from requests.adapters import HTTPAdapter

# surpress self-signed certificate warning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

NONE = 0
TARGET = 'registry'


class RegistryScanner(abstract.AbsPlugin):
    """ Docker Registry Scanner """

    def __http_request(self, ip, port, path):
        """ sending an http request to the registry and returns status code """

        url = 'http://{ip}:{port}/v2/{path}'.format(
            ip=ip, port=port, path=path)

        try:
            r = requests.Session()
            r.mount('http://', HTTPAdapter(max_retries=2))
            result = r.get(url, timeout=3)
        except requests.exceptions.RequestException:
            return NONE
        return result

    def __https_request(self, ip, port, path):
        """ sending an https request to the registry and returns status code """

        url = 'https://{ip}:{port}/v2/{path}'.format(
            ip=ip, port=port, path=path)

        try:
            r = requests.Session()
            r.mount('https://', HTTPAdapter(max_retries=2))
            result = r.get(url, verify=False, timeout=2)
        except requests.exceptions.RequestException:
            return NONE

        return result

    def __is_registry(self, ip, port):
        """ confirms that the address is in fact a docker registry"""

        result = self.__http_request(ip, port, '')
        if result != NONE and 'Docker-Distribution-Api-Version' in result.headers:
            return True
        result = self.__https_request(ip, port, '')
        if result != NONE and 'Docker-Distribution-Api-Version' in result.headers:
            return False
        return True

    def __check_internal(self, ip, port, num):
        """ checks internal containers for auth"""
        if num == 1:
            result = self.__http_request(ip, port, '')
            if result.status_code == 200:
                status = "Unsecured(R/W) " + "\033[1;33mInternal\033[1;m " + \
                    "Registry Detected at http://{ip}:{port}".format(
                        ip=ip, port=port)
                return status

            elif result.status_code == 401:
                result = self.__http_request(ip, port, '_catalog')
                if result.status_code == 200:
                    status = "Accessible(R) " + "\033[1;33mInternal\033[1;m " + \
                        "Registry Detected at http://{ip}:{port}".format(
                            ip=ip, port=port)
                    return status
                elif result.status_code == 401:
                    status = "This is a \033[92mSecured\033[1;m" + "Registry http://{ip}:{port}".format(
                        ip=ip, port=port)
                    return status

            elif result.status_code == 404:
                status = "seems like not a v2 registry, please check manually http://{ip}:{port}".format(
                    url=url, port=port)
                return status

            else:  # should be SSL
                result = self.__https_request(ip, port, '')
                if result.status_code == 200:
                    status = "Unsecured(R/W) " + "\033[1;33mInternal\033[1;m " + \
                        "Registry Detected at https://{ip}:{port}".format(
                            ip=ip, port=port)
                    return status
                elif result.status_code == 401:
                    result = self.__https_request(
                        ip, port, '_catalog')
                    if result.status_code == 200:
                        status = "Accessible(R) " + "\033[1;33mInternal\033[1;m " + \
                            "Registry Detected at https://{ip}:{port}".format(
                                ip=ip, port=port)
                        return status
                    elif result.status_code == 401:
                        status = "This is a \033[92mSecured\033[1;m" + "Registry https://{ip}:{port}".format(
                            ip=ip, port=port)
                        return status
                elif result.status_code == 404:
                    status = "this is a v1 registry and is not currently supported, please check it manualy at https://{ip}:{port}".format(
                        ip=ip, port=port)
                    return status

        elif num == 2:
            result = self.__http_request(ip, port, '')
            if result == NONE:
                return NONE
            if result.status_code == 200:
                status = "Unsecured(R/W) " + "\033[1;31mExternal(!)\033[1;m " + \
                    "Registry Detected at http://{ip}:{port}".format(
                        ip=ip, port=port)
                return status

            elif result.status_code == 401:
                result = self.__http_request(ip, port, '_catalog')
                if result.status_code == 200:
                    status = "Accessible(R) " + "\033[1;31mExternal(!)\033[1;m " + \
                        "Registry Detected at http://{ip}:{port}".format(
                            ip=ip, port=port)
                    return status
                elif result.status_code == 401:
                    status = "This is a \033[92mSecured\033[1;m" + " Registry http://{ip}:{port}".format(
                        ip=ip, port=port)
                    return status

            elif result.status_code == 404:
                status = "seems like not a v2 registry, please check manually http://{ip}:{port}".format(
                    url=url, port=port)
                return status

            else:  # should be SSL
                result = self.__https_request(ip, port, '')
                if result == NONE:
                    return NONE
                if result.status_code == 200:
                    status = "Unsecured(R/W) " + "\033[1;31mExternal(!)\033[1;m " + \
                        "Registry Detected at https://{ip}:{port}".format(
                            ip=ip, port=port)
                    return status

                elif result.status_code == 401:
                    result = self.__https_request(
                        ip, port, '_catalog')
                    if result == 200:
                        status = "Accessible(R) " + "\033[1;31mExternal(!)\033[1;m " + \
                            "Registry Detected at https://{ip}:{port}".format(
                                ip=ip, port=port)
                        return status
                    elif result.status_code == 401:
                        status = "This is a \033[92mSecured\033[1;m" + " Registry https://{ip}:{port}".format(
                            ip=ip, port=port)
                        return status

                elif result.status_code == 404:
                    status = "this is a v1 registry and is not currently supported, please check it manualy at https://{ip}:{port}".format(
                        ip=ip, port=port)
                    return status
        return NONE

    def __check_remote(self, ip, port):
        if not self.__is_registry(ip, port):
            return NONE

        url = 'http://{ip}:{port}/v2/'.format(ip=ip, port=port)
        result = self.__http_request(ip, port, '')
        if result == NONE:
            return NONE
        if result.status_code == 200:
            status = "Unsecured(R/W) " + "\033[1;31mRemote(!)\033[1;m " + \
                "Registry Detected at {url}".format(url=url)
            return status

        elif result.status_code == 401:
            result = self.__http_request(ip, port, '_catalog')
            if result.status_code == 200:
                status = "Accessible(R) " + "Registry Detected at {url}".format(
                    url=url)
            elif result.status_code == 401:
                status = "This is a \033[92mSecured\033[1;m" + " Registry http://{ip}:{port}".format(
                    ip=ip, port=port)
                return status
        elif result.status_code == 404:
            status = "this is a v1 registry and is not currently supported, please check it manualy {url}".format(
                url=url)
            return status

        else:  # should be SSL
            result = self.__https_request(ip, port, '')
            if result == NONE:
                return NONE
            if result.status_code == 200:
                status = "Unsecured(R/W) " + "\033[1;31mRemote(!)\033[1;m " + \
                    "Registry Detected at {url}".format(url=url)
                return status

            elif result.status_code == 401:
                result = self.__https_request(ip, port, '_catalog')
                if result == NONE:
                    return NONE
                if result.status_code == 200:
                    status = "Accessible(R) " + "Registry Detected at {url}".format(
                        url=url)
                    return status
                elif result.status_code == 401:
                    status = "This is a \033[92mSecured\033[1;m" + " Registry https://{ip}:{port}".format(
                        ip=ip, port=port)
                    return status
            elif result.status_code == 404:
                status = "this is a v1 registry and is not currently supported, please check it manualy {url}".format(
                    url=url)
                return status

    def check(self, args):
        """ checks for authentication of Docker registries """

        parser = optparse.OptionParser(usage="registry check <options>")
        parser.add_option('-i', '--host',
                          help='IP addresses to scan, 1 per flag',
                          action='append', dest='hosts')
        parser.add_option('-l', '--local',
                          help='scans local registry containers',
                          action='store_true', dest='local')
        parser.add_option('-p', '--port',
                          help='additional port to scan,1 per flag, defaults are: [80,443,5000,8000,8080,9200]',
                          action='append', type=int, dest='ports', default=[443, 80, 8080, 8000, 5000, 9200])

        (options, args) = parser.parse_args(args)

        if not options.hosts and not options.local:
            parser.print_help()
            return

        if options.local:
            published_addr = containers.get_ids(self, 'published', TARGET)
            exposed_addr = containers.get_ids(self, 'exposed', TARGET)
            if not exposed_addr and not published_addr:
                print("could not locate local registries, are we running on the host?")
                return

            elif not exposed_addr and published_addr:
                print("Found externally accessible registries!")
                print("Checking Auth...\n")
                for ip in published_addr:
                    status = self.__check_internal(ip, published_addr[ip], 2)
                    print('\n {}'.format(status))

            print("Found internally accessible registries\nChecking Auth...\n")
            for ip in containers.get_ids(self, 'exposed', TARGET):
                status = self.__check_internal(ip, exposed_addr[ip], 1)
                print('\n {}'.format(status))

        if options.hosts:
            print("\nScanning supplied ip addresses...\n")
            for ip in options.hosts:
                for port in options.ports:
                    status = self.__check_remote(ip, port)
                    if status != NONE:
                        print('\n{}'.format(status))


def load():
    """ Loads the Registry Scanner """
    return RegistryScanner()
