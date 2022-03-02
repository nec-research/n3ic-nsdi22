#!/usr/bin/python3

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
