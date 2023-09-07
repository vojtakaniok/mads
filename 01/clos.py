import random

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


def generate_positions():
    positions = ns.CreateObject("ListPositionAllocator")
    for layer, node_count in enumerate(NODES):
        for node in range(node_count):
            positions.__deref__().Add(ns.Vector(layer * 10, node * 10, 0))

    return positions


def main():
    # Create nodes for each stage
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
                        "layer": connection_layer,
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
                        "layer": connection_layer,
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
                            "layer": connection_layer,
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
            print(address_container.GetAddress(0))
            print(address_container.GetAddress(1))

    # Set up traffic
    source_apps = ns.network.ApplicationContainer()
    dest_apps = ns.network.ApplicationContainer()

    # for i in range(num_switches_per_stage):
    onoff_helper = ns.applications.OnOffHelper(
        "ns3::UdpSocketFactory", ns.network.Address()
    )
    onoff_helper.SetAttribute(
        "OnTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=1]")
    )
    onoff_helper.SetAttribute(
        "OffTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=0]")
    )

    for i in range(NODES[0]):
        source_nodes_idxs = list(range(NODES[0]))
        dest_nodes_idxs = list(range(NODES[-1]))
        source_node_idx = random.choice(source_nodes_idxs)
        dest_node_idx = random.choice(dest_nodes_idxs)
        source_nodes_idxs.remove(source_node_idx)
        dest_nodes_idxs.remove(dest_node_idx)

        source_node = node_containers[0].Get(source_node_idx)
        # print(source_node.GetObject(ns.Ipv4.GetTypeId()))
        address.GetAddress(source_node)

        a = ns.cppyy.gbl.getIpv4AddressFromNode(source_node)
        # ipv4_obj = source_node.GetObject(ns.Ipv4.GetTypeId())
        # address = ipv4_obj.GetAddress(1, 0).GetLocal()
        d = source_node.GetDevice(0)
        i = ns.Ipv4.GetInterfaceForDevice(d)
        a = ns.Ipv4.GetAddress(i)
        print(a)

    #
    #     # remote_addr = ns.network.InetSocketAddress(output_stage.Get(i).GetObject(ns.internet.Ipv4.GetTypeId()).GetAddress(1,0).GetLocal(), 9)
    #     # ipv4_obj = ns.internet.Ipv4AddressHelper.GetIpv4(output_stage.Get(i))
    #     # ipv4_obj = output_stage.Get(i).GetObject(ns.internet.Ipv4.GetTypeId())
    #     # ipv4_obj = output_stage.Get(i).GetObject(ns.internet.Ipv4.GetTypeId()).GetObject(ns.internet.Ipv4)
    #     ipv4_obj = output_stage.Get(i).GetObject(ns.internet.Ipv4.GetTypeId())
    #     remote_addr = ns.network.InetSocketAddress(
    #         ipv4_obj.GetAddress(1, 0).GetLocal(), 9
    #     )
    #
    #     onoff_helper.SetAttribute("Remote", ns.network.AddressValue(remote_addr))
    #
    #     sourceApps.Add(onoff_helper.Install(input_stage.Get(i)))
    #
    #     # Set up packet sinks at the receivers to capture packets
    #     packet_sink_helper = ns.applications.PacketSinkHelper(
    #         "ns3::UdpSocketFactory", ns.network.Address(remote_addr)
    #     )
    #     destApps.Add(packet_sink_helper.Install(output_stage.Get(i)))
    #
    source_apps.Start(ns.core.Seconds(1.0))
    source_apps.Stop(ns.core.Seconds(10.0))
    dest_apps.Start(ns.core.Seconds(1.0))
    dest_apps.Stop(ns.core.Seconds(10.0))

    # Setup FlowMonitor
    # flow_monitor_helper = ns.flow_monitor.FlowMonitorHelper()
    # monitor = flow_monitor_helper.InstallAll()

    # Set up NetAnim

    # p2p.EnableAsciiAll("clos-ascii-trace.tr")
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
