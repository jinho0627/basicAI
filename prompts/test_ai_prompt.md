# 📝 test_ai.py AI Prompt Log

This file is a log of AI prompts used when creating or modifying the `test_ai.py` code.

## 1. Role & Objective
* Write unit tests (Unit Test) to verify the core algorithms (Procedural Map generation, A* pathfinding, Enemy FSMs, and difficulty multipliers) of Team B's modules.
* Ensure code safety and feature integrity before merging features or opening pull requests.

## 2. Prompts Used
### Version 1 (Initial Test Suite)
```markdown
Create a unit test file named test_ai.py that validates B team's files (map.py, enemy.py, pathfinding.py).
```

### Version 2 (Melee Damage Accumulation Test)
```markdown
While playing, it seems that attacks from enemies other than D are not being reflected in player health immediately.
```

### Version 3 (Angry Professor Boss Spawn Ratio Tests)
```markdown
Add an "Angry Professor" boss enemy. Make him the strongest and toughest, but slow and spawn in very low numbers.
```

### Version 4 (Poison Trap, Auto/Secret Door, and Item Spawns Verification)
```markdown
Create poison traps at random positions on the map floor that slowly drain health and slow down movement when stepped on. Create automatic doors that are normally closed but open when approached to act as shortcuts. Also create a secret room that only opens when you are almost touching the wall, containing either an A+ grade item that grants lots of score, or a cafeteria meal item that restores health. The two items must not spawn together in the same room.
```

### Version 5 (Trap Placement Filters and Door Proximities)
```markdown
Show the number of remaining enemies next to the kill counter. Make the poison puddles slightly larger, and make the health drain slower. Do not place traps in one-way paths (dead-ends). Also make the auto doors open only when standing close, similar to secret rooms.
```

### Version 6 (Updated Proximity Ranges)
```markdown
Increase the trigger range of auto doors and secret rooms to at least 1 unit, they don't open well. Reduce the number of poison traps, and increase the maximum starting/max ammo size.
```

### Version 7 (Sliding Door Delay Verification)
```markdown
Make poison trap damage reduce health in integers. Make auto doors and secret rooms open slightly slower. Let the user adjust difficulty on the start screen using number keys.
```

### Version 8 (Proximity & Boss HP Test Updates)
```markdown
Update tests to reflect Grade P HP buff (400) and door detection range extension (1.5).
```

## 3. Feedback & Refinement
* **Test Verification Scope**:
  * Randomized map seed reproducibility.
  * Outer border wall checks and player/enemy spawn tile safety.
  * A* path availability and correct node connections.
  * Enemy grade base parameters.
  * Spawn volumes per difficulty (5 for Easy, 10 for Medium, 15 for Hard) and correct damage multipliers.
  * Melee damage compilation in `pending_damage` and verification that `check_melee_hits()` clears the value.
  * Angry Professor (P) attributes (buffed to HP 400, Attack 30) and spawn ratio bounds checking.
  * **Interactive Element Validations**:
    * Auto door range triggers (opening inside 1.5, setting cell grid to 0, transitioning state to open, and locking back to closed/4 after delay).
    * Secret doors trigger check (only opening when distance < 1.5).
    * Secret room validation (ensuring exactly one item type, either A+ or H, is placed on the secret room floor).
    * Dead-end check (`test_traps_no_dead_ends`) ensuring no poison trap spawns in cells with $\le 1$ walkable neighbor.
    * Sliding animation verification: calling `update_doors` twice with a simulated sleep interval to confirm the state changes from `'closed'` to `'opening'` and finally to `'open'`.
* **Execution Utility**: Added `unittest.main()` block so the developer can execute tests directly.

