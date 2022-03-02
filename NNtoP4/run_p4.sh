#! /bin/bash

rm $1.json
p4c-bm2-ss -o $1.json $1.p4
simple_switch --log-console --dump-packet-data 64 -i 0@veth0_a $1.json
