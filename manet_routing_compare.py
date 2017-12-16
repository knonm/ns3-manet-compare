import csv
import sys
import os

import ns.aodv
import ns.applications
import ns.core
import ns.dsdv
import ns.dsr
import ns.internet
import ns.mobility
import ns.network
import ns.olsr
import ns.wifi

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
__workdir__ = os.path.join(__location__, "work")


class RoutingExperiment:
    def __init__(self):
        self.port = 9
        self.bytesTotal = 0
        self.packetsReceived = 0
        self.m_CSVfileName = "manet-routing.output"
        self.m_nSinks = 10
        self.m_protocolName = ""
        self.m_txp = 7.5
        self.m_traceMobility = False
        self.m_protocol = 2
        self.m_total_time = 200
        self.m_nodes = 50

    # Ptr<Socket> socket, Ptr<Packet> packet, Address senderAddress
    # returns string
    def PrintReceivedPacket(self, socket, packet, senderAddress):
        oss = str(ns.core.Simulator.Now().GetSeconds()) + " " + str(socket.GetNode().GetId())

        if ns.network.InetSocketAddress.IsMatchingType(senderAddress):
            addr = ns.network.InetSocketAddress.ConvertFrom(senderAddress)  # type: InetSocketAddress
            ipv4 = addr.GetIpv4()  # type: Ipv4Address
            oss += " received one packet from "
            sys.stdout.write(oss)
            print ipv4
        else:
            oss += " received one packet!"
            print oss

    # Ptr<Socket> socket
    # returns void
    def ReceivePacket(self, socket):
        senderAddress = ns.network.Address()  # type: ns.network.Address
        packet = socket.RecvFrom(senderAddress)
        while packet != None:
            self.bytesTotal += packet.GetSize()
            self.packetsReceived += 1
            self.PrintReceivedPacket(socket, packet, senderAddress)
            packet = socket.RecvFrom(senderAddress)

    def WriteHeaderCsv(self):
        with open(os.path.join(__workdir__, (self.m_CSVfileName + ".csv")), 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(
                ['SimulationSecond', 'ReceiveRate', 'PacketsReceived', 'NumberOfSinks', 'RoutingProtocol',
                 'TransmissionPower'])

    def CheckThroughput(self):
        kbs = (self.bytesTotal * 8.0) / 1000
        self.bytesTotal = 0
        now = int((ns.core.Simulator.Now()).GetSeconds())

        with open(os.path.join(__workdir__, (self.m_CSVfileName + ".csv")), 'a') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([now, kbs, self.packetsReceived, self.m_nSinks, self.m_protocolName, self.m_txp])

        self.packetsReceived = 0
        ns.core.Simulator.Schedule(ns.core.Seconds(1.0), RoutingExperiment.CheckThroughput, self)

    # Ipv4Address addr, Ptr<Node> node
    # returns Ptr<Socket>
    def SetupPacketReceive(self, addr, node):
        tid = ns.core.TypeId.LookupByName("ns3::UdpSocketFactory")  # type: TypeId
        sink = ns.network.Socket.CreateSocket(node, tid)  # type: Ptr<Socket>
        local = ns.network.InetSocketAddress(addr, self.port)  # type: InetSocketAddress
        sink.Bind(local)
        sink.SetRecvCallback(self.ReceivePacket)

        return sink

    # int argc, char **argv
    # returns string
    def CommandSetup(self, argc, argv):
        cmd = ns.core.CommandLine()  # type: CommandLine
        cmd.AddValue("CSVfileName", "The name of the CSV output file name", self.m_CSVfileName)
        cmd.AddValue("traceMobility", "Enable mobility tracing", self.m_traceMobility)
        cmd.AddValue("protocol", "1=OLSR;2=AODV;3=DSDV;4=DSR", self.m_protocol)
        cmd.Parse(argc, argv)
        return self.m_CSVfileName

    # int nSinks, double txp, std::string CSVfileName
    def Run(self, *positional_parameters, **keyword_parameters):
        ns.network.Packet.EnablePrinting()

        if 'nSinks' in keyword_parameters:
            self.m_nSinks = keyword_parameters['nSinks'];
        if 'txp' in keyword_parameters:
            self.m_txp = keyword_parameters['txp'];
        if 'TotalTime' in keyword_parameters:
            self.m_total_time = keyword_parameters['TotalTime'];
        if 'Nodes' in keyword_parameters:
            self.m_nodes = keyword_parameters['Nodes'];
        if 'CSVfileName' in keyword_parameters:
            self.m_CSVfileName = keyword_parameters['CSVfileName'];

        rate = "2048bps"
        phyMode = "DsssRate11Mbps"
        tr_name = self.m_CSVfileName + "-compare"
        nodeSpeed = 20  # in m/s
        nodePause = 0  # in s
        self.m_protocolName = "protocol"

        ns.core.Config.SetDefault("ns3::OnOffApplication::PacketSize", ns.core.StringValue("64"))
        ns.core.Config.SetDefault("ns3::OnOffApplication::DataRate", ns.core.StringValue(rate))

        # Set Non-unicastMode rate to unicast mode
        ns.core.Config.SetDefault("ns3::WifiRemoteStationManager::NonUnicastMode", ns.core.StringValue(phyMode));

        adhocNodes = ns.network.NodeContainer()
        adhocNodes.Create(self.m_nodes)

        # setting up wifi phy and channel using helpers
        wifi = ns.wifi.WifiHelper()
        wifi.SetStandard(ns.wifi.WIFI_PHY_STANDARD_80211b)

        wifiPhy = ns.wifi.YansWifiPhyHelper.Default()
        wifiChannel = ns.wifi.YansWifiChannelHelper()
        wifiChannel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel")
        wifiChannel.AddPropagationLoss("ns3::FriisPropagationLossModel")
        wifiPhy.SetChannel(wifiChannel.Create())

        # Add a mac and disable rate control
        wifiMac = ns.wifi.WifiMacHelper()
        wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                     "DataMode", ns.core.StringValue(phyMode),
                                     "ControlMode", ns.core.StringValue(phyMode))

        wifiPhy.Set("TxPowerStart", ns.core.DoubleValue(self.m_txp))
        wifiPhy.Set("TxPowerEnd", ns.core.DoubleValue(self.m_txp))

        wifiMac.SetType("ns3::AdhocWifiMac")
        adhocDevices = wifi.Install(wifiPhy, wifiMac, adhocNodes)  # type: NetDeviceContainer

        mobilityAdhoc = ns.mobility.MobilityHelper()
        streamIndex = 0  # used to get consistent mobility across scenarios

        pos = ns.core.ObjectFactory()
        pos.SetTypeId("ns3::RandomRectanglePositionAllocator")
        pos.Set("X", ns.core.StringValue("ns3::UniformRandomVariable[Min=0.0|Max=300.0]"))
        pos.Set("Y", ns.core.StringValue("ns3::UniformRandomVariable[Min=0.0|Max=1500.0]"))

        # Same as: Ptr<PositionAllocator> taPositionAlloc = pos.Create ()->GetObject<PositionAllocator> ();
        taPositionAlloc = pos.Create().GetObject(
            ns.mobility.PositionAllocator.GetTypeId())  # type: Ptr<PositionAllocator>
        streamIndex += taPositionAlloc.AssignStreams(streamIndex)

        ssSpeed = "ns3::UniformRandomVariable[Min=0.0|Max=%s]" % (nodeSpeed)
        ssPause = "ns3::ConstantRandomVariable[Constant=%s]" % (nodePause)

        mobilityAdhoc.SetMobilityModel("ns3::RandomWaypointMobilityModel",
                                       "Speed", ns.core.StringValue(ssSpeed),
                                       "Pause", ns.core.StringValue(ssPause),
                                       "PositionAllocator", ns.core.PointerValue(taPositionAlloc))
        mobilityAdhoc.SetPositionAllocator(taPositionAlloc)
        mobilityAdhoc.Install(adhocNodes)
        streamIndex += mobilityAdhoc.AssignStreams(adhocNodes, streamIndex)
        # NS_UNUSED(streamIndex) # From this point, streamIndex is unused

        aodv = ns.aodv.AodvHelper()
        olsr = ns.olsr.OlsrHelper()
        dsdv = ns.dsdv.DsdvHelper()
        dsr = ns.dsr.DsrHelper()
        dsrMain = ns.dsr.DsrMainHelper()
        list = ns.internet.Ipv4ListRoutingHelper()
        internet = ns.internet.InternetStackHelper()

        if self.m_protocol == 1:
            list.Add(olsr, 100)
            self.m_protocolName = "OLSR"
        elif self.m_protocol == 2:
            list.Add(aodv, 100)
            self.m_protocolName = "AODV"
        elif self.m_protocol == 3:
            list.Add(dsdv, 100)
            self.m_protocolName = "DSDV"
        elif self.m_protocol == 4:
            self.m_protocolName = "DSR"
        else:
            print("No such protocol:%s" % (self.m_protocol))  # NS_FATAL_ERROR ("No such protocol:" << m_protocol);

        if self.m_protocol < 4:
            internet.SetRoutingHelper(list)
            internet.Install(adhocNodes)
        elif self.m_protocol == 4:
            internet.Install(adhocNodes)
            dsrMain.Install(dsr, adhocNodes)

        print("assigning ip address")  # NS_LOG_INFO("assigning ip address");

        addressAdhoc = ns.internet.Ipv4AddressHelper()
        addressAdhoc.SetBase(ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
        adhocInterfaces = addressAdhoc.Assign(adhocDevices)

        onoff1 = ns.applications.OnOffHelper("ns3::UdpSocketFactory", ns.network.Address())
        onoff1.SetAttribute("OnTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=1.0]"))
        onoff1.SetAttribute("OffTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=0.0]"))

        for i in range(0, self.m_nSinks):
            # Ptr<Socket> sink = SetupPacketReceive (adhocInterfaces.GetAddress (i), adhocNodes.Get (i));
            sink = self.SetupPacketReceive(adhocInterfaces.GetAddress(i), adhocNodes.Get(i))

            remoteAddress = ns.network.AddressValue(
                ns.network.InetSocketAddress(adhocInterfaces.GetAddress(i), self.port))
            onoff1.SetAttribute("Remote", remoteAddress);

            # Ptr<UniformRandomVariable> var = CreateObject<UniformRandomVariable> ();
            posURV = ns.core.ObjectFactory()
            posURV.SetTypeId("ns3::UniformRandomVariable")
            var = posURV.Create().GetObject(ns.core.UniformRandomVariable.GetTypeId())

            temp = onoff1.Install(adhocNodes.Get(i + self.m_nSinks))  # type: ApplicationContainer
            temp.Start(ns.core.Seconds(var.GetValue(100.0, 101.0)))
            temp.Stop(ns.core.Seconds(self.m_total_time))

        ss = self.m_nodes
        nodes = str(ss)

        ss2 = nodeSpeed
        sNodeSpeed = str(ss2)

        ss3 = nodePause
        sNodePause = str(ss3)

        ss4 = rate
        sRate = str(ss4)

        # NS_LOG_INFO ("Configure Tracing.");
        tr_name = tr_name + "_" + \
                  self.m_protocolName + "_" + \
                  nodes + "nodes_" + \
                  sNodeSpeed + "speed_" + \
                  sNodePause + "pause_" + \
                  sRate + "rate";

        # AsciiTraceHelper ascii;
        # Ptr<OutputStreamWrapper> osw = ascii.CreateFileStream ( (tr_name + ".tr").c_str());
        # wifiPhy.EnableAsciiAll (osw);
        ascii = ns.network.AsciiTraceHelper()
        ns.mobility.MobilityHelper.EnableAsciiAll(ascii.CreateFileStream(os.path.join(__workdir__, (tr_name + ".mob"))))

        # Ptr<FlowMonitor> flowmon;
        # FlowMonitorHelper flowmonHelper;
        # flowmon = flowmonHelper.InstallAll ();

        # NS_LOG_INFO ("Run Simulation.");
        print("Run Simulation.")

        self.WriteHeaderCsv()
        self.CheckThroughput()

        ns.core.Simulator.Stop(ns.core.Seconds(self.m_total_time))
        ns.core.Simulator.Run()

        # flowmon->SerializeToXmlFile ((tr_name + ".flowmon").c_str(), false, false);

        ns.core.Simulator.Destroy()


if __name__ == "__main__":
    v = RoutingExperiment()
    if len(sys.argv) == 1:
        v.Run()
    if len(sys.argv) == 2:
        v.Run(nSinks=(sys.argv[1]))
    if len(sys.argv) == 3:
        v.Run(nSinks=int(sys.argv[1]), txp=float(sys.argv[2]))
    if len(sys.argv) == 4:
        v.Run(nSinks=int(sys.argv[1]), txp=float(sys.argv[2]), TotalTime=int(sys.argv[3]), Nodes=int(sys.argv[4]))
    if len(sys.argv) == 5:
        v.Run(nSinks=int(sys.argv[1]),
              txp=float(sys.argv[2]),
              TotalTime=int(sys.argv[3]),
              Nodes=int(sys.argv[4]),
              CSVfileName=sys.argv[5])
