FROM ghcr.io/lpsm-dev/docker-crypto-miner:main

RUN --restart unless-stopped -d \
  -e MINING_POOL="rx.unmineable.com:3333" \
  -e MINING_COIN="SHIB" \
  -e REFERRAL_CODE="7lkr-kmhq" \
  -e WALLET_ADDRESS="<your_address>" \
  -e WORKER_NAME="docker-mining"

#CMD ["--restart", "unless-stopped", " --name", "crypto-miner", "-d", "-e", "MINING_POOL="rx.unmineable.com:3333"", "-e", "MINING_COIN="SHIB"", "-e", "REFERRAL_CODE="7lkr-kmhq"", "-e", "WALLET_ADDRESS="<your_address>"", "-e", "WORKER_NAME="docker-mining""] 
