#!/bin/sh
for i in $(seq 1 10)
do
    container="nmap_victim${i}_1"
    hping3 --scan 1-99 -S -d 5000 $container
    hping3 --scan 100-400 -S -d 5000 $container
    hping3 --scan 401-1024 -S -d 5000 $container
done
