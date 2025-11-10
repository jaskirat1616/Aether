#!/bin/bash
# Comprehensive test script for Aether

set -e

echo "🧪 Aether Test Suite"
echo "===================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry not found. Please install Poetry first.${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Please run this script from the project root${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Installing dependencies...${NC}"
poetry install --quiet

echo ""
echo -e "${YELLOW}🧪 Running Python unit tests...${NC}"
if poetry run pytest tests/ -v; then
    echo -e "${GREEN}✅ All Python tests passed!${NC}"
else
    echo -e "${RED}❌ Some Python tests failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}🔍 Testing CLI...${NC}"
if poetry run aether scan --interface simulate > /dev/null 2>&1; then
    echo -e "${GREEN}✅ CLI test passed!${NC}"
else
    echo -e "${RED}❌ CLI test failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}🌐 Testing API import...${NC}"
if poetry run python -c "from aether import Aether; a = Aether('simulate'); a.close()" 2>/dev/null; then
    echo -e "${GREEN}✅ API import test passed!${NC}"
else
    echo -e "${RED}❌ API import test failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""
echo "Next steps:"
echo "1. Start API server: cd services/api && poetry run uvicorn main:app --reload"
echo "2. Start dashboard: cd viz/web && npm install && npm run dev"
echo "3. Open http://localhost:3000 in your browser"

