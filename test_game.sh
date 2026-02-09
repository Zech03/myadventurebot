#!/bin/bash

# Timeout game setelah 30 detik dan simulate input
timeout 30 python main.py << 'INPUT'
TestHero
1
2
3
4
1
1
n
INPUT

echo -e "\n\n=== CHECKING LOG FILE ==="
if [ -f game_log.txt ]; then
    echo "Log file found!"
    tail -20 game_log.txt
else
    echo "No log file created"
fi
