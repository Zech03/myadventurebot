#!/bin/bash

# Test 1: Test save feature dengan menu
echo "=== TEST 1: Buat game baru dan save ==="
(
    sleep 1
    echo "2"        # New Game
    sleep 0.5
    echo "SaveTest" # Nama pemain
    sleep 0.5
    echo "1"        # Recruit 1
    sleep 0.5
    echo "2"        # Recruit 2
    sleep 0.5
    echo "11"       # Lanjutkan ke petualangan
    sleep 2
) | timeout 15 python main.py > /dev/null 2>&1

echo "Checking save files..."
ls -la saves/ 2>/dev/null | tail -5

echo -e "\n=== TEST 2: Check game log ==="
tail -10 game_log.txt

