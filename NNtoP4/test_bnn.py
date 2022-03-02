#!/usr/bin/env python3

from scapy.all import sendp, send, srp1, sniff
from scapy.all import Packet, hexdump, binrepr
from scapy.all import Ether, IP, IntField
from scapy.all import bind_layers

from nn_utils import MLP
import struct
import socket
import time
from threading import Thread
import argparse

class BNN_pkt(Packet):
    name = "BNN_pkt"
    fields_desc = [ IntField("x", 0x00)]


bind_layers(Ether, BNN_pkt, type=0x2323)
bind_layers(Ether, IP, type=0x800)

def weights(nn_desc):
    # 32x32 layers
    w1 = "0x76ced201 0xc12e8fcd 0xf28a043b 0xb6794bea 0x2f4a4018 0x89ea24ea 0xfc615308 0x1622052f 0x739db96 0x3f6100ed 0x9b304f19 0x460623a1 0xd21478d 0x4d14d0b 0xcae57470 0x8c3f42 0xa364d18 0x3560ffb6 0x70ce8213 0xb3382e2f 0x280379c1 0xc85f445b 0x9ef2184 0x9412630d 0x1ef7d6f1 0x9e4d997f 0x6e598c54 0xd6c57dea 0x29d1af7e 0xb0dae2c9 0x310d4941 0xec6aa1db"
    w1 = list(map(eval, w1.split()))
    w2 = "0x2b1939f6 0xdb2501f6 0xaa3a895f 0x1ca0e969 0x99a43cde 0xd0cad442 0xeacdfd01 0x35a170fa 0x435a9cb8 0x10606d4a 0xd0269cd3 0x41e8174d 0x9a91a923 0x93a1161d 0xc6b580b7 0xc967049 0xd1f518eb 0x20553b50 0x27efdab3 0x98485a1c 0x2370fe70 0x14e2c158 0x6e0f238f 0xf942a305 0xf50d4088 0x212b2db4 0x9bcf06d8 0x50b36bf1 0xe62403f7 0xb59e59f 0x16eebedc 0xfbd9a663"
    w2 = list(map(eval, w2.split()))
    w3 = "0x1680d952 0x1ab08c42 0xa9b1c67f 0x337c40e3 0x15a07afe 0x6b8d5534 0x8805de23 0x20469baf 0x3f9c28b7 0x83899d82 0x323566b4 0xcef168c0 0x9ef1724a 0x8bb0f056 0xa743bb41 0x28b9fc77 0xc9eccaf7 0x85b1dbe3 0x86747c76 0xbd9f8977 0x9b945aa6 0x11c96e82 0xac054462 0x33d1efbf 0xf2860164 0x9487593f 0x26a3116a 0xa6d3096d 0x71808ef3 0x1b55d542 0x448cc470 0x2c95db63"
    w3 = list(map(eval, w3.split()))

    # 8x8 layer
    w4 = "0xa0 0xb1 0xc2 0xd3 0xe4 0xf5 0x06 0x17"
    w4 = list(map(eval, w4.split()))

    # 8x32 layer
    w5 = "0x00 0x01 0x02 0x03 0x00 0x01 0x02 0x03 0x00 0x01 0x02 0x03 0x00 0x01 0x02 0x03 0x00 0x01 0x02 0x03 0x00 0x01 0x02 0x03 0x00 0x01 0x02 0x03 0x00 0x01 0x02 0x03"
    w5 = list(map(eval, w5.split()))

    # 32x8 layer
    w6 = "0x2b1939f6 0xdb2501f6 0xaa3a895f 0x1ca0e969 0x99a43cde 0xd0cad442 0xeacdfd01 0x35a170fa"
    w6 = list(map(eval, w6.split()))

    if nn_desc == [32, 32, 32, 32]:
        weights = [w1, w2, w3]
    elif nn_desc == [32, 32, 32]:
        weights = [w1, w2]
    elif nn_desc == [32, 32]:
        weights = [w1]
    elif nn_desc == [8, 8, 8]:
        weights = [w4, w4]
    elif nn_desc == [8, 8]:
        weights = [w4]
    elif nn_desc == [8, 32, 8]:
        weights = [w5, w6]
    elif nn_desc == [32, 8, 32]:
        weights = [w6, w5]
    elif nn_desc == [32, 8]:
        weights = [w6]
    elif nn_desc == [8, 32]:
        weights = [w5]
    else:
        print(yellow_str('The test packet has been sent, but the result cannot be verified because the NN weights for the %s network configuration are unknown!' % nn_desc))
        exit()

    return weights

