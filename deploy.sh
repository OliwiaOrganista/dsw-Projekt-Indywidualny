#!/bin/bash
# Deploy to DigitalOcean

set -e

DROPLET_IP=$1
DROPLET_USER=${2:-root}
DEPLOY_KEY=$3

if [ -z "$DROPLET_IP" ] || [ -z "$DEPLOY_KEY" ]; then
    echo "Usage: ./deploy.sh <DROPLET_IP> [USER] <DEPLOY_KEY_FILE>"
    echo "Example: ./deploy.sh 192.168.1.1 root ~/.ssh/id_rsa"
    exit 1
fi

echo "🚀 Deploying to $DROPLET_USER@$DROPLET_IP"

# SSH commands
ssh -i "$DEPLOY_KEY" "$DROPLET_USER@$DROPLET_IP" << 'EOFSH'
set -e

echo "📦 Pulling latest code..."
cd /app/file-ingestor 2>/dev/null || {
    mkdir -p /app
    cd /app
    git clone <REPO_URL> file-ingestor
    cd file-ingestor
}

git pull origin main
git fetch --all

echo "🐳 Pulling Docker images..."
docker-compose pull

echo "🔧 Restarting services..."
docker-compose down || true
docker-compose up -d

echo "⏳ Waiting for services..."
sleep 30

echo "🏥 Health check..."
curl -f http://localhost:8000/health || exit 1

echo "✅ Deployment successful!"
docker-compose ps

EOFSH

echo "✅ Deployed to $DROPLET_IP"
