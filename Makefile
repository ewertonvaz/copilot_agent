.PHONY: help run

.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  help   - Show this help message"
	@echo "  run    - Start API development server with hot reload on port 8000"

run:
	uv run uvicorn sample_agent.demo:app --host 0.0.0.0 --port 8000