def red_str(s):
    return '\x1b[6;30;31m%s\x1b[0m' % s

def green_str(s):
    return '\x1b[6;30;32m%s\x1b[0m' % s

def yellow_str(s):
    return '\x1b[6;30;33m%s\x1b[0m' % s

def print_bin_hex_dec(value, nn_desc):
    print(yellow_str('0b') + format(value, '#0%db' % (nn_desc[0] + 2))[2:], yellow_str('0x') + hex(value)[2:], value)

def main():
    iface = 'veth0_b'
    src = '00:00:00:00:00:0a'
    dst = '00:00:00:00:00:0b'

    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--nn_desc', help='NN description', required=True)
    parser.add_argument('-f','--header_field', help='packet header field', choices=['bnn', 'ipv4_src'], required=True)
    parser.add_argument('-i','--nn_input', help='NN input', required=True)
    args = parser.parse_args()

    nn_desc = list(map(int, args.nn_desc.split(',')))
    if len(nn_desc) < 2:
        print('The NN must have at least 1 layer!')
        exit()

    if args.header_field == 'bnn':
        nn_input = int(args.nn_input,16)
    else:
        nn_input = args.nn_input

    if args.header_field == 'ipv4_src':
        nn_input = struct.unpack("!I", socket.inet_aton(args.nn_input))[0]
    if nn_input >= 2 ** nn_desc[0]:
        nn_input = nn_input % (2 ** nn_desc[0])
        print(red_str('WARNING: BNN input has been truncated to the %d LSB!' % nn_desc[0]))
        if args.header_field == 'bnn':
            print(red_str('%d' % nn_input + '\x1b[0m'))
        else:
            print(red_str('%s' % socket.inet_ntoa(struct.pack('!I', nn_input)) + ' (%d) \x1b[0m' % nn_input))

    if args.header_field == 'bnn':
        pkt = Ether(src=src, dst=dst,type=0x2323)/BNN_pkt(x=nn_input)
    else:
        pkt = Ether(src=src, dst=dst,type=0x800)/IP(src=socket.inet_ntoa(struct.pack('!I', nn_input)))

    print(green_str('Sending packet...'))
    pkt.show()
    if args.header_field == 'bnn':
        print("BNN input: BNN_pkt.x header field")
    else:
        print("BNN input: IPv4.src header field")
    value = nn_input
    print_bin_hex_dec(value, nn_desc)
    print()

    if args.header_field == 'bnn':
        resp = srp1(pkt, iface=iface)
    else:
        def threaded_send(pkt):
             time.sleep(1)
             sendp(pkt, iface=iface)
        Thread(target = threaded_send, args = (pkt,)).start()
        resp = sniff(iface=iface, count=2)[1]
    if resp:
        print(green_str('...got reply packet!'))
        resp.show()
    else:
        print(red_str('...no reply packet received!'))
        exit()

    nn_weights = weights(nn_desc)

    mlp = MLP(nn_desc[0], nn_desc[1:-1], nn_desc[-1])
    exp_output = mlp.do_inference(nn_input, nn_weights, verbose=False)
    rx_output = resp[BNN_pkt].x if args.header_field == 'bnn' else struct.unpack("!I", socket.inet_aton(resp[IP].dst))[0]

    # keeping just the "NN_output_size" LSB
    exp_output = exp_output % 2**nn_desc[-1]
    rx_output = rx_output % 2**nn_desc[-1]

    print()
    print('Expected:')
    print_bin_hex_dec(exp_output, nn_desc)
    print('Got:')
    print_bin_hex_dec(rx_output, nn_desc)
    if exp_output == rx_output:
        print(green_str('Success!'))
    else:
        print(red_str('Fail!'))

if __name__ == '__main__':
    main()
