#!/usr/bin/python

# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.link import Intf
from mininet.util import quietRun

from p4_mininet import P4Switch, P4Host

import argparse
from time import sleep
import os
import subprocess
import threading
import re
import sys

os.system('dpkg -i /tmp/python3-six_1.10.0-3_all.deb')
os.system('tar -xvzf /tmp/construct-2.9.45.tar.gz')
os.system('cd /tmp/construct-2.9.45 && python3 setup.py install')
#from twamp_server import start_twamp_server

_THIS_DIR = os.path.dirname(os.path.realpath(__file__))
_THRIFT_BASE_PORT = 22222

parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", required=True)
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)
parser.add_argument('--cli', help='Path to BM CLI',
                    type=str, action="store", required=True)
args = parser.parse_args()

class MyTopo(Topo):
    def __init__(self, sw_path, json_path, nb_hosts, nb_switches, links, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        for i in xrange(nb_switches):
           self.addSwitch('s%d' % (i + 1),
                            sw_path = sw_path,
                            json_path = json_path,
                            thrift_port = _THRIFT_BASE_PORT + i,
                            pcap_dump = True,
                            device_id = i,
                            enable_debugger = True)

        for h in xrange(nb_hosts):
            self.addHost('h%d' % (h + 1), ip="10.0.%d.%d" % ((h + 1),(h + 1)),
                    mac="00:00:00:00:0%d:0%d" % ((h+1), (h+1)))

        for a, b in links:
            self.addLink(a, b)

def read_topo():
    nb_hosts = 0
    nb_switches = 0
    links = []
    with open("topo.txt", "r") as f:
        line = f.readline()[:-1]
        w, nb_switches = line.split()
        assert(w == "switches")
        line = f.readline()[:-1]
        w, nb_hosts = line.split()
        assert(w == "hosts")
        for line in f:
            if not f: break
            a, b = line.split()
            links.append( (a, b) )
    return int(nb_hosts), int(nb_switches), links


def readRegister(register, thrift_port, idx=None):
        p = subprocess.Popen(['simple_switch_CLI', '--thrift-port', str(thrift_port)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if idx is not None:
            stdout, stderr = p.communicate(input="register_read %s %d" % (register, idx))
            reg_val = filter(lambda l: ' %s[%d]' % (register, idx) in l, stdout.split('\n'))[0].split('= ', 1)[1]
            return long(reg_val)
        else:
            stdout, stderr = p.communicate(input="register_read %s" % (register))
            return stdout

def checkIntf( intf ):
    "Make sure intf exists and is not configured."
    quietRun( 'ifconfig %s 0 0.0.0.0 2>/dev/null' % intf, shell=True )
    config = quietRun( 'ifconfig %s 2>/dev/null' % intf, shell=True )
    #config = quietRun( 'ifconfig 2>/dev/null', shell=True )
    print config
    if not config:
        print 'Error:', intf, 'does not exist!\n' 
        exit(1)
    ips = re.findall( r'\d+\.\d+\.\d+\.\d+', config )
    print(ips)
    #~ if ips:
        #~ print 'Error:', intf, 'has an IP address, and is probably in use!\n' 
        #~ exit(1)
        
def checkIntf( intf ):
    "Make sure intf exists and is not configured."
    quietRun( 'ifconfig %s 0 0.0.0.0 2>/dev/null' % intf, shell=True )
    config = quietRun( 'ifconfig %s 2>/dev/null' % intf, shell=True )
    #config = quietRun( 'ifconfig 2>/dev/null', shell=True )
    if not config:
        print 'Error:', intf, 'does not exist!\n' 
        exit(1)
    ips = re.findall( r'\d+\.\d+\.\d+\.\d+', config )
    #~ if ips:
        #~ print 'Error:', intf, 'has an IP address, and is probably in use!\n' 
        #~ exit(1)
        
def create_link_to_external_interface(switch, external_interface_name):
    checkIntf(external_interface_name)
    print  '*** Adding hardware interface', external_interface_name, 'to switch', switch.name, '\n'
    _intf = Intf(external_interface_name, node=switch)

    
def create_dp_cpu_link(switch, cpu_mac, cpu_ip):
    quietRun( 'ip link add name veth_dp type veth peer name veth_cpu', shell=True )
    quietRun( 'ip netns add ns1', shell=True )
    quietRun( 'sudo ip link set veth_cpu netns ns1', shell=True )
    quietRun( 'ip netns exec ns1 ifconfig veth_cpu hw ether %s' % cpu_mac, shell=True )
    quietRun( 'ifconfig veth_dp hw ether f6:61:c0:6a:00:77', shell=True )
    quietRun( 'ip link set dev veth_dp up', shell=True )
    quietRun( 'ip netns exec ns1 ip link set dev veth_cpu up', shell=True )
    for off in "rx tx sg tso ufo gso gro lro rxvlan txvlan rxhash".split(' '):
        quietRun( '/sbin/ethtool --offload veth_dp %s off' % off, shell=True )
        quietRun( 'ip netns exec ns1 /sbin/ethtool --offload veth_cpu %s off' % off, shell=True )
    quietRun( 'ip netns exec ns1 ifconfig veth_cpu %s/24' % cpu_ip, shell=True )
    
    quietRun( 'ip netns exec ns1 ip route add default via %s' % cpu_ip, shell=True )
    quietRun( 'ip netns exec ns1 sysctl -w net.ipv6.conf.all.disable_ipv6=1', shell=True )
    quietRun( 'ip netns exec ns1 sysctl -w net.ipv6.conf.default.disable_ipv6=1', shell=True )
    quietRun( 'ip netns exec ns1 sysctl -w net.ipv6.conf.lo.disable_ipv6=1', shell=True )
    quietRun( 'ip netns exec ns1 sysctl -w net.ipv4.tcp_congestion_control=reno', shell=True )
    
    print  '*** Adding hardware interface', 'veth_dp', 'to switch', switch.name, '\n'
    _intf = Intf('veth_dp', node=switch) 
    
def run_twamp_server():
    os.system('ip netns exec ns1 python3 twamp_server.py')

def start_twamp_server():
    thread = threading.Thread(target=run_twamp_server)
    thread.daemon = True
    thread.start()
        
def main():
    nb_hosts, nb_switches, links = read_topo()
    topo = MyTopo(args.behavioral_exe,
                  args.json,
                  nb_hosts, nb_switches, links)

    net = Mininet(topo = topo,
                  host = P4Host,
                  switch = P4Switch,
                  controller = None,
                  autoStaticArp=True)
    
    create_link_to_external_interface(switch=net.switches[0], external_interface_name='eth1')
    create_dp_cpu_link(switch=net.switches[0], cpu_mac ='f6:61:c0:6a:14:66', cpu_ip='10.0.0.254')

    net.start()

    for n in xrange(nb_hosts):
        h = net.get('h%d' % (n + 1))
        for off in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload eth0 %s off" % off
            print cmd
            h.cmd(cmd)
        print "disable ipv6"
        h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv4.tcp_congestion_control=reno")
        h.cmd("iptables -I OUTPUT -p icmp --icmp-type destination-unreachable -j DROP")

    sleep(1)

    for i in xrange(nb_switches):
        cmd = [args.cli, "--json", args.json,
               "--thrift-port", str(_THRIFT_BASE_PORT + i)
               ]
        with open("commands"+str((i+1))+".txt", "r") as f:
            print " ".join(cmd)
            try:
                output = subprocess.check_output(cmd, stdin = f)
                print output
            except subprocess.CalledProcessError as e:
                print e
                print e.output

        s = net.get('s%d' % (n + 1))
        s.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        s.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        s.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
        s.cmd("sysctl -w net.ipv4.tcp_congestion_control=reno")
        s.cmd("iptables -I OUTPUT -p icmp --icmp-type destination-unreachable -j DROP")

    sleep(1)
    start_twamp_server()
    print "Ready !"

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main()
