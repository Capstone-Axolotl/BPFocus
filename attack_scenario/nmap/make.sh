#!/bin/bash
cat > docker-compose.yml <<EOF
version: "3"
services:
    ping:
        build:
            context: .
            dockerfile: Dockerfile
        stdin_open: true
        tty: true
        cap_add:
        - ALL
        entrypoint: ["/ping_start.sh"]
$(for c in {1..10}
do
cat <<EOC
    victim$c:
        image: ubuntu:latest
        entrypoint: ["sleep", "inf"]
EOC
done
)
EOF

cat << EOF > ping_start.sh
#!/bin/sh
for i in \$(seq 1 10)
do
    container="nmap_victim\${i}_1"
    hping3 --scan 1-99 -S -d 5000 \$container
    hping3 --scan 100-400 -S -d 5000 \$container
    hping3 --scan 401-1024 -S -d 5000 \$container
done
EOF

