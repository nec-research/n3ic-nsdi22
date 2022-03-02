#!/usr/bin/env python3

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
