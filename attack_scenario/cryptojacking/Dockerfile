FROM ghcr.io/lpsm-dev/docker-crypto-miner:main

RUN --restart unless-stopped -d \
  -e MINING_POOL="rx.unmineable.com:3333" \
  -e MINING_COIN="SHIB" \
  -e REFERRAL_CODE="7lkr-kmhq" \
  -e WALLET_ADDRESS="0x989fbe40a7c62bd7f1d78266fbe23dcc8e3220be" \
  -e WORKER_NAME="docker-mining"

#CMD ["--restart", "unless-stopped", " --name", "crypto-miner", "-d", "-e", "MINING_POOL="rx.unmineable.com:3333"", "-e", "MINING_COIN="SHIB"", "-e", "REFERRAL_CODE="7lkr-kmhq"", "-e", "WALLET_ADDRESS="0x989fbe40a7c62bd7f1d78266fbe23dcc8e3220be"", "-e", "WORKER_NAME="docker-mining""] 
