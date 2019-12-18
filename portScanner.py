#!/bin/python3
import sys
import argparse
import socket
import subprocess
import threading
from datetime import datetime


def scan_port(args, serv_ip, results, port, index):
    """
        Set up the socket based on the optional argument and give it a default timeout

        Parameters
        -------------------------
        args: namespace containing arguments from command line
        serv_ip: formatted address for socket
        results: dictionary
        port: int
        index: int

        Returns
        -------------------------
        results
            {int: bool, ...}
    """

    if args.udp and args.tcp:   # check if the optional argument are both true, this cannot be allowed
        print(
            "udp and tcp cannot both be true. Please rerun scrip with only one selected.\n"
        )
        sys.exit()

    elif args.udp:              # check if optional flag -u/-udp was entered
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    else:     # either -t/--tcp has been entered or if nothing has been entered default to TCP connection
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    my_socket.settimeout(args.timeout)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # see if port can be connected to
    res = my_socket.connect_ex((args.target, port))

    if res == 0:
        results[index] = True
    else:
        results[index] = False

    my_socket.close()


def get_args():
    """
        using arg parse get input from command line

        Parameters
        -------------------------
        void

        Returns
        -------------------------
        results
        namespace [target:str, timeout:int, udp:boolean, tcp:boolean, ip:boolean, name:boolean]
    """
    parser = argparse.ArgumentParser(
        description="""This will scan ports of a given website/IP Address, the only truly required argument is the target,
        timeout is defaulted to 1 second if not entered.
        The socket type can be either TCP or UDP. If one is not specified it will default to TCP""")

    parser.add_argument(
        "target", help="The name of the website you are scanning", type=str)

    parser.add_argument(
        "timeout",
        help="Set the timeout time for the program",
        type=int,
        default=1)

    parser.add_argument(
        "-u",
        "--udp",
        help="Set to scan UDP connections",
        action="store_true",
        default=False)

    parser.add_argument(
        "-t",
        "--tcp",
        help="Set to scan TCP connections",
        action="store_true",
        default=False)

    return parser.parse_args()


def main():
    """
        Use threads to speed up the port scanner.

        Parameters
        -------------------------
        void

        Returns
        -------------------------
        results
        void
    """
    port_range = range(1, 1001, 1)  # Range of ports to scan
    threads = []
    results = {}

    my_args = get_args()

    subprocess.call("clear", shell=True)  # clear shell screen

    try:

        # get by name if a website name is entered
        server_ip = socket.gethostbyname(my_args.target)

        print("Scanning {} \n".format(server_ip))
        print("Open ports: \n")

        for index, port in enumerate(port_range):  # populate the threads
            t = threading.Thread(
                target=scan_port,
                args=(
                    my_args,
                    server_ip,
                    results,
                    port,
                    index))
            threads.append(t)

        for index, thread in enumerate(threads):  # run the threads
            threads[index].start()

        for index, thread in enumerate(
                threads):  # lock them to prevent critical section errors
            threads[index].join()

        for res in results:
            if results[res]:
                print("Port {}".format(res))

    except KeyboardInterrupt:   # abort
        print("Program Aborted...")
        sys.exit()

    except socket.gaierror:
        print("Could not resolve Hostname...")
        sys.exit()

    except socket.error:
        print("Could not connect.. ")
        sys.exit()


if __name__ == "__main__":
    main()
