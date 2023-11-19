import ctypes
import os
from typing import Optional, Union
import json

from ns import ns

"""
# enable logging on applications
ns.LogComponentEnable("UdpEchoClientApplication", ns.core.LOG_LEVEL_INFO)
ns.LogComponentEnable("UdpEchoServerApplication", ns.core.LOG_LEVEL_INFO)
ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()
"""

##########################################################################
# 03
def get_node_ips_all(node_container: Union[ns.NodeContainer, ns.Ptr], verbose=False) -> list:
    """
    Get IP addresses of all nodes in a node container.

    Parameters
    ----------
    node_container : Union[ns.NodeContainer, ns.Ptr]
        The node container or a pointer to it.
    verbose : bool, optional
        If True, print verbose output, by default False.

    Returns
    -------
    list
        List of IP addresses of all nodes in the node container.
    """
    # Ensure that node is a Node and not a pointer
    try:
        node_container = node_container.__deref__()
    except AttributeError as e:
        pass
    output_list = []
    for node_idx in range(node_container.GetN()):
        output_list.append(get_node_ips(node_container.Get(node_idx), verbose=verbose))
    return output_list

def get_node_ips(node: Union[ns.Node, ns.Ptr], verbose: bool = False) -> dict[int,list]:
    """
    Get IP addresses of a node.

    Parameters
    ----------
    node : Union[ns.Node, ns.Ptr]
        The node or a pointer to it.
    verbose : bool, optional
        If True, print verbose output, by default False.

    Returns
    -------
    dict[int,list]
        Dictionary of IP addresses of the node, keyed by interface index.
    """
    # Ensure that node is a Node and not a pointer
    try:
        node = node.__deref__()
    except AttributeError as e:
        pass
    addrs: dict[int,list] = {}
    addrs_verbose: dict[int,list] = {}
    ipv4 = node.GetObject[ns.internet.Ipv4]()
    for i in range(ipv4.GetNInterfaces()):
        for j in range(ipv4.GetNAddresses(i)):
            if i not in addrs.keys():
                addrs[i] = [ipv4.GetAddress(i, j)]
                addrs_verbose[i] = [str(ipv4.GetAddress(i, j))]
            else:
                addrs[i].append(ipv4.GetAddress(i, j))
                addrs_verbose[i].append(str(ipv4.GetAddress(i, j)))
    if verbose:
        print(json.dumps(addrs_verbose, indent=2))
    return addrs

def get_ip_of_remote_server(echo_client: Union[ns.applications.UdpEchoClient, ns.Ptr]) -> ns.network.Ipv4Address:
    """
    Get IP address of a remote server.

    Parameters
    ----------
    echo_client : Union[ns.applications.UdpEchoClient, ns.Ptr]
        The echo client or a pointer to it.

    Returns
    -------
    ns.network.Ipv4Address
        The IP address of the remote server.
    """
    # Ensure that client is application and not a pointer
    try:
        echo_client = echo_client.__deref__()
    except AttributeError as e:
        pass
    f = ns.AddressValue()
    echo_client.GetAttribute("RemoteAddress",f)
    addr = f.Get()
    ipv4_addr = ns.Ipv4Address.ConvertFrom(addr)
    return ipv4_addr

##########################################################################
# 02

"""
def generate_positions():
    positions = ns.CreateObject("ListPositionAllocator")
    for layer, node_count in enumerate(NODES):
        for node in range(node_count):
            positions.__deref__().Add(ns.Vector(layer * 10, node * 10, 0))

    return positions
"""


def get_node_ip_from_idx(
    devices: dict,
    connection_layer: int,
    left_idx: Optional[int] = None,
    right_idx: Optional[int] = None,
    nodes_len: int = 5,
) -> ns.Ipv4Address:
    """
    Retrieves the IP address of a node from its index.

    Parameters
    ----------
    devices : dict
        The dictionary containing the devices. The structure is defined in Jupyter.
    connection_layer : int
        The layer of the connection.
    left_idx : Optional[int], optional
        The index of the node on the left, by default None.
    right_idx : Optional[int], optional
        The index of the node on the right, by default None.
    nodes_len : int, optional
        The length of the nodes, by default 5. This is actually a number of layers in
        Clos network with endpoints so 5 actually means a 3-stage Clos network.

    Returns
    -------
    ns.cppyy.gbl.ns3.Ipv4Address
        The IP address of the node.
    """
    devs_in_layer = devices[connection_layer]
    if connection_layer == 0:  # inputs
        assert left_idx is not None
        dev = list(filter(lambda d: d["l"] == left_idx, devs_in_layer))
        assert len(dev) == 1
        ip = dev[0]["ip_addresses"][0]
    elif connection_layer == nodes_len - 2:  # outputs
        assert right_idx is not None
        dev = list(filter(lambda d: d["r"] == right_idx, devs_in_layer))
        assert len(dev) == 1
        ip = dev[0]["ip_addresses"][1]
    else:
        return

    return ip


##########################################################################


def get_iface_from_ifacecontainer(
    container: ns.Ipv4InterfaceContainer, if_idx: int
) -> ns.Ipv4Interface:
    """
    Retrieves an interface from an Ipv4InterfaceContainer.

    Parameters
    ----------
    container : ns.Ipv4InterfaceContainer
        The container from which the interface is to be retrieved.
    if_idx : int
        The index of the interface in the container.

    Returns
    -------
    ns.Ipv4Interface
        The retrieved interface.
    """
    ipproto, idx = container.Get(if_idx)
    ipproto = ipproto.__deref__()
    iface = ipproto.GetInterface(idx).__deref__()
    return iface


