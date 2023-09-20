import ctypes
from typing import Union

from ns import ns

"""
# enable logging on applications
ns.LogComponentEnable("UdpEchoClientApplication", ns.core.LOG_LEVEL_INFO)
ns.LogComponentEnable("UdpEchoServerApplication", ns.core.LOG_LEVEL_INFO)
ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()
"""


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
