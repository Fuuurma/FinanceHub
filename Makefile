# Makefile for FinanceHub Development & Deployment

.PHONY: help install test build deploy lint clean health

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3.11
PIP := pip3
NPM := npm
DOCKER_COMPOSE := docker-compose

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[1;33m
NC := \033[0m

##@ General

help: ## Display this help message
	@echo "$(BLUE)FinanceHub Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

##@ Development Setup

install: ## Install all dependencies (backend + frontend)
	@echo "$(BLUE)Installing Backend dependencies...$(NC)"
	cd Backend && $(PIP) install -r requirements-testing.txt
	@echo "$(BLUE)Installing Frontend dependencies...$(NC)"
	cd Frontend && $(NPM) install
	@echo "$(GREEN)✓ Installation complete$(NC)"

install-backend: ## Install backend dependencies only
	@echo "$(BLUE)Installing Backend dependencies...$(NC)"
	cd Backend && $(PIP) install -r requirements-testing.txt
	@echo "$(GREEN)✓ Backend installation complete$(NC)"

install-frontend: ## Install frontend dependencies only
	@echo "$(BLUE)Installing Frontend dependencies...$(NC)"
	cd Frontend && $(NPM) install
	@echo "$(GREEN)✓ Frontend installation complete$(NC)"

##@ Development

dev: ## Start all services in development mode
	@echo "$(BLUE)Starting development environment...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo ""
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "Admin: http://localhost:8000/admin"

dev-detach: ## Start services in detached mode
	$(DOCKER_COMPOSE) up -d

dev-stop: ## Stop all services
	@echo "$(YELLOW)Stopping services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Services stopped$(NC)"

dev-restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

dev-logs: ## Show logs from all services
	$(DOCKER_COMPOSE) logs -f

dev-logs-backend: ## Show backend logs only
	$(DOCKER_COMPOSE) logs -f backend

dev-logs-frontend: ## Show frontend logs only
	$(DOCKER_COMPOSE) logs -f frontend

##@ Database

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	docker-compose exec backend python manage.py migrate
	@echo "$(GREEN)✓ Migrations complete$(NC)"

db-makemigrations: ## Create new migrations
	docker-compose exec backend python manage.py makemigrations

db-shell: ## Open database shell
	docker-compose exec postgres psql -U financehub -d finance_hub

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker-compose up -d postgres redis; \
		sleep 5; \
		docker-compose exec backend python manage.py migrate; \
		echo "$(GREEN)✓ Database reset$(NC)"; \
	fi

db-seed: ## Seed database with sample data
	@echo "$(BLUE)Seeding database...$(NC)"
	docker-compose exec backend python manage.py seed_data
	@echo "$(GREEN)✓ Database seeded$(NC)"

##@ Testing

test: ## Run all tests (backend + frontend)
	@echo "$(BLUE)Running all tests...$(NC)"
	$(MAKE) test-backend
	$(MAKE) test-frontend
	@echo "$(GREEN)✓ All tests complete$(NC)"

test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd Backend/src && pytest --cov=. --cov-report=html --cov-report=term -v
	@echo "$(GREEN)✓ Backend tests complete$(NC)"

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd Frontend && $(NPM) test -- --coverage --watchAll=false
	@echo "$(GREEN)✓ Frontend tests complete$(NC)"

test-e2e: ## Run E2E tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	cd Frontend && npx playwright test
	@echo "$(GREEN)✓ E2E tests complete$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	cd Frontend && $(NPM) test -- --watch

##@ Linting & Formatting

lint: ## Run all linters
	@echo "$(BLUE)Running all linters...$(NC)"
	$(MAKE) lint-backend
	$(MAKE) lint-frontend
	@echo "$(GREEN)✓ Linting complete$(NC)"

lint-backend: ## Lint backend code
	@echo "$(BLUE)Linting backend...$(NC)"
	cd Backend/src && black --check . && isort --check-only . && flake8 .
	@echo "$(GREEN)✓ Backend linting complete$(NC)"

lint-frontend: ## Lint frontend code
	@echo "$(BLUE)Linting frontend...$(NC)"
	cd Frontend && $(NPM) run lint
	@echo "$(GREEN)✓ Frontend linting complete$(NC)"

format: ## Format all code
	@echo "$(BLUE)Formatting all code...$(NC)"
	$(MAKE) format-backend
	$(MAKE) format-frontend
	@echo "$(GREEN)✓ Formatting complete$(NC)"

format-backend: ## Format backend code
	@echo "$(BLUE)Formatting backend...$(NC)"
	cd Backend/src && black . && isort .
	@echo "$(GREEN)✓ Backend formatting complete$(NC)"

format-frontend: ## Format frontend code
	@echo "$(BLUE)Formatting frontend...$(NC)"
	cd Frontend && $(NPM) run lint -- --fix
	@echo "$(GREEN)✓ Frontend formatting complete$(NC)"

typecheck: ## Run type checking
	@echo "$(BLUE)Running type checks...$(NC)"
	$(MAKE) typecheck-backend
	$(MAKE) typecheck-frontend
	@echo "$(GREEN)✓ Type checking complete$(NC)"

typecheck-backend: ## Type check backend
	@echo "$(BLUE)Type checking backend...$(NC)"
	cd Backend/src && mypy . || true
	@echo "$(GREEN)✓ Backend type check complete$(NC)"

typecheck-frontend: ## Type check frontend
	@echo "$(BLUE)Type checking frontend...$(NC)"
	cd Frontend && npx tsc --noEmit
	@echo "$(GREEN)✓ Frontend type check complete$(NC)"

##@ Security

security-scan: ## Run all security scans
	@echo "$(BLUE)Running comprehensive security scanner...$(NC)"
	@./scripts/security-scan.sh
	@echo "$(GREEN)✓ Security scanning complete$(NC)"

security-backend: ## Scan backend for vulnerabilities
	@echo "$(BLUE)Scanning backend...$(NC)"
	cd Backend && pip-audit --desc
	cd Backend/src && bandit -r . || true
	@echo "$(GREEN)✓ Backend security scan complete$(NC)"

security-frontend: ## Scan frontend for vulnerabilities
	@echo "$(BLUE)Scanning frontend...$(NC)"
	cd Frontend && $(NPM) audit --audit-level=moderate
	@echo "$(GREEN)✓ Frontend security scan complete$(NC)"

##@ Build

build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Build complete$(NC)"

build-backend: ## Build backend Docker image
	@echo "$(BLUE)Building backend image...$(NC)"
	docker build -f Dockerfile.backend -t financehub-backend:latest .
	@echo "$(GREEN)✓ Backend image built$(NC)"

build-frontend: ## Build frontend Docker image
	@echo "$(BLUE)Building frontend image...$(NC)"
	docker build -f Dockerfile.frontend -t financehub-frontend:latest .
	@echo "$(GREEN)✓ Frontend image built$(NC)"

build-prod: ## Build production bundles
	@echo "$(BLUE)Building production bundles...$(NC)"
	cd Frontend && $(NPM) run build
	@echo "$(GREEN)✓ Production build complete$(NC)"

##@ Deployment

deploy-staging: ## Deploy to staging
	@echo "$(BLUE)Deploying to staging...$(NC)"
	./scripts/deploy.sh staging
	@echo "$(GREEN)✓ Staging deployment complete$(NC)"

deploy-production: ## Deploy to production
	@echo "$(RED)WARNING: Deploying to PRODUCTION!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		./scripts/deploy.sh production; \
		echo "$(GREEN)✓ Production deployment complete$(NC)"; \
	fi

deploy-check: ## Check deployment status
	@echo "$(BLUE)Checking deployment status...$(NC)"
	./scripts/health-check.sh production

##@ Docker Management

docker-clean: ## Remove all Docker containers, volumes, and images
	@echo "$(YELLOW)Cleaning Docker resources...$(NC)"
	docker-compose down -v
	docker system prune -af
	@echo "$(GREEN)✓ Docker clean complete$(NC)"

docker-ps: ## Show running containers
	docker ps

docker-stats: ## Show container stats
	docker stats

##@ Health & Monitoring

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo ""
	@echo "$(GREEN)Frontend:$(NC)"
	@curl -s -o /dev/null -w "  Status: %{http_code}\n" http://localhost:3000/health || echo "  Status: DOWN"
	@echo ""
	@echo "$(GREEN)Backend:$(NC)"
	@curl -s -o /dev/null -w "  Status: %{http_code}\n" http://localhost:8000/api/health || echo "  Status: DOWN"
	@echo ""
	@echo "$(GREEN)Database:$(NC)"
	@docker-compose exec postgres pg_isready -U financehub || echo "  Status: DOWN"
	@echo ""
	@echo "$(GREEN)Redis:$(NC)"
	@docker-compose exec redis redis-cli ping || echo "  Status: DOWN"

logs-tail: ## Tail all service logs
	docker-compose logs -f

logs-backend: ## Tail backend logs
	docker-compose logs -f backend

logs-frontend: ## Tail frontend logs
	docker-compose logs -f frontend

##@ Utilities

clean: ## Clean all generated files
	@echo "$(YELLOW)Cleaning generated files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf Backend/src/.pytest_cache
	rm -rf Backend/src/htmlcov
	rm -rf Backend/src/.coverage
	rm -rf Frontend/.next
	rm -rf Frontend/node_modules/.cache
	rm -rf Frontend/coverage
	@echo "$(GREEN)✓ Clean complete$(NC)"

shell-backend: ## Open backend shell
	docker-compose exec backend bash

shell-frontend: ## Open frontend shell
	docker-compose exec frontend sh

superuser: ## Create Django superuser
	@echo "$(BLUE)Creating superuser...$(NC)"
	docker-compose exec backend python manage.py createsuperuser

collectstatic: ## Collect static files
	@echo "$(BLUE)Collecting static files...$(NC)"
	docker-compose exec backend python manage.py collectstatic --noinput
	@echo "$(GREEN)✓ Static files collected$(NC)"

##@ CI/CD

ci-test: ## Run CI pipeline locally
	@echo "$(BLUE)Running CI pipeline...$(NC)"
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) security-scan
	$(MAKE) build-prod
	@echo "$(GREEN)✓ CI pipeline complete$(NC)"

ci-validate: ## Validate CI/CD configuration
	@echo "$(BLUE)Validating CI/CD configuration...$(NC)"
	@which docker > /dev/null || (echo "$(RED)Docker not installed$(NC)" && exit 1)
	@which docker-compose > /dev/null || (echo "$(RED)Docker Compose not installed$(NC)" && exit 1)
	@echo "$(GREEN)✓ CI/CD configuration valid$(NC)"

##@ Backup & Restore

backup: ## Create backup of database and files
	@echo "$(BLUE)Creating backup...$(NC)"
	@./scripts/backup.sh

restore-list: ## List available backups
	@./scripts/restore.sh list

restore: ## Restore from backup (interactive)
	@./scripts/restore.sh

##@ Database Migrations

migrate-create: ## Create new migration
	@echo "$(YELLOW)Usage: make migrate-create NAME=migration_name$(NC)"
	@./scripts/migrate.sh create $(NAME)

migrate: ## Apply pending migrations
	@echo "$(BLUE)Applying migrations...$(NC)"
	@./scripts/migrate.sh migrate

migrate-status: ## Show migration status
	@./scripts/migrate.sh status

migrate-plan: ## Show migration plan
	@./scripts/migrate.sh plan

migrate-rollback: ## Rollback migration
	@echo "$(YELLOW)Usage: make migrate-rollback APP=app_name$(NC)"
	@./scripts/migrate.sh rollback $(APP)

##@ Performance Testing

perf-test: ## Run performance tests (headless)
	@echo "$(BLUE)Running performance tests...$(NC)"
	@echo "$(YELLOW)Install locust first: pip install locust$(NC)"
	@if command -v locust >/dev/null 2>&1; then \
		locust -f tests/performance/locustfile.py --headless --users 100 --spawn-rate 10 --run-time 5m --host $(TEST_HOST); \
	else \
		echo "$(RED)locust not found. Install with: pip install locust$(NC)"; \
		exit 1; \
	fi

perf-test-ui: ## Start performance test UI
	@echo "$(BLUE)Starting performance test UI...$(NC)"
	@echo "$(GREEN)Open http://localhost:8089 when started$(NC)"
	@if command -v locust >/dev/null 2>&1; then \
		locust -f tests/performance/locustfile.py --host $(TEST_HOST); \
	else \
		echo "$(RED)locust not found. Install with: pip install locust$(NC)"; \
		exit 1; \
	fi

##@ Cost Monitoring

cost-summary: ## Show AWS cost summary
	@echo "$(BLUE)Fetching AWS cost summary...$(NC)"
	@./scripts/cost-monitor.sh summary

cost-all: ## Show detailed AWS cost breakdown
	@echo "$(BLUE)Fetching AWS costs...$(NC)"
	@./scripts/cost-monitor.sh all

cost-report: ## Generate cost report
	@echo "$(BLUE)Generating cost report...$(NC)"
	@./scripts/cost-monitor.sh report cost-report-$$(date +%Y%m%d).txt
	@echo "$(GREEN)✓ Report generated$(NC)"

##@ Quick Operations

smoke-test: ## Run smoke tests
	@echo "$(BLUE)Running smoke tests...$(NC)"
	@./scripts/smoke-test.sh

check-health: ## Quick health check
	@./scripts/health-check.sh

##@ SLO/SLI Monitoring

slo-report: ## Generate SLO/SLI compliance report
	@echo "$(BLUE)Generating SLO report...$(NC)"
	@python3 scripts/slo-monitor.py report

slo-monitor: ## Start SLO monitoring loop (1 hour)
	@echo "$(BLUE)Starting SLO monitoring...$(NC)"
	@python3 scripts/slo-monitor.py monitor --interval 60 --duration 3600

slo-check: ## Quick SLO compliance check
	@echo "$(BLUE)Checking SLO compliance...$(NC)"
	@python3 scripts/slo-monitor.py check

##@ Incident Response

incident-monitor: ## Start automated incident monitoring
	@echo "$(BLUE)Starting incident monitoring...$(NC)"
	@./scripts/incident-response.sh monitor

incident-check: ## Single incident check
	@echo "$(BLUE)Running incident check...$(NC)"
	@./scripts/incident-response.sh check

incident-report: ## Show incident report
	@./scripts/incident-response.sh report

##@ Infrastructure Drift Detection

drift-capture: ## Capture infrastructure baseline
	@echo "$(BLUE)Capturing infrastructure state...$(NC)"
	@./scripts/drift-detect.sh capture

drift-detect: ## Detect infrastructure drift
	@echo "$(BLUE)Detecting infrastructure drift...$(NC)"
	@./scripts/drift-detect.sh detect

drift-summary: ## Show drift summary
	@./scripts/drift-detect.sh summary

##@ Advanced Operations

auto-remediate: ## Enable auto-remediation and fix issues
	@echo "$(YELLOW)⚠️  Enabling auto-remediation...$(NC)"
	@AUTO_FIX=true ./scripts/incident-response.sh remediate

monitor-all: ## Start all monitoring (SLO + incidents)
	@echo "$(BLUE)Starting comprehensive monitoring...$(NC)"
	@$(MAKE) -j2 slo-monitor incident-monitor

compliance-check: ## Full compliance check (drift + SLO + health)
	@echo "$(BLUE)Running compliance check...$(NC)"
	@echo "=== Health Check ===" && make check-health
	@echo ""
	@echo "=== SLO Check ===" && make slo-check
	@echo ""
	@echo "=== Drift Detection ===" && make drift-detect
