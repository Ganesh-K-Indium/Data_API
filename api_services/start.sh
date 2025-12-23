#!/bin/bash

# Data Sources API - Startup Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Data Sources REST API Server${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/installed" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
    touch venv/installed
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ Warning: .env file not found${NC}"
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}Please edit .env file with your configuration before running again${NC}"
    exit 1
fi

# Check for required environment variables
source .env
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}✗ Error: OPENAI_API_KEY not set in .env${NC}"
    echo -e "${YELLOW}Please set your OpenAI API key in .env file${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment configured${NC}"
echo ""

# Check if Qdrant is running (optional check)
QDRANT_URL=${QDRANT_URL:-"http://localhost:6333"}
if command -v curl &> /dev/null; then
    if curl -s "$QDRANT_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Qdrant is accessible at $QDRANT_URL${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Cannot reach Qdrant at $QDRANT_URL${NC}"
        echo -e "${YELLOW}  Make sure Qdrant is running for ingestion features${NC}"
    fi
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Starting API Server...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get host and port from environment or use defaults
HOST=${API_HOST:-"0.0.0.0"}
PORT=${API_PORT:-"8000"}

echo -e "${GREEN}📍 API Server:${NC} http://$HOST:$PORT"
echo -e "${GREEN}📚 API Docs:${NC} http://localhost:$PORT/docs"
echo -e "${GREEN}🔍 Health Check:${NC} http://localhost:$PORT/health"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the server
python main.py
