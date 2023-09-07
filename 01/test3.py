import random

from ns import ns

# Global parameters for the Clos network
r = 3  # Number of input switches
n = 3  # Number of output switches
m = 3  # Number of middle switches


def route_packet(packet, source, destination):
    middle_switch = (source + destination) % n
    return middle_switch


def main(argv):
    # Create nodes for input, middle, and output switches
    input_nodes = ns.network.NodeContainer()
    middle_nodes = ns.network.NodeContainer()
    output_nodes = ns.network.NodeContainer()

    input_nodes.Create(r)
    middle_nodes.Create(m)
    output_nodes.Create(n)

    # Create Point-to-Point links with default settings
    pointToPoint = ns.point_to_point.PointToPointHelper()

    devices = ns.network.NetDeviceContainer()

    # Connect input switches to middle switches
    for i in range(r):
        for j in range(m):
            devices.Add(pointToPoint.Install(input_nodes.Get(i), middle_nodes.Get(j)))

    # Connect middle switches to output switches
    for j in range(m):
        for k in range(n):
            devices.Add(pointToPoint.Install(middle_nodes.Get(j), output_nodes.Get(k)))

    stack = ns.internet.InternetStackHelper()
    stack.Install(ns.network.NodeContainer(input_nodes, middle_nodes, output_nodes))

    address = ns.internet.Ipv4AddressHelper()
    address.SetBase(
        ns.network.Ipv4Address("10.0.0.0"), ns.network.Ipv4Mask("255.255.255.0")
    )
    address.Assign(devices)

    port = 9  # Discard port
    available_sources = list(range(r))  # List of available input switches
    available_sinks = list(range(n))  # List of available output switches

    # while available_sources and available_sinks:
    #     source_index = random.choice(available_sources)
    #     sink_index = random.choice(available_sinks)
    #
    #     # Create an OnOff application to generate packets at the chosen source
    #     onOffHelper = ns.applications.OnOffHelper(
    #         "ns3::UdpSocketFactory",
    #         # ns.network.Address(ns.network.InetSocketAddress(port)),
    #         # ns.network.Address(ns.network.InetSocketAddress("255.255.255.255", port)),
    #         ns.network.InetSocketAddress("255.255.255.255", port),
    #     )
    #     onOffHelper.SetConstantRate(ns.network.DataRate("448kb/s"))
    #
    #     sourceApps = onOffHelper.Install(input_nodes.Get(source_index))
    #     sourceApps.Start(ns.core.Seconds(1.0))
    #     sourceApps.Stop(ns.core.Seconds(10.0))
    #
    #     # Create a PacketSink at the chosen destination to receive packets
    #     sinkHelper = ns.applications.PacketSinkHelper(
    #         "ns3::UdpSocketFactory",
    #         # ns.network.Address(ns.network.InetSocketAddress(port)),
    #         ns.network.Address(ns.network.InetSocketAddress("0.0.0.0", port)),
    #     )
    #     sinkApps = sinkHelper.Install(output_nodes.Get(sink_index))
    #     sinkApps.Start(ns.core.Seconds(1.0))
    #     sinkApps.Stop(ns.core.Seconds(10.0))
    #
    #     # Remove chosen source and sink from available lists
    #     available_sources.remove(source_index)
    #     available_sinks.remove(sink_index)

    ns.core.Simulator.Run()
    ns.core.Simulator.Destroy()
    # For the OnOffHelper, the address doesn't matter much, so we'll use a wildcard address


if __name__ == "__main__":
    import sys

    main(sys.argv)
