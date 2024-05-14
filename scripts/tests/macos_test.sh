#!/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Start the application in the background
./NSO-RPC.app/Contents/MacOS/NSO-RPC > output.log 2>&1 &
APP_PID=$!

sleep 10
kill $APP_PID

output=$(<output.log)

if echo "$output" | grep -q "Launch error"; then
    echo -e "${RED}Test Failed!${NC}"
    echo -e "${RED}Launch error was triggered${NC}"
    echo -e "${YELLOW}Application output:"
    echo -e "${YELLOW}$(cat output.log)${NC}"
    exit 1
else
    echo -e "${GREEN}Test Passed!${NC}"
    exit 0
fi
