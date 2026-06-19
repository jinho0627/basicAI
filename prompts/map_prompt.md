# 📝 map.py AI Prompt Log

This file is a log of AI prompts used when creating or modifying the `map.py` code.

## 1. Role & Objective
* Create a 2D grid maze for a Pygame-based 3D Doom clone game.
* Procedurally design maps and place walls using the Recursive Backtracking (DFS) algorithm.
* Compute initial spawn points for the player and graded enemies, managing spawn safety.

## 2. Prompts Used
### Version 1 (Initial Maze Design)
```markdown
I'm going to make a game called Doom in Python, and I'm Team B member: in charge of map and enemy AI.

Key tasks:
- Map design
- Wall layout

Example file in GitHub:
map.py

We'll create these files and make sure they can be merged into a single game later.
```

### Version 2 (Randomized Map Generation on Startup)
```markdown
Generate a completely new map structure every time the game runs.
```

### Version 3 (Console Encoding Error & Enemy Spawn Balance)
```markdown
1. When running the game, a UnicodeEncodeError occurs in the console map drawing part, crashing the game.
2. During the game, enemies bunch up at the map edges and aren't visible. Modify spawn positions to distribute enemies across the map.
```

### Version 4 (Poison Traps, Auto Doors, and Secret Room Layout)
```markdown
Create poison traps at random positions on the map floor that slowly drain health and slow down movement when stepped on. Create automatic doors that are normally closed but open when approached to act as shortcuts. Also create a secret room that only opens when you are almost touching the wall, containing either an A+ grade item that grants lots of score, or a cafeteria meal item that restores health. The two items must not spawn together in the same room.
```

### Version 5 (Trap Location Rules & Close Auto Doors)
```markdown
Show the number of remaining enemies next to the kill counter. Make the poison puddles slightly larger, and make the health drain slower. Do not place traps in one-way paths (dead-ends). Also make the auto doors open only when standing close, similar to secret rooms.
```

### Version 6 (Door Ranges & Trap Quantity)
```markdown
Increase the trigger range of auto doors and secret rooms to at least 1 unit, they don't open well. Reduce the number of poison traps, and increase the maximum starting/max ammo size.
```

### Version 7 (Slowly Sliding Doors)
```markdown
Make poison trap damage reduce health in integers. Make auto doors and secret rooms open slightly slower. Let the user adjust difficulty on the start screen using number keys.
```

### Version 8 (Door Range Extension)
```markdown
Increase the recognition range of all doors slightly more.
```

## 3. Feedback & Refinement
* **Procedural Map Generation**: Implemented random seeds on startup to generate uniquely shaped mazes every session. Ensured all open corridors are connected so there are no isolated/inaccessible zones.
* **Spawn Calculations**: Ensured player spawns are far away from initial enemy spawns to avoid cheap deaths right at startup.
* **Wall Varieties**: Mapped specific numeric indices to walls (e.g., 1 for Stone Wall, 2 for Blue Wall) to assist Team A's 3D raycaster and renderer.
* **Console Encoding Error Handling**: Caught encoding crashes in `print_map` on CP949 terminals by automatically replacing unicode block symbols (`██`) with ASCII characters (`##`).
* **Distributed Spawn Points**: Used `random.shuffle` on generated corridor locations to distribute spawns across the entire maze layout instead of grouping them strictly in the furthest corner.
* **Interactive Elements Layout**: Placed auto doors (4) at path junctions. Added secret doors (5) hiding isolated secret rooms containing exactly one item (either A+ or meal tray).
* **Dead-End Filtering**: Ensured poison traps are not generated in dead-end corridors (where corridor neighbors $\le 1$) so that players are never forced to step on a poison trap with no alternative route.
* **Auto Door Range Adjustments**: Decreased the auto door activation range from `2.0` to `0.8` to require closer interaction, re-adjusted to `1.0` (same as secret rooms) to make the gameplay feel smoother, and finally increased both automatic and secret door detection range thresholds to `1.5` to provide a much more comfortable interaction distance.
* **Trap Cap**: Reduced the maximum number of poison traps from `6` to `3` to keep corridors cleaner.
* **Sliding Door States**: Replaced binary open/close jumps with an `'opening'` state machine that increments door `progress` step-by-step to create a smooth sliding-up animation.
