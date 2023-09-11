import ctypes
import random
from typing import Optional

from ns import ns

NODES = (
    4,  # input nodes
    2,  # input switches
    3,  # middle switches
    2,  # output switches
    4,  # output nodes
)

NODES = (
    9,  # input nodes
    3,  # input switches
    5,  # middle switches
    3,  # output switches
    9,  # output nodes
)
assert len(NODES) == 5
assert NODES[0] % NODES[1] == 0
assert NODES[-1] % NODES[-2] == 0
assert NODES[0] == NODES[-1]
assert NODES[1] == NODES[-2]
assert NODES[0] == NODES[1] ** 2

ns.cppyy.cppdef(
    """
    Ipv4Address getIpv4AddressFromNode(Ptr<Node> node){
    return node->GetObject<Ipv4>()->GetAddress(1,0).GetLocal();
    }
"""
)
# Let's fetch the IP address of the last node, which is on Ipv4Interface 1


def print_routing_table(node):
    ipv4 = node.GetObject[ns.Ipv4]()
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
                    print(
                        f"Destination: {dest}, Gateway: {gateway}, Interface: {interface}"
                    )


def generate_positions():
    positions = ns.CreateObject("ListPositionAllocator")
    for layer, node_count in enumerate(NODES):
        for node in range(node_count):
            positions.__deref__().Add(ns.Vector(layer * 10, node * 10, 0))

    return positions


def get_node_ip_from_idx(
    devices: dict,
    connection_layer: int,
    left_idx: Optional[int] = None,
    right_idx: Optional[int] = None,
) -> ns.cppyy.gbl.ns3.Ipv4Address:
    devs_in_layer = devices[connection_layer]
    if connection_layer == 0:  # inputs
        assert left_idx is not None
        dev = list(filter(lambda d: d["l"] == left_idx, devs_in_layer))
        assert len(dev) == 1
        ip = dev[0]["ip_addresses"][0]
    elif connection_layer == len(NODES) - 2:  # outputs
        assert right_idx is not None
        dev = list(filter(lambda d: d["r"] == right_idx, devs_in_layer))
        assert len(dev) == 1
        ip = dev[0]["ip_addresses"][1]
    else:
        return

    return ip


