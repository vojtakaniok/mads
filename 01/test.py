from ns import ns

# from dataclasses import dataclass

N_DEV_INPUT = 4
N_DEV_OUTPUT = 4
N_SW_INPUT = 2
N_SW_MIDDLE = 2
N_SW_OUTPUT = 2

# @dataclass
# class Device:
#     layer: int # 0: input, 1: middle, 2: output
#     lswitch: int
#     rswitch: int


def main():
    # Create nodes for each stage
    input_stage = ns.network.NodeContainer()
    input_stage.Create(N_SW_INPUT)

    middle_stage = ns.network.NodeContainer()
    middle_stage.Create(N_SW_MIDDLE)

    output_stage = ns.network.NodeContainer()
    output_stage.Create(N_SW_OUTPUT)

    p2p = ns.point_to_point.PointToPointHelper()
    devices = {1: [], 2: []}

    # Connect input switches to middle switches
    LAYER = 1
    for i in range(N_SW_INPUT):
        for j in range(N_SW_MIDDLE):
            devices[LAYER].append(
                {
                    "layer": LAYER,
                    "l": i,
                    "r": j,
                    "devices": p2p.Install(input_stage.Get(i), middle_stage.Get(j)),
                }
            )

    # Connect middle switches to output switches
    LAYER = 2
    for j in range(N_SW_MIDDLE):
        for k in range(N_SW_OUTPUT):
            devices[LAYER].append(
                {
                    "layer": LAYER,
                    "l": j,
                    "r": k,
                    "devices": p2p.Install(input_stage.Get(i), middle_stage.Get(j)),
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
            address.Assign(dev["devices"])

    # Set up traffic
    source_apps = ns.network.ApplicationContainer()
    dest_apps = ns.network.ApplicationContainer()

    # for i in range(num_switches_per_stage):
    #     onoff_helper = ns.applications.OnOffHelper(
    #         "ns3::UdpSocketFactory", ns.network.Address()
    #     )
    #     onoff_helper.SetAttribute(
    #         "OnTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=1]")
    #     )
    #     onoff_helper.SetAttribute(
    #         "OffTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=0]")
    #     )
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
    # animator = ns.netanim.AnimationInterface("clos-animation.xml")

    print("sssss")
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
