# 📝 pathfinding.py AI Prompt Log

This file is a log of AI prompts used when creating or modifying the `pathfinding.py` code.

## 1. Role & Objective
* Implement the A* search algorithm to calculate the shortest path from a start position (enemy coordinates) to a goal position (player coordinates) on a 2D grid maze.
* Optimize path search execution to ensure smooth frame rates in the main game loop.
* Coordinate with the enemy FSM Chase state to follow path nodes in real-time.

## 2. Prompts Used
### Version 1 (Initial Shortest Path Logic)
```markdown
I'm going to make a game called Doom in Python, and I'm Team B member: in charge of map and enemy AI.

Key tasks:
- Enemy tracking/chase algorithm

Example file in GitHub:
pathfinding.py

We'll create these files and make sure they can be merged into a single game later.
```

## 3. Feedback & Refinement
* **Heuristic Choice**: Adopted the Manhattan Distance heuristic because players and enemies only move orthogonally (up, down, left, right) on the 2D grid map with no diagonal routes.
* **Performance Enhancements**: Used the `heapq` module to maintain the open set as a minimum heap, maximizing lookup speeds for nodes with the lowest estimated $F$ cost.
* **Fallbacks**: Returned an empty path list (`[]`) in case the player is unreachable (e.g. enclosed rooms or out-of-bound coordinates) to prevent crashes.