def main():
    # Create nodes for each stage
    # ns.core.LogComponentEnable("OnOffApplication", ns.core.LOG_LEVEL_INFO)
    ns.core.LogComponentEnable("PacketSink", ns.core.LOG_LEVEL_INFO)
    node_containers = [ns.network.NodeContainer() for _ in NODES]
    x = 10.0
    for num, c in zip(NODES, node_containers):
        y = 10.0
        c.Create(num)
        for node_idx in range(c.GetN()):
            node = c.Get(node_idx).__deref__()
            ns.AnimationInterface.SetConstantPosition(node, x, y)
            y += 10.0
        x += 10.0
    #
    p2p = ns.point_to_point.PointToPointHelper()
    devices = {i: [] for i in range(len(NODES) - 1)}  # inter layer connections hence -1

    # Connect input switches to middle switches
    for connection_layer in devices.keys():
        if connection_layer == 0:
            for node_idx in range(NODES[0]):
                switch_idx = node_idx // NODES[1]
                devices[connection_layer].append(
                    {
                        "connection_layer": connection_layer,
                        "l": node_idx,
                        "r": switch_idx,
                        "devices": p2p.Install(
                            node_containers[connection_layer].Get(node_idx),
                            node_containers[connection_layer + 1].Get(switch_idx),
                        ),  # returns NetDeviceContainer
                    }
                )

        elif connection_layer == len(NODES) - 2:  # -2 for last layer
            # connections to sources/sinks with single device
            for node_idx in range(NODES[-1]):
                switch_idx = node_idx // NODES[-2]
                devices[connection_layer].append(
                    {
                        "connection_layer": connection_layer,
                        "l": switch_idx,
                        "r": node_idx,
                        "devices": p2p.Install(
                            node_containers[connection_layer].Get(switch_idx),
                            node_containers[connection_layer + 1].Get(node_idx),
                        ),  # returns NetDeviceContainer
                    }
                )
        else:
            # interswitch connections hence more than one device
            for i in range(NODES[connection_layer]):  # left side
                for j in range(NODES[connection_layer + 1]):  # right side
                    devices[connection_layer].append(
                        {
                            "connection_layer": connection_layer,
                            "l": i,
                            "r": j,
                            "devices": p2p.Install(
                                node_containers[connection_layer].Get(i),
                                node_containers[connection_layer + 1].Get(j),
                            ),  # returns NetDeviceContainer
                        }
                    )

    # Add Internet stack
    internet = ns.internet.InternetStackHelper()
    internet.InstallAll()

    # Assign IP addresses
    address = ns.internet.Ipv4AddressHelper()
    for layer, devs in devices.items():
        for idx, dev in enumerate(devs):
            base_ip = f"10.{layer}.{idx}.0"
            address.SetBase(
                ns.network.Ipv4Address(base_ip), ns.network.Ipv4Mask("255.255.255.0")
            )
            address_container = address.Assign(dev["devices"])
            # store ip addresses for future use
            dev["ip_addresses"] = (
                address_container.GetAddress(0),
                address_container.GetAddress(1),
            )

    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

    # Set up traffic
    source_apps = ns.network.ApplicationContainer()
    dest_apps = ns.network.ApplicationContainer()

    # for i in range(num_switches_per_stage):

    source_nodes_idxs = list(range(NODES[0]))
    dest_nodes_idxs = list(range(NODES[-1]))
    for i in range(NODES[0]):
        source_node_idx = random.choice(source_nodes_idxs)
        dest_node_idx = random.choice(dest_nodes_idxs)
        source_nodes_idxs.remove(source_node_idx)
        dest_nodes_idxs.remove(dest_node_idx)

        source_node = node_containers[0].Get(source_node_idx)
        dest_node = node_containers[-1].Get(dest_node_idx)

        source_addr = get_node_ip_from_idx(devices, 0, source_node_idx)
        dest_addr = get_node_ip_from_idx(
            devices, len(NODES) - 2, right_idx=dest_node_idx
        )
        print(source_addr, dest_addr)

        # a = ns.cppyy.gbl.getIpv4AddressFromNode(source_node)

        #
        # onoff_helper.SetAttribute("Remote", dest_addr)
        port = 9
        source_socket = ns.network.InetSocketAddress(source_addr, port)
        onoff_helper = ns.applications.OnOffHelper(
            "ns3::UdpSocketFactory", source_socket.ConvertTo()
        )
        onoff_helper.SetAttribute(
            "OnTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=1]")
        )
        onoff_helper.SetAttribute(
            "OffTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=0]")
        )
        source_apps.Add(onoff_helper.Install(source_node))

        destination_socket = ns.network.InetSocketAddress(dest_addr, port)
        #  Create a packet sink to receive these packets
        sink = ns.applications.PacketSinkHelper(
            "ns3::UdpSocketFactory",
            destination_socket.ConvertTo(),
        )
        dest_apps.Add(sink.Install(dest_node))
        if i == 0:
            p2p.EnablePcapAll("/opt/brum")

    #
    source_apps.Start(ns.core.Seconds(2.0))
    source_apps.Stop(ns.core.Seconds(10.0))
    dest_apps.Start(ns.core.Seconds(1.0))
    dest_apps.Stop(ns.core.Seconds(10.0))

    p2p.EnableAsciiAll("clos-ascii-trace.tr")
    print("sssss")
    animator = ns.netanim.AnimationInterface("clos-animation.xml")
    ns.core.Simulator.Run()
    print("sssss")
    # ns.core.Simulator.Stop(ns.core.Seconds(5))

    # # Analyze and print results
    # monitor.CheckForLostPackets()
    # classifier = flow_monitor_helper.GetClassifier()
    # stats = monitor.GetFlowStats()
    #
    # for i, stat in enumerate(stats):
    #     if not stat.rxPackets:
    #         print(
    #             "Flow",
    #             i,
    #             "(from node",
    #             classifier.GetFlow(i).sourceAddress,
    #             "to",
    #             classifier.GetFlow(i).destinationAddress,
    #             ") is blocked!",
    #         )
    #     else:
    #         print(
    #             "Flow",
    #             i,
    #             "(from node",
    #             classifier.GetFlow(i).sourceAddress,
    #             "to",
    #             classifier.GetFlow(i).destinationAddress,
    #             ") has throughput of",
    #             stat.rxBytes * 8.0 / 9.0 / 1e3,
    #             "kbps",
    #         )

    ns.core.Simulator.Destroy()


if __name__ == "__main__":
    main()
