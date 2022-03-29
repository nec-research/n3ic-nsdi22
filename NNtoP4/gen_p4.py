#!/usr/bin/python3

'''
       N3IC - NSDI 2022

  File:     gen_p4.py
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

import argparse
import fileinput
import math
from shutil import copyfile

class FcLayer:

    def __init__(self, layer_size, layer_id, output_size, next_out_size):

        self.layer_size = layer_size
        self.layer_id = layer_id
        self.output_size = output_size
        self.p4code = ''
        self.next_out_size = next_out_size

    def gen_fold(self):
        s = '\taction l%d_fold(){\n' % self.layer_id
        for w in range(self.output_size):
            s += '\t\tmeta.meta%d_%d.x1_0[%d:%d] = meta.meta%d_%d.x%d_0[0:0];\n' %(self.output_size, self.next_out_size, self.output_size-w-1, self.output_size-w-1, self.layer_size, self.output_size, w+1 )
        s += '\t}\n\n'
        return s

    def gen_l_xor_table(self):
        s = '\ttable l%d_xor_table {\n' %(self.layer_id)
        s += '\t\tactions = { xor_%d_%d; NoAction; } \n\t\tdefault_action = NoAction();\n\t}\n\n' % (self.layer_size, self.output_size)

        return s

    def gen_l_popcount(self):
        s = ''

        s += '\taction l%d_popcount(){\n' % (self.layer_id)

        for i in range(int(math.log(self.layer_size,2))):
            s += '\t\tcpy_%d_%d();\n' % (self.layer_size, self.output_size)
            s += '\t\tstep_pop_%d_%d(m%d_%d,%d);\n' % (self.layer_size, self.output_size,2**i ,self.layer_size, 2**i)
            s += '\t\tsum_%d_%d();\n' %(self.layer_size, self.output_size)

        s += '\t\tsign_%d_%d();\n' % (self.layer_size, self.output_size)
        s += '\t\tl%d_fold();\n' % (self.layer_id)
        s += '\t\tmcpy_%d_%d();\n' % (self.output_size, self.next_out_size)
        s += '\t}\n\n'

        return s

    def gen_l_popcount_table(self):
        s = '\ttable l%d_popcount_table {\n' %(self.layer_id)
        s += '\t\tactions = { l%d_popcount; } \n\t\tdefault_action = l%d_popcount();\n\t}\n\n' % (self.layer_id, self.layer_id)
        return s


class MLP:

    # TODO net_desc=hidden_layers_neurons, output_size=last_layer_neurons
    def __init__(self, input_size, net_desc, output_size, template, outname):

        self.POP_CONST  = '==POP_CONST=='
        self.BNN_META_T = '==BNN_META_T=='
        self.BNN_ACT    = '==BNN_ACT=='
        self.BNN_NN_IN  = '==BNN_NN_IN=='
        self.BNN_NN_OUT = '==BNN_NN_OUT=='
        self.BNN_TAB    = '==BNN_TAB=='
        self.BNN_APPLY  = '==BNN_APPLY=='

        self.template = template
        self.input_size = input_size
        self.output_size = output_size
        self.net_desc = net_desc
        self.p4code = ''
        self.layers = []
        self.outname = outname
        self.sizes = [input_size] + net_desc + [output_size]
        self.size_pairs = list(zip(self.sizes, self.sizes[1:]))
        self.meta_sizes_pairs = set()
        for pair in self.size_pairs:
            self.meta_sizes_pairs.add(tuple(pair))
        self.meta_sizes_pairs.add((output_size, output_size))
        self.meta_sizes_pairs = list(self.meta_sizes_pairs)

        assert self.input_size in [8, 16, 32, 64], 'Input size not supported'
        assert self.output_size in [8, 16, 32, 64], 'Output size not supported'
        for l in self.net_desc:
            assert l in [8, 16, 32, 64], 'Layer size not supported'
        assert max([input_size, output_size] + net_desc) <= 64, 'Popcount for layer size > 64 is not implemented'

        copyfile(template, outname)

        # const

        self.p4code += self.gen_step_pop_const()
        self.add_to_template(self.POP_CONST, self.gen_step_pop_const())

        # meta

        self.p4code += self.gen_meta_hdr()
        self.add_to_template(self.BNN_META_T, self.gen_meta_hdr())

        # action

        actions = ''
        actions += self.gen_xor()
        actions += self.gen_step_pop()
        actions += self.gen_sum()
        actions += self.gen_sign()
        actions += self.gen_cpy()
        actions += self.gen_mcpy()

        self.p4code += self.gen_xor()
        self.p4code += self.gen_step_pop()
        self.p4code += self.gen_sum()
        self.p4code += self.gen_sign()
        self.p4code += self.gen_cpy()
        self.p4code += self.gen_mcpy()

        # create layers

        if len(self.net_desc) > 0:
            self.layers.append(FcLayer(self.input_size, 1, self.net_desc[0], self.sizes[2]))
            for layer_id, (layer_size, output_size) in enumerate(zip(self.net_desc, self.net_desc[1:])):
                self.layers.append(FcLayer(layer_size, layer_id + 2, output_size, self.sizes[layer_id + 3]))
            self.layers.append(FcLayer(self.net_desc[-1], len(self.net_desc) + 1, self.output_size, self.output_size))
        else:
            self.layers.append(FcLayer(self.input_size, 1, self.output_size, self.output_size))

        # per layer action

        for l in self.layers:
            actions += l.gen_fold()
            actions += l.gen_l_popcount()
            self.p4code += l.gen_fold()
            self.p4code += l.gen_l_popcount()

        self.add_to_template(self.BNN_ACT, actions)

        # user actions

        code = self.gen_get_nn_input()
        self.p4code += code
        self.add_to_template(self.BNN_NN_IN, code)
        code = self.gen_get_nn_output()
        self.p4code += code
        self.add_to_template(self.BNN_NN_OUT, code)

        # per layer tables

        tables = ''

        for l in self.layers:
            tables += l.gen_l_xor_table()
            tables += l.gen_l_popcount_table()
            self.p4code += l.gen_l_xor_table()
            self.p4code += l.gen_l_popcount_table()

        self.add_to_template(self.BNN_TAB, tables)

        # apply block

        self.p4code += self.gen_mpl_apply_list()
        self.add_to_template(self.BNN_APPLY,self.gen_mpl_apply_list())

    def add_to_template(self, placeholder, code):
        with fileinput.FileInput(self.outname, inplace=True) as file:
            for line in file:
                print(line.replace(placeholder, code), end='')

    def gen_meta_hdr(self):
        s = ''
        # gen metadata fields for each layer size in nn
        for inp,out in self.meta_sizes_pairs:
            s += 'struct meta%d_%d_t {\n' % (inp,out)
            for i in range(1, out + 1):
                s += '\tbit<%d> x%d_0;\n' % (inp, i)
                s += '\tbit<%d> x%d_1;\n' % (inp, i)
            s += '}\n\n'
        s += 'struct metadata {\n'

        for inp,out in self.meta_sizes_pairs:
            s += '\tmeta%d_%d_t meta%d_%d;\n' % (inp, out, inp, out)

        s += '}\n\n'
        return s

    def gen_step_pop_const(self):
        s = ''

        for size in sorted(list(set([self.input_size, self.output_size] + self.net_desc))):

           if (size == 8):
                s += 'const bit<8> m1_8 = 0x55;\n'
                s += 'const bit<8> m2_8 = 0x33;\n'
                s += 'const bit<8> m4_8 = 0x0f;\n'
           elif (size == 16):
                s += 'const bit<16> m1_16 = 0x5555;\n'
                s += 'const bit<16> m2_16 = 0x3333;\n'
                s += 'const bit<16> m4_16 = 0x0f0f;\n'
                s += 'const bit<16> m8_16 = 0x00ff;\n'
           elif (size == 32):
                s += 'const bit<32> m1_32 = 0x55555555;\n'
                s += 'const bit<32> m2_32 = 0x33333333;\n'
                s += 'const bit<32> m4_32 = 0x0f0f0f0f;\n'
                s += 'const bit<32> m8_32 = 0x00ff00ff;\n'
                s += 'const bit<32> m16_32 = 0x0000ffff;\n'
           elif (size == 64):
                s += 'const bit<64> m1_64 = 0x5555555555555555;\n'
                s += 'const bit<64> m2_64 = 0x3333333333333333;\n'
                s += 'const bit<64> m4_64 = 0x0f0f0f0f0f0f0f0f;\n'
                s += 'const bit<64> m8_64 = 0x00ff00ff00ff00ff;\n'
                s += 'const bit<64> m16_64 = 0x0000ffff0000ffff;\n'
                s += 'const bit<64> m32_64 = 0x00000000ffffffff;\n'

           s += '\n'
        return s

    def gen_step_pop(self):
        s = ''

        for inp,out in self.meta_sizes_pairs:
            s += '\taction step_pop_%d_%d(bit<%d> m, bit<8> s){\n' % (inp, out, inp)

            for i in range(1, out + 1):
                s += '\t\tmeta.meta%d_%d.x%d_0 = (meta.meta%d_%d.x%d_0 & m);\n' % (inp, out, i, inp, out, i)
                s += '\t\tmeta.meta%d_%d.x%d_1 = ((meta.meta%d_%d.x%d_1 >> s) & m);\n' % (inp, out, i, inp, out, i)

            s += '\t}\n\n'

        return s

    def gen_xor(self):
        s = ''

        for inp,out in self.meta_sizes_pairs:
            s += '\taction xor_%d_%d(' % (inp, out)
            s += ', '.join(['bit<%d> w_%d' % (inp, w) for w in range(1, out+1)])
            s += '){\n'
            for w in range(1, out+1):
                s += '\t\tmeta.meta%d_%d.x%d_0 = (meta.meta%d_%d.x%d_0 ^ w_%d);\n' %(inp, out, w, inp, out, w, w)
            s += '\t}\n\n'
        return s

    def gen_cpy(self):
        s = ''

        for inp,out in self.meta_sizes_pairs:
            s += '\taction cpy_%d_%d(){\n' % (inp, out)

            for i in range(1, out + 1):
                s += '\t\tmeta.meta%d_%d.x%d_1 = meta.meta%d_%d.x%d_0;\n' % (inp, out, i, inp, out, i)
            s += '\t}\n\n'

        return s

    def gen_mcpy(self):
        s = ''

        for inp,out in self.meta_sizes_pairs:
            s += '\taction mcpy_%d_%d(){\n' % (inp, out)

            for i in range(1, out + 1):
                if i > 1:
                    s += '\t\tmeta.meta%d_%d.x%d_0 = meta.meta%d_%d.x1_0;\n' % (inp, out, i, inp, out)
                s += '\t\tmeta.meta%d_%d.x%d_1 = meta.meta%d_%d.x1_0;\n' % (inp, out, i, inp, out)
            s += '\t}\n\n'

        return s

    def gen_sum(self):
        s = ''

        for inp,out in self.meta_sizes_pairs:
            s += '\taction sum_%d_%d(){\n' % (inp, out)

            for i in range(1, out + 1):
                s += '\t\tmeta.meta%d_%d.x%d_0 = (meta.meta%d_%d.x%d_0 + meta.meta%d_%d.x%d_1);\n' % (inp, out, i, inp, out, i, inp, out, i)
            s += '\t}\n\n'

        return s

    def gen_sign(self):
        s = ''

        for inp,out in self.meta_sizes_pairs:
            s += '\taction sign_%d_%d(){\n' % (inp, out)

            for i in range(1, out + 1):
                s += '\t\tif (meta.meta%d_%d.x%d_0 >= %d) \n\t\t\tmeta.meta%d_%d.x%d_0 = 0;\n' % (inp, out, i, inp/2, inp, out, i)
                s += '\t\telse \n\t\t\tmeta.meta%d_%d.x%d_0 = 1;\n' % (inp, out, i)

            s += '\t}\n\n'

        return s

    def gen_mpl_apply_list(self):
        s = ''

        for l in self.layers:
            s += '\t\tl%d_xor_table.apply();\n' % l.layer_id
            s += '\t\tl%d_popcount_table.apply();\n' % l.layer_id

        return s

    def gen_sign(self):
        s = ''

        for inp,out in self.meta_sizes_pairs:
            s += '\taction sign_%d_%d(){\n' % (inp, out)

            for i in range(1, out + 1):
                s += '\t\tif (meta.meta%d_%d.x%d_0 >= %d) \n\t\t\tmeta.meta%d_%d.x%d_0 = 0;\n' % (inp, out, i, inp/2, inp, out, i)
                s += '\t\telse \n\t\t\tmeta.meta%d_%d.x%d_0 = 1;\n' % (inp, out, i)

            s += '\t}\n\n'

        return s

    def gen_get_nn_input(self):
        s = ''

        header = 'hdr.bnn_pkt.x' if self.template == 'tmpl_bnn.p4' else 'hdr.ipv4.srcAddr'
        inp, out = self.size_pairs[0]
        s += '\taction get_nn_input(){\n'
        s += '\t\t//Here we can select the input features vector from packet header.\n'
        reply = ''
        while reply not in ['>', '<', '=']:
            reply = input('The \033[1mNN input\033[0m header field is ... than %d bits. [>,<,=]? ' % inp)[:1]
        if reply == '>':
            s += '\t\tmeta.meta%d_%d.x1_0 = %s[%d:0];\n\n' % (inp, out, header, inp-1)
        elif reply == '<':
            s += '\t\tmeta.meta%d_%d.x1_0[%d:0] = %s;\n\n' % (inp, out, inp-1, header)
        else:
            s += '\t\tmeta.meta%d_%d.x1_0 = %s;\n\n' % (inp, out, header)
        s += '\t\t//copy meta.meta%d_%d.x1_0 into meta.meta%d_%d.x**_0 and meta.meta%d_%d.x**_1\n' % (inp, out, inp, out, inp, out)
        s += '\t\tmcpy_%d_%d();\n' % (inp, out)
        s += '\t}\n\n'

        return s

    def gen_get_nn_output(self):
        s = ''

        header = 'hdr.bnn_pkt.x' if self.template == 'tmpl_bnn.p4' else 'hdr.ipv4.srcAddr'
        inp, out = self.size_pairs[-1]
        s += '\taction get_nn_output(){\n'
        s += '\t\t//Here we can select the destination packet header\n'
        reply = ''
        while reply not in ['>', '<', '=']:
            reply = input('The \033[1mNN output\033[0m header field is ... than %d bits. [>,<,=]? ' % out)[:1]
        if reply == '>':
            s += '\t\t%s[%d:0] = meta.meta%d_%d.x1_0;\n' % (header, out-1, out, out)
        elif reply == '<':
            s += '\t\t%s = meta.meta%d_%d.x1_0[%d:0];\n' % (header, out, out, out-1)
        else:
            s += '\t\t%s = meta.meta%d_%d.x1_0;\n' % (header, out, out)
        s += '\t}\n\n'

        return s

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--nn_desc', help='NN description (comma-separated list of number of neurons)', required=True)
    parser.add_argument('-t','--template', help='p4 template file (e.g. tmpl_bnn.p4 or tmpl_ipv4_src.p4)', required=True)
    parser.add_argument('-o','--out_file', help='p4 output file', required=False)
    args = parser.parse_args()

    nn_desc = list(map(int,args.nn_desc.split(',')))
    if len(nn_desc) < 2:
        print('The NN must have at least 2 layer (including the input)!')
        exit()

    if args.out_file is not None:
        pass
    else:
        out_file = 'out.p4'

    mlp = MLP(nn_desc[0], nn_desc[1:-1], nn_desc[-1], args.template, out_file)
    #print(mlp.p4code)
    print('%s file has been generated' % out_file)

if __name__ == '__main__':
    main()
