# smartmine
Playable console minesweeper game programmed in python. The game includes an algorithmical solver.

# Current status
## Human game 
- Human game is working
- **TODO**: add mines flagging functionality
## Solver
- Solver is working quite good and fast.
- **TODO**: use max number of mines and mines already found for calculations, specially at the game ending
- **TODO**: improve guessing probabiity algorithm. Probabilities are not "real" probabilities
## Benchmark
- Benchmarking is working and showing victory rate
- Last victory rate based on 100 games of each kind

|Difficulty|Size|Mines|Success percent|
|--|--|--|--|
|Easy|9x9|10|85%|
|Intermediate|16x16|40|77%|
|Expert|16x30|99|33%|

- **TODO**: automate large benchmarks for thousands of games

# Installation
- Clone the repository
- Install termcolor with sudo pip install termcolor or sudo easy_installtermcolor if you want colored display
- python smartmine.py / pypy smartmine.py

# Use
- Please enter the width (> 0), height (> 0) and mines (>= 0)
- Select H for human game, M for computer game or B for benchmarking
Human tile marking:
- Enter the position to mark as x y (e.g. 0 0). Origin of coordinates is top left (rows, columns)
- The game will tell you when you win or loose
