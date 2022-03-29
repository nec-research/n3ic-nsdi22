#!/usr/bin/env python3

'''
       N3IC - NSDI 2022

  File:     test_bnn.py
  Authors:  Davide Sanvito (Davide.Sanvito@neclab.eu)
            Giuseppe Siracusano (Giuseppe.Siracusano@neclab.eu)
            Roberto Bifulco (Roberto.Bifulco@neclab.eu)

NEC Laboratories Europe GmbH, Copyright (c) 2022, All rights reserved.

       THIS HEADER MAY NOT BE EXTRACTED OR MODIFIED IN ANY WAY.

       PROPRIETARY INFORMATION ---

SOFTWARE LICENSE AGREEMENT

ACADEMIC OR NON-PROFIT ORGANIZATION NONCOMMERCIAL RESEARCH USE ONLY

BY USING OR DOWNLOADING THE SOFTWARE, YOU ARE AGREEING TO THE TERMS OF THIS
LICENSE AGREEMENT.  IF YOU DO NOT AGREE WITH THESE TERMS, YOU MAY NOT USE OR
DOWNLOAD THE SOFTWARE.

This is a license agreement ("Agreement") between your academic institution
or non-profit organization or self (called "Licensee" or "You" in this
Agreement) and NEC Laboratories Europe GmbH (called "Licensor" in this
Agreement).  All rights not specifically granted to you in this Agreement
are reserved for Licensor.

RESERVATION OF OWNERSHIP AND GRANT OF LICENSE: Licensor retains exclusive
ownership of any copy of the Software (as defined below) licensed under this
Agreement and hereby grants to Licensee a personal, non-exclusive,
non-transferable license to use the Software for noncommercial research
purposes, without the right to sublicense, pursuant to the terms and
conditions of this Agreement. NO EXPRESS OR IMPLIED LICENSES TO ANY OF
LICENSOR'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. As used in this
Agreement, the term "Software" means (i) the actual copy of all or any
portion of code for program routines made accessible to Licensee by Licensor
pursuant to this Agreement, inclusive of backups, updates, and/or merged
copies permitted hereunder or subsequently supplied by Licensor,  including
all or any file structures, programming instructions, user interfaces and
screen formats and sequences as well as any and all documentation and
instructions related to it, and (ii) all or any derivatives and/or
modifications created or made by You to any of the items specified in (i).

CONFIDENTIALITY/PUBLICATIONS: Licensee acknowledges that the Software is
proprietary to Licensor, and as such, Licensee agrees to receive all such
materials and to use the Software only in accordance with the terms of this
Agreement.  Licensee agrees to use reasonable effort to protect the Software
from unauthorized use, reproduction, distribution, or publication. All
publication materials mentioning features or use of this software must
explicitly include an acknowledgement the software was developed by NEC
Laboratories Europe GmbH.

COPYRIGHT: The Software is owned by Licensor.

PERMITTED USES:  The Software may be used for your own noncommercial
internal research purposes. You understand and agree that Licensor is not
obligated to implement any suggestions and/or feedback you might provide
regarding the Software, but to the extent Licensor does so, you are not
entitled to any compensation related thereto.

DERIVATIVES: You may create derivatives of or make modifications to the
Software, however, You agree that all and any such derivatives and
modifications will be owned by Licensor and become a part of the Software
licensed to You under this Agreement.  You may only use such derivatives and
modifications for your own noncommercial internal research purposes, and you
may not otherwise use, distribute or copy such derivatives and modifications
in violation of this Agreement.

BACKUPS:  If Licensee is an organization, it may make that number of copies
of the Software necessary for internal noncommercial use at a single site
within its organization provided that all information appearing in or on the
original labels, including the copyright and trademark notices are copied
onto the labels of the copies.

USES NOT PERMITTED:  You may not distribute, copy or use the Software except
as explicitly permitted herein. Licensee has not been granted any trademark
license as part of this Agreement.  Neither the name of NEC Laboratories
Europe GmbH nor the names of its contributors may be used to endorse or
promote products derived from this Software without specific prior written
permission.

You may not sell, rent, lease, sublicense, lend, time-share or transfer, in
whole or in part, or provide third parties access to prior or present
versions (or any parts thereof) of the Software.

ASSIGNMENT: You may not assign this Agreement or your rights hereunder
without the prior written consent of Licensor. Any attempted assignment
without such consent shall be null and void.

TERM: The term of the license granted by this Agreement is from Licensee's
acceptance of this Agreement by downloading the Software or by using the
Software until terminated as provided below.

The Agreement automatically terminates without notice if you fail to comply
with any provision of this Agreement.  Licensee may terminate this Agreement
by ceasing using the Software.  Upon any termination of this Agreement,
Licensee will delete any and all copies of the Software. You agree that all
provisions which operate to protect the proprietary rights of Licensor shall
remain in force should breach occur and that the obligation of
confidentiality described in this Agreement is binding in perpetuity and, as
such, survives the term of the Agreement.

FEE: Provided Licensee abides completely by the terms and conditions of this
Agreement, there is no fee due to Licensor for Licensee's use of the
Software in accordance with this Agreement.

DISCLAIMER OF WARRANTIES:  THE SOFTWARE IS PROVIDED "AS-IS" WITHOUT WARRANTY
OF ANY KIND INCLUDING ANY WARRANTIES OF PERFORMANCE OR MERCHANTABILITY OR
FITNESS FOR A PARTICULAR USE OR PURPOSE OR OF NON- INFRINGEMENT.  LICENSEE
BEARS ALL RISK RELATING TO QUALITY AND PERFORMANCE OF THE SOFTWARE AND
RELATED MATERIALS.

SUPPORT AND MAINTENANCE: No Software support or training by the Licensor is
provided as part of this Agreement.

EXCLUSIVE REMEDY AND LIMITATION OF LIABILITY: To the maximum extent
permitted under applicable law, Licensor shall not be liable for direct,
indirect, special, incidental, or consequential damages or lost profits
related to Licensee's use of and/or inability to use the Software, even if
Licensor is advised of the possibility of such damage.

EXPORT REGULATION: Licensee agrees to comply with any and all applicable
export control laws, regulations, and/or other laws related to embargoes and
sanction programs administered by law.

SEVERABILITY: If any provision(s) of this Agreement shall be held to be
invalid, illegal, or unenforceable by a court or other tribunal of competent
jurisdiction, the validity, legality and enforceability of the remaining
provisions shall not in any way be affected or impaired thereby.

NO IMPLIED WAIVERS: No failure or delay by Licensor in enforcing any right
or remedy under this Agreement shall be construed as a waiver of any future
or other exercise of such right or remedy by Licensor.

GOVERNING LAW: This Agreement shall be construed and enforced in accordance
with the laws of Germany without reference to conflict of laws principles.
You consent to the personal jurisdiction of the courts of this country and
waive their rights to venue outside of Germany.

ENTIRE AGREEMENT AND AMENDMENTS: This Agreement constitutes the sole and
entire agreement between Licensee and Licensor as to the matter set forth
herein and supersedes any previous agreements, understandings, and
arrangements between the parties relating hereto.

       THIS HEADER MAY NOT BE EXTRACTED OR MODIFIED IN ANY WAY.
'''

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
