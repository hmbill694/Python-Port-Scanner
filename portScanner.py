#!/bin/python3
import sys
import argparse
import socket
import subprocess
import threading
from datetime import datetime


def scan_port(args, serv_ip, results, port, index):
    """Set up the socket based on the optional argument and give it a default timeout"""
    if args.udp and args.tcp:
        print(
            "udp and tcp cannot both be true. Please rerun scrip with only one selected.\n"
        )
        sys.exit()
    elif args.udp:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    my_socket.settimeout(args.timeout)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    res = my_socket.connect_ex((args.target, port))

    if res == 0:
        results[index] = True
    else:
        results[index] = False

    my_socket.close()


def get_args():
    """This function will use argparse to get user input
       from the command line"""
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
    parser.add_argument(
        "-i",
        "--ip",
        help="Will get hostname by ip address EX: xx.xx.xxx.xxx",
        action="store_true",
        default=False)
    parser.add_argument(
        "-n",
        "--name",
        help="Will get hostname by name EX: www.google.com",
        action="store_true",
        default=False)

    return parser.parse_args()


def main():
    """ This port scanner will use multithreading to quickly scan the desired
        address. """
    port_range = range(1, 1000, 1)  # Range of ports to scan
    threads = []
    results = {}

    my_args = get_args()

    
    subprocess.call("clear", shell=True)  # clear shell screen
    
    if my_args.ip and my_args.name:
        print("You must get the host either by name or by IP not both. Please try again")
        sys.exit()
    elif my_args.name:
        server_ip = socket.gethostbyname(my_args.target)  # get by name
    else:
        server_ip = socket.gethostbyaddr(my_args.target)
        server_ip = server_ip[2]

    print("Scanning {} \n\n".format(server_ip))

    print("Open ports: \n")

    
    try:
        for index, port in enumerate(port_range):
            t = threading.Thread(
                target=scan_port,
                args=(
                    my_args,
                    server_ip,
                    results,
                    port,
                    index))
            threads.append(t)

        for index, thread in enumerate(threads):
            threads[index].start()

        for index, thread in enumerate(threads):
            threads[index].join()

        for res in results:
            if results[res] == True:
                print("Port {}".format(res))

    except KeyboardInterrupt:
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
