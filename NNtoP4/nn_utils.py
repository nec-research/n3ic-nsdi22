#!/usr/bin/env python3

'''
       N3IC - NSDI 2022

  File:     nn_utils.py
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

class FcLayer:
    def __init__(self, input_size, output_size, layer_id):
        self.input_size = input_size
        self.output_size = output_size
        self.layer_id = layer_id

class MLP:
    def __init__(self, input_layer_size, hidden_layers_sizes, output_layer_size):
        self.input_layer_size = input_layer_size
        self.output_layer_size = output_layer_size
        self.hidden_layers_sizes = hidden_layers_sizes

        self.layers = []
        self.sizes = [input_layer_size] + hidden_layers_sizes + [output_layer_size]

        assert self.input_layer_size in [8, 16, 32, 64], 'Input size not supported'
        assert self.output_layer_size in [8, 16, 32, 64], 'Output size not supported'
        for l in self.hidden_layers_sizes:
            assert l in [8, 16, 32, 64], 'Layer size not supported'

        assert max([input_layer_size, output_layer_size] + hidden_layers_sizes) <= 64, 'Popcount for layer size > 64 is not implemented'

        if len(self.hidden_layers_sizes) > 0:
            self.layers.append(FcLayer(self.input_layer_size, self.hidden_layers_sizes[0], 1))
            for layer_id, (layer_size, output_layer_size) in enumerate(zip(self.hidden_layers_sizes, self.hidden_layers_sizes[1:])):
                self.layers.append(FcLayer(layer_size, output_layer_size, layer_id + 2))
            self.layers.append(FcLayer(self.hidden_layers_sizes[-1], self.output_layer_size, len(self.hidden_layers_sizes) + 1))
        else:
            self.layers.append(FcLayer(self.input_layer_size, self.output_layer_size, 1))

    def popcount(self, x):
        return bin(x).count('1')

    def sign(self, x, n):
        if x >= n/2:
            return 0
        else:
            return 1

    def binary_str(self, n, zero_pad_size):
        return format(n, '#0%db' % (zero_pad_size + 2))

    def do_layer(self, input_data, weights, layer, reverse_output=False, verbose=False):
        if verbose:
            print('\033[1mL%d input_data\033[0m' % layer.layer_id, self.binary_str(input_data, layer.input_size))
            print('\033[1mWeights\033[0m  ', ','.join(map(lambda x: self.binary_str(x, layer.input_size), weights)))
        h = [input_data^w_ for w_ in weights]
        if verbose:
            print('\033[1mAfter XOR\033[0m', ','.join(map(lambda x: self.binary_str(x, layer.input_size), h)))
            print('\033[1mAfter popcount\033[0m', [self.popcount(h_) for h_ in h])
        y = [self.sign(self.popcount(h_), layer.input_size) for h_ in h]
        if verbose:
            print('\033[1mAfter sign\033[0m', y)
        binary_list = list(map(str, y))

        if reverse_output:
            binary_list = binary_list[::-1]

        folded_value = eval('0b'+''.join(binary_list))
        if verbose:
            print('\033[1mAfter folding\033[0m', self.binary_str(folded_value, layer.output_size), '(%d)' % folded_value)

        return eval('0b'+''.join(binary_list))

    def do_inference(self, input_data, weights, verbose=False):
        x = input_data
        for layer_idx, layer in enumerate(self.layers):
            x = self.do_layer(x, weights[layer_idx], layer, verbose=verbose)
            if verbose:
                if layer_idx != len(self.layers)-1:
                    print('-'*80)
                else:
                    print('\n'+'='*80+'\n')
        return x
