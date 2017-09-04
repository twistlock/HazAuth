HazAuth
=================
HazAuth - an authentication testing framework


What's HazAuth
=================

An open source tool to test authentication in containerised applications.
With HazAuth you will be able to quickly identify services that are not locked with an authentication mechanism.

Currently HazAuth is shipped with 3 plugins:
1. Docker Registry
2. Redis
3. MongoDB

Requirments
==================
     python3.5
     requests
     docker
     docker-py
     redis-py
   ##### get requirments with:
       > pip3.5 install requests docker redis
       > apt-get install docker python3.5
Very quick install
==================


    >  docker run --disable-content-trust=false twistlock/hazauth -h
    
Dont want to run as a container? no problem!:
     
    > git clone https://github.com/twistlock/HazAuth.git
    > python3.5 hazauth.py -h

Available actions
=================

Currently HazAuth support these actions:

###  Scanning local registries:

    > docker run -v /var/run/docker.sock:/var/run/docker.sock twistlock/hazauth registry check -l
    
   ###### we have to mount the docker socket in order for hazauth to be able to scan local containers!
###  Scanning remote registry:

    > docker run twistlock/hazauth registry check -i IP -p PORT
###### by default (without -p flag) hazuath will scan this default ports: [80,443,5000,8000,8080,9200]


### Scanning a remote redis instance:

    > docker run twistlock/hazauth redi5 check -i IP -p PORT


###  Scanning local redis instances:

     >docker run twistlock/hazauth redi5 check -l
    
###  Scanning MongoDB:

    >





Documentation
=============

Documentation is still in progress... sorry!

Contributing
============

Any collaboration is welcome!

There are lots of additional possible plugins and improvments.
You can check the [Issues](https://github.com/twistlock/HazAuth/issues) and send us a Pull Request.

License
=======

This project is distributed under [GNU v3 license](https://github.com/twistlock/HazAuth/blob/master/LICENSE)
