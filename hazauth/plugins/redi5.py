import abstract
import optparse
from utils import containers

import redis

NONE = 0
TARGET = 'redis'

class RedisScanner(abstract.AbsPlugin):
    """ Redis instances authentication Scanner """


    def __check_auth(self, ip,port):
        """ checks redis for auth"""
        hazauth=True
        r = redis.StrictRedis(host=ip,port=port,password='')
        r.set('hazauth','true')
        value = r.get('hazauth')
        if value == None:
            return hazauth
        r.delete('hazauth')
        hazauth = False
        return hazauth

    def check(self, args):
        """ checks for authentication of Redis instances """

        parser = optparse.OptionParser(usage="redi5 check <options>")
        parser.add_option('-i', '--host',
                          help='IP addresses to scan, 1 per flag',
                          action='append', dest='hosts')
        parser.add_option('-l', '--local',
                          help='scans local redis containers',
                          action='store_true', dest='local')
        parser.add_option('-p', '--port',
                          help='additional port to scan,1 per flag, defaults are: [6379]',
                          action='append', type=int, dest='ports', default=[6379])

        (options, args) = parser.parse_args(args)

        if not options.hosts and not options.local:
            parser.print_help()
            return

        if options.local:
            published_addr =  containers.get_ids(self, 'published', TARGET)
            exposed_addr =  containers.get_ids(self, 'exposed', TARGET)
            if not exposed_addr and not published_addr:
                print("could not locate local redis instances, are we running on the host?")
                return

            elif not exposed_addr and published_addr:
                print("Found externally accessible redis instances!\nChecking Auth...\n")
                for ip in published_addr:
                    hazauth = self.__check_auth(ip,published_addr[ip])
                    if hazauth:
                    	print("the instance at {}:{} is configured correctly".format(ip,published_addr[ip]))
                    print('Redis instance at {}:{} has no authentication configured!'.format(ip,published_addr[ip]))

            print("Found internally accessible redis instances\nChecking Auth...\n")
            for ip in containers.get_ids(self, 'exposed', TARGET):
                hazauth = self.__check_auth(ip,exposed_addr[ip])
                if hazauth:
                    print("the instance at {}:{} is configured correctly".format(ip,exposed_addr[ip]))
                print('Redis instance at {}:{} has no authentication configured!'.format(ip,exposed_addr[ip]))

        if options.hosts:
            for ip in options.hosts:
                for port in options.ports:
                    self.__check_auth(ip, port)


def load():
    """ Loads the Registry Scanner """
    return RedisScanner()



