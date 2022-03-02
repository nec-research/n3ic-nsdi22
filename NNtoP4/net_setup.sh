#!/bin/bash

add(){
	ip link add veth0_a type veth peer name veth0_b
	ip l s dev veth0_a address 00:00:00:00:00:0a
	ip l s dev veth0_b address 00:00:00:00:00:0b
	ip l s veth0_a up
	ip l s veth0_b up

	TOE_OPTIONS="rx tx sg tso ufo gso gro lro rxvlan txvlan rxhash"
	/sbin/ethtool --offload veth0_a "$TOE_OPTION" off
	/sbin/ethtool --offload veth0_b "$TOE_OPTION" off
	sysctl net.ipv6.conf.veth0_a.disable_ipv6=1
	sysctl net.ipv6.conf.veth0_b.disable_ipv6=1
}

del() {
	ip l d veth0_a
	ip l d veth1_b
}

$1
