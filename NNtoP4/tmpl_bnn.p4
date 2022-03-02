/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*
 * Standard ethernet header
 */
header ethernet_t {
	bit<48> dstAddr;
	bit<48> srcAddr;
	bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}


const bit<48> MAC_SND       = 0x00000000000a;
const bit<16> BNN_PKT_ETYPE = 0x2323;

==POP_CONST==

/*
 * BNN packet
 */

header bnn_pkt_t {
	bit<32> x;
}


/*
 * All headers must be assembled in a signle struct, no need to be instanctiated
 */
struct my_headers_t {
	ethernet_t ethernet;
	ipv4_t ipv4;
	bnn_pkt_t bnn_pkt;
}

==BNN_META_T==


/*************************************************************************
 ***********************  P A R S E R  ***********************************
 *************************************************************************/

parser MyParser(
	packet_in packet,
	out my_headers_t hdr,
	inout metadata meta,
	inout standard_metadata_t standard_metadata)
{
	state start {
		packet.extract(hdr.ethernet);
		transition select(hdr.ethernet.etherType) {
			0x800: parse_ipv4;
			BNN_PKT_ETYPE : bnn_found;
			default       : accept;
		}
	}

	state bnn_found {
		packet.extract(hdr.bnn_pkt);
		transition accept;
	}

	state parse_ipv4 {
        packet.extract(hdr.ipv4);
		transition accept;
	}
}

/*************************************************************************
 ************   C H E C K S U M    V E R I F I C A T I O N   *************
 *************************************************************************/

control MyVerifyChecksum(
	inout  my_headers_t   hdr,
	inout metadata meta)
{
	apply { }
}
/*************************************************************************
 **************  I N G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

control MyIngress(
	inout my_headers_t     hdr,
	inout metadata meta,
	inout standard_metadata_t standard_metadata)
{
	action _drop() {
		mark_to_drop(standard_metadata);
	}

	action send_back() {
		bit<48> tmp;
		/* Swap the MAC addresses */
		tmp = hdr.ethernet.dstAddr;
		hdr.ethernet.dstAddr = hdr.ethernet.srcAddr;
		hdr.ethernet.srcAddr = tmp;
		bit<32> tmp2;

		/* Send the packet back to the port it came from */
		standard_metadata.egress_spec = standard_metadata.ingress_port;
	}

==BNN_ACT==

	/***** user actions *****/

==BNN_NN_IN==

==BNN_NN_OUT==

==BNN_TAB==

	/****** user tables ******/

	table replication_table {

		key = {
			hdr.ethernet.srcAddr: exact;
		}
		actions = {
			get_nn_input;
		}
		const default_action = get_nn_input();
	}


	table folding_table {

		key = {
			hdr.ethernet.srcAddr: exact;
		}
		actions = {
			get_nn_output;
		}
		const default_action = get_nn_output();
	}


	table send_back_table {

		key = {
			hdr.ethernet.srcAddr: exact;
		}
		actions = {
			send_back;
			_drop;
		}
		const default_action = _drop();
		const entries = {
			MAC_SND : send_back();
		}

	}

	apply {
		replication_table.apply();

==BNN_APPLY==

		folding_table.apply();
		send_back_table.apply();
	}

}
/*************************************************************************
 ****************  E G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

control MyEgress(
	inout my_headers_t        hdr,
	inout metadata meta,
	inout standard_metadata_t standard_metadata)
{
	apply {   }
}

/*************************************************************************
 *************   C H E C K S U M    C O M P U T A T I O N   **************
 *************************************************************************/
control MyComputeChecksum(
	inout my_headers_t  hdr,
	inout metadata meta)
{
	apply {   }
}

/*************************************************************************
 ***********************  D E P A R S E R  *******************************
 *************************************************************************/
control MyDeparser(
	packet_out      packet,
	in my_headers_t hdr)
{
	apply {
		packet.emit(hdr.ethernet);
		packet.emit(hdr.bnn_pkt);
	}
}



V1Switch(
	MyParser(),
	MyVerifyChecksum(),
	MyIngress(),
	MyEgress(),
	MyComputeChecksum(),
	MyDeparser()
) main;
