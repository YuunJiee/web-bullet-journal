#!/bin/bash

# ==========================================
# Jotly (Web Bullet Journal) - Development Script
# ==========================================

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Jotly Development Server...${NC}"

# Check if conda environment 'bullet-journal' exists
if conda info --envs | grep -q "bullet-journal"; then
    echo -e "${GREEN}✓ Found conda environment 'bullet-journal'${NC}"
else
    echo -e "${RED}✗ Conda environment 'bullet-journal' not found!${NC}"
    echo "Please run: conda env create -f environment.yml"
    exit 1
fi

# Activate conda environment and run server
# Note: Using 'conda run' allows us to run commands within the env without needing to explicitly activate it in the bash session
echo -e "${BLUE}Checking for pending database migrations...${NC}"
conda run -n bullet-journal python manage.py makemigrations --dry-run --check > /dev/null 2>&1
MIGRATION_STATUS=$?

if [ $MIGRATION_STATUS -ne 0 ]; then
    echo -e "${RED}Pending migrations detected. Running migrations...${NC}"
    conda run -n bullet-journal python manage.py migrate
fi

echo -e "${GREEN}Starting Django built-in server at http://127.0.0.1:8000${NC}"
echo -e "${BLUE}(Press Ctrl+C to stop)${NC}"

# Run the server
conda run -n bullet-journal --no-capture-output python manage.py runserver 0.0.0.0:8000
