#!/bin/sh
for i in $(seq 1 10)
do
    container="nmap_victim${i}_1"
    hping3 --scan 1-80 -S -d 5000 $container
    hping3 --scan 100-180 -S -d 5000 $container
done
sleep inf
