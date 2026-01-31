#!/bin/bash
# Restart FinanceHub Docker Services

set -e

echo "🔄 Restarting FinanceHub services..."
echo ""

# Change to project root
cd /Users/sergi/Desktop/Projects/FinanceHub

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check status
echo ""
echo "📊 Service Status:"
echo "================"
docker-compose ps

# Check PostgreSQL
echo ""
echo "🗄️  PostgreSQL Status:"
docker-compose exec postgres pg_isready -U financehub

# Check Redis
echo ""
echo "🔴 Redis Status:"
docker-compose exec redis redis-cli ping

# Final status
echo ""
if docker-compose ps | grep -q "Up"; then
    echo "✅ All services are running!"
else
    echo "❌ Some services failed to start. Check logs with: docker-compose logs"
fi
