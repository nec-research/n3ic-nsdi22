# Requirements (tested on Ubuntu 20.04.3 LTS)

```
sudo apt update
sudo apt install -y python3-pip curl
pip install scapy
```

Install BMv2 (https://github.com/p4lang/behavioral-model)
```
git clone https://github.com/p4lang/behavioral-model.git
cd behavioral-model
./install_deps.sh
./autogen.sh
./configure
make
sudo make install
```

Install P4 compiler (https://github.com/p4lang/p4c)
```
. /etc/os-release
echo "deb http://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${VERSION_ID}/ /" | sudo tee /etc/apt/sources.list.d/home:p4lang.list
curl -L "http://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${VERSION_ID}/Release.key" | sudo apt-key add -
sudo apt-get update
sudo apt install -y p4lang-p4c

```

# gen_p4.py

This script generates a p4_16 program for the execution of a Binarized Neural
Network (BNN), on a bmv2 target. When the switch receives a packet that contains
a BNN input, it reads the input value from a packet header field, performs the
network execution and writes back to a packet header field the result of the s
computation. The packet is then forwarded according to the switch configuration.

To combine the BNN processing with regular switch operations, the user of this
script should provide a P4_16 program template, which contains all the
statements for the networking pipeline description and a set of custom
annotations that are interpreted to introduce the handling of BNNs.

We provide two template examples.

In a first example, contained in `tmpl_bnn.p4`, a BNN packet is an ethernet
packet with `ETH_TYPE` 0x2323 followed by a 32b custom header.
```
xx:xx:xx:xx:xx:xx || xx:xx:xx:xx:xx:xx ||  0x2323  || 0xXXXXXXXX
     MAC_DST              MAC_SRC         ETH_TYPE        BNN
```
The switch executes the network as soon as the packet is received, and provides
the result by forwarding back the packet to the sender. The packet has the
MAC addresses swapped, so that the sender can receive it, and the result of the
network inference written in the BNN field.

The second example, contained in `tmpl_ipv4_src.p4`, encodes in the IPv4 source
address the BNN input. The reply packet coming out from the switch has both
the MAC and IP addresses swapped, with the IPv4 destination address rewritten
to contain the inference result. I.e., the IPv4 destination address is used
in place of the custom BNN header in this case.


The BNN description is provided as a comma-separated list of number of neurons.
The numbers represent the ordered number of neurons of the BNN.

For example the command
```
./gen_p4.py -n 32,8,32 -t tmpl_bnn.p4
```
generates a P4
program that implements a BNN with an input layer of 32 neurons, a hidden layer
of 8 neurons and an output layers of 32 neurons, whose input/output is
read/written from/to the custom BNN header field.

If not specified otherwise, the script generates the p4 code in the `out.p4` file.

```
usage: gen_p4.py [-h] -n NN_DESC -t TEMPLATE [-o OUT_FILE]

optional arguments:
  -h, --help            show this help message and exit
  -n NN_DESC, --nn_desc NN_DESC
                        NN description (comma-separated list of number of
                        neurons)
  -t TEMPLATE, --template TEMPLATE
                        p4 template file (e.g. tmpl_bnn.p4 or
                        tmpl_ipv4_src.p4)
  -o OUT_FILE, --out_file OUT_FILE
                        p4 output file
```

# test_bnn.py

This script generates a packet with the NN input specified by the user, sends it
to the switch and verifies if the NN output read from the reply packet is
correct.

To verify the output of the NN, the user has to specify the set of weights in
the `weights()` method of `test_bnn.py` and provide the proper txt file to configure
the flow entries (examples can be found in the `cmd_txt` folder).

```
usage: test_bnn.py [-h] -n NN_DESC -f {bnn,ipv4_src} -i NN_INPUT

optional arguments:
  -h, --help            show this help message and exit
  -n NN_DESC, --nn_desc NN_DESC
                        NN description
  -f {bnn,ipv4_src}, --header_field {bnn,ipv4_src}
                        packet header field
  -i NN_INPUT, --nn_input NN_INPUT
                        NN input
```

Before running the two examples below, once after each boot, the following command
is required to configure the virtual ethernet interfaces.
```
sudo ./net_setup.sh add
```

## Example 1

Generate the P4 code
```
./gen_p4.py -n 32,8,32 -t tmpl_bnn.p4
```

Notice: to support the encoding of a BNN input in a header field that is larger
than the actual BNN input, or to encode only a portion of the results in the
output field, the script asks if the size of the input/output header field is
bigger/smaller/equal than the input/output size of the BNN. This generates
the proper slicing when reading/writing from/to the header fields.
The second example provides a clarifying case of this.

In this first example, you should type `=` twice, since no slicing is needed.

Further custom pre/post processing can be added by modifying `get_nn_input()`
and `get_nn_output()` actions from the generated `out.p4` file.
The output of the BNN can be written to a different header field,
but the `test_bnn.py` script would not able to verify the results.

Run the bmv2 switch and load the `out.p4` code with
```
sudo ./run_p4.sh out
```

From a second terminal, load the flow entries with the BNN weights
```
sudo simple_switch_CLI < cmd_txt/cmd_32_8_32_bnn.txt
```

Create a test packet and verify the BNN computation
```
sudo ./test_bnn.py -n 32,8,32 -f bnn -i 0x8000
```

When using BNN header field, the NN input has to be specified as a
hexadecimal number.
When using IPv4 source address, the NN input has to be specified with
dot-decimal notation.

NB: the input/output is automatically truncated to match the
BNN input/output (and the user is warned about it!)

## Example 2

Generate the P4 code
```
./gen_p4.py -n 8,8,8 -t tmpl_ipv4_src.p4
```

Since the IPv4 address is bigger (32 bits) than the
BNN input and output (8 bits) you have to reply twice with `>`.

In this way the generated p4 file already read/write from the 8
LSB of the IPv4 address.
The user can customize the slicing by manually editing the generated p4 file.

Run the bmv2 switch and load the `out.p4` code with
```
sudo ./run_p4.sh out
```

From a second terminal, load the flow entries with the BNN weights
```
sudo simple_switch_CLI < cmd_txt/cmd_8_8_8_bnn.txt
```

Create a test packet and verify the BNN computation
```
sudo ./test_bnn.py -n 8,8,8 -f ipv4_src -i 128.0.0.0
```
