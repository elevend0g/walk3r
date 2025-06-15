.PHONY: all build run walk long_walk docker clean

all: run

build:
	docker build -t walk3r .

# Original functionality preserved exactly
run:
	python3 app/go_walk3r.py

# Original walk target preserved exactly  
walk:
	python3 app/go_walk3r.py

# New comprehensive analysis target
long_walk:
	@echo "🚶‍♀️ Starting comprehensive long walk analysis..."
	python3 -m app.cli --path ../walk3r/app --mode long --config walk3r.toml

# Docker version with long walk mode
long_walk_docker:
	docker build -t walk3r .
	docker run --rm \
		-v $(PWD)/../padma:/src \
		-v $(PWD)/walk3r.toml:/walk3r/walk3r.toml \
		walk3r --path /src/app --mode long --config /walk3r/walk3r.toml

# Original docker target preserved exactly
docker:
	docker run --rm -v $(PWD)/../padma:/src walk3r \
		--path /src/app --format dot --output /src/walk3r/deps

# Enhanced clean target
clean:
	@echo "🧹 Cleaning up generated files..."
	rm -f ../padma/walk3r/deps.*
	rm -f ./reports/*.json
	rm -f ./reports/*.csv  
	rm -f ./reports/*.dot
	rm -f ./reports/*.svg
	rm -f ./reports/*.png

# Help target to explain available commands
help:
	@echo "Walk3r Makefile Commands:"
	@echo "  make run        - Run basic analysis (same as original)"
	@echo "  make walk       - Run basic analysis (same as original)" 
	@echo "  make long_walk  - Run comprehensive analysis with all features"
	@echo "  make build      - Build Docker image"
	@echo "  make docker     - Run basic analysis in Docker"
	@echo "  make long_walk_docker - Run comprehensive analysis in Docker"
	@echo "  make clean      - Remove generated files"
	@echo "  make help       - Show this help message"