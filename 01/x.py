from ns import ns


def main():
    # Create two nodes
    nodes = ns.network.NodeContainer()
    nodes.Create(2)

    # Set up the Point-to-Point link between the nodes
    pointToPoint = ns.network.PointToPointHelper()
    pointToPoint.SetDeviceAttribute("DataRate", ns.core.StringValue("5Mbps"))
    pointToPoint.SetChannelAttribute("Delay", ns.core.StringValue("2ms"))
    devices = pointToPoint.Install(nodes)

    # Install the Internet stack on the nodes
    stack = ns.internet.InternetStackHelper()
    stack.Install(nodes)

    # Assign IP addresses
    address = ns.internet.Ipv4AddressHelper()
    address.SetBase(
        ns.network.Ipv4Address("10.0.0.0"), ns.network.Ipv4Mask("255.255.255.0")
    )
    interfaces = address.Assign(devices)

    # Set up the OnOffApplication on the first node
    port = 9
    socketAddr = ns.network.InetSocketAddress(ns.network.Ipv4Address("10.0.0.2"), port)
    onoff = ns.applications.OnOffHelper("ns3::UdpSocketFactory", socketAddr.ConvertTo())
    apps = onoff.Install(nodes.Get(0))
    apps.Start(ns.core.Seconds(3))
    apps.Stop(ns.core.Seconds(10))

    #  Create a packet sink to receive these packets
    sink = ns.applications.PacketSinkHelper(
        "ns3::UdpSocketFactory",
        socketAddr.ConvertTo(),
    )
    sinkContainer = ns.network.NodeContainer(nodes.Get(1))
    apps = sink.Install(sinkContainer)
    pointToPoint.EnablePcapAll("/opt/onoff")

    # Set up a PacketSink on the second node to receive packets
    # Run the simulation
    ns.core.Simulator.Run()
    ns.core.Simulator.Destroy()


if __name__ == "__main__":
    main()
