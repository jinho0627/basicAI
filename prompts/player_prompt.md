# 📝 player.py AI Prompt Log

This file is a log of AI prompts used when creating or modifying the `player.py` code.

## 1. Role & Objective
* Develop player physics, translation movement, and viewing rotation systems for a 3D raycasted environment.
* Implement smooth wall-sliding collisions, mouse tracking controls, and inertia.

## 2. Prompts Used
### Version 1 (Initial Player Creation)
```markdown
[Please write the prompt used for initial player creation here]
```

### Version 2 (Refinement and Debugging)
- Optimized rotation and translation speeds, mouse sensitivity limits, and implemented linear interpolation (Lerp) for smooth sliding acceleration/deceleration.

### Version 3 (Poison Slowdown effect)
```markdown
Create poison traps at random positions on the map floor that slowly drain health and slow down movement when stepped on. Create automatic doors that are normally closed but open when approached to act as shortcuts. Also create a secret room that only opens when you are almost touching the wall, containing either an A+ grade item that grants lots of score, or a cafeteria meal item that restores health. The two items must not spawn together in the same room.
```

### Version 4 (Trap Collision Range Increase)
```markdown
Show the number of remaining enemies next to the kill counter. Make the poison puddles slightly larger, and make the health drain slower. Do not place traps in one-way paths (dead-ends). Also make the auto doors open only when standing close, similar to secret rooms.
```

### Version 5 (Movement Speed Re-balancing)
```markdown
Slow down player movement speed a bit, and end the game when all enemies are defeated.
```

## 3. Feedback & Refinement
* **Poison Speed Debuff**: Created `is_poisoned` state flags within the `Player` class. During the movement update checks, if the player stands inside a poison puddle, their maximum translation speed and acceleration limits are reduced by 60% to apply the slow effect.
* **Poison Trap Bounds Expansion**: Increased player-to-trap detection range from `0.6` to `0.9` to align the physical step trigger region with the scaled visual width of the green poison puddle on the screen.
* **Controllable Inertia Tuning**: Tuned the player's movement physics. Lowered the speed limit (`max_speed`) from `5.0` to `3.8` and deceleration factors (`acceleration`) from `15.0` to `11.0` to reproduce the smooth but heavy inertial movement classic to early Doom games.
