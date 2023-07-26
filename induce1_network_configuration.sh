#!/bin/bash

#16: eno1.444@eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
#    link/ether 1c:98:ec:1c:51:40 brd ff:ff:ff:ff:ff:ff
#    inet 10.10.10.144/24 scope global eno1.444
#       valid_lft forever preferred_lft forever
#    inet6 fe80::1e98:ecff:fe1c:5140/64 scope link
#       valid_lft forever preferred_lft forever
#17: eno1.443@eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
#    link/ether 1c:98:ec:1c:51:40 brd ff:ff:ff:ff:ff:ff
#    inet 10.10.9.144/32 scope global eno1.443
#       valid_lft forever preferred_lft forever
#    inet6 2a02:587:f805:fff:484c:4a85:b94a:7300/64 scope global temporary dynamic
#       valid_lft 603704sec preferred_lft 84858sec
#    inet6 2a02:587:f805:fff:1e98:ecff:fe1c:5140/64 scope global dynamic mngtmpaddr
#       valid_lft 2591979sec preferred_lft 604779sec
#    inet6 fe80::1e98:ecff:fe1c:5140/64 scope link
#       valid_lft forever preferred_lft forever

sudo ip link add link eno1 name eno1.444 type vlan id 444
sudo ip link add link eno1 name eno1.443 type vlan id 443
sudo ip address add 10.10.10.144/24 dev eno1.444
sudo ip address add 10.10.9.144/24 dev eno1.443
sudo ip link set dev eno1.444 up
sudo ip link set dev eno1.443 up