def assign_ip_to_iface(
    device: Union[ns.NetDevice, ns.Ptr], addr: str, netmask: str
) -> bool:
    """
    Assigns an IP address to a device.

    Parameters
    ----------
    device : Union[ns.NetDevice, ns.Ptr]
        The device to which the IP address will be assigned.
    addr : str
        The IP address to be assigned.
    netmask : str
        The netmask for the IP address.

    Returns
    -------
    bool
        True if the IP address was successfully assigned, False otherwise.
    """

    # Ensure that device is a NetDevice
    try:
        device = device.__deref__()
    except AttributeError as e:
        # device is already a NetDevice
        pass

    # Get the node
    node = device.GetNode().__deref__()
    # Get Ipv4 object for node
    ip = node.GetObject[ns.internet.Ipv4]().__deref__()
    # Check if there is an interface with ip stack on device
    if_index = ip.GetInterfaceForDevice(device)
    if if_index == -1:
        if_index = ip.AddInterface(device)

    # Assign ip address
    status = ip.AddAddress(
        if_index,
        ns.internet.Ipv4InterfaceAddress(
            ns.network.Ipv4Address(addr), ns.network.Ipv4Mask(netmask)
        ),
    )

    return status


def get_ipproto_on_node(node: Union[ns.Node, ns.Ptr]) -> ns.Ipv4L3Protocol:
    """
    Returns the Ipv4L3Protocol object for a node.

    Parameters
    ----------
    node : Union[ns.Node, ns.Ptr]
        The node for which the Ipv4L3Protocol object is to be returned.

    Returns
    -------
    ns.Ipv4L3Protocol
        The Ipv4L3Protocol object for the node.
    """
    # Ensure that node is a Node and not a pointer
    try:
        node = node.__deref__()
    except AttributeError as e:
        pass

    return node.GetObject[ns.internet.Ipv4]().__deref__()


def create_echo_client_helper(
    server_address: ns.Address,
    server_port: int,
    max_packets: int = 50,
    interval: float = 1.0,
    packet_size: int = 1500,
) -> ns.applications.UdpEchoClientHelper:
    """
    Creates a UdpEchoClientHelper object.

    Parameters
    ----------
    server_address : ns.Address
        The server address for the UdpEchoClientHelper.
    server_port : int
        The server port for the UdpEchoClientHelper.
    max_packets : int, optional
        The maximum number of packets for the UdpEchoClientHelper, by default 50.
    interval : float, optional
        The interval for the UdpEchoClientHelper, by default 1.0.
    packet_size : int, optional
        The packet size for the UdpEchoClientHelper, by default 1500.

    Returns
    -------
    ns.applications.UdpEchoClientHelper
        The created UdpEchoClientHelper object.
    """
    echo_client = ns.applications.UdpEchoClientHelper(server_address, server_port)
    echo_client.SetAttribute("MaxPackets", ns.core.UintegerValue(max_packets))
    echo_client.SetAttribute("Interval", ns.core.TimeValue(ns.core.Seconds(interval)))
    echo_client.SetAttribute("PacketSize", ns.core.UintegerValue(packet_size))
    return echo_client


def get_routing_table_str(node: Union[ns.Node, ns.Ptr]) -> str:
    """
    Retrieves the routing table for a node and returns it as a string.
    This function uses ns-3 internal PrintRoutingTable method.
    However, as this method only works with files, we provide it with
    temporary name and the file is then read to memory and deleted.

    Parameters
    ----------
    node : Union[ns.Node, ns.Ptr]
        The node for which the routing table is to be returned.

    Returns
    -------
    str
        The routing table for the node.
    """
    try:
        node = node.__deref__()
    except AttributeError as e:
        pass

    tmpfname = ".routing"
    ipproto = node.GetObject[ns.Ipv4]().__deref__()
    routing_proto = ipproto.GetRoutingProtocol().__deref__()
    routing_stream = ns.network.OutputStreamWrapper(tmpfname, 0)
    routing_proto.PrintRoutingTable(routing_stream)

    with open(tmpfname, "r") as f:
        routing_table = f.read()
    os.remove(tmpfname)
    return routing_table


def get_routing_table(node: Union[ns.Node, ns.Ptr]) -> list:
    """
    Returns the routing table for a node.

    Parameters
    ----------
    node : Union[ns.Node, ns.Ptr]
        The node for which the routing table is to be returned.

    Returns
    -------
    list
        The routing table for the node.
    """
    try:
        node = node.__deref__()
    except AttributeError as e:
        pass

    ipv4 = node.GetObject[ns.Ipv4]()
    routes = []
    if ipv4:
        list_routing = ipv4.GetRoutingProtocol().GetObject[ns.Ipv4ListRouting]()

        # Iterate through each routing protocol in the list
        for i in range(list_routing.GetNRoutingProtocols()):
            priority = ctypes.c_int16()
            routing_protocol = list_routing.GetRoutingProtocol(i, priority)

            # Check if the routing protocol provides a GetNRoutes function
            # This is true for Ipv4StaticRouting, but may vary for other protocols
            if hasattr(routing_protocol, "GetNRoutes"):
                num_routes = routing_protocol.GetNRoutes()

                for j in range(num_routes):
                    route = routing_protocol.GetRoute(j)
                    dest = route.GetDest()
                    gateway = route.GetGateway()
                    interface = route.GetInterface()
                    routes.append(dict(dest=dest, gateway=gateway, interface=interface))
    return routes


def stringify_routing_table(routing_table: list[dict]) -> list[str]:
    """
    Converts a routing table to a list of strings.

    Parameters
    ----------
    routing_table : list[dict]
        The routing table to be converted.

    Returns
    -------
    list[str]
        The converted routing table.
    """
    rt = []
    for i in routing_table:
        rt.append(
            f"dest: {i['dest']}, gateway: {i['gateway']}, interface: {i['interface']}"
        )

    return rt
