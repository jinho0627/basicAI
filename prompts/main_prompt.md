# 📝 main.py AI Prompt Log

This file is a log of AI prompts used when creating or modifying the `main.py` code.

## 1. Role & Objective
* Act as the Main Integration Engineer to integrate all modules (Team A's renderer/raycaster, Team B's map/enemy, and Team C's game systems) into a unified game loop.
* Handle initial state setup, game resets, keyboard/mouse input forwarding, collision responses, and game state transitions.

## 2. Prompts Used
### Version 1 (Initial Creation)
```markdown
[Please write the prompt used for initial creation here]
```

### Version 2 (Refinement and Debugging)
```markdown
[Please write the prompt used for debugging or refining here]
```

### Version 3 (Fix Bug where Melee Damage was not Applied)
```markdown
While playing, it seems that attacks from enemies other than D are not being reflected in player health immediately.
```

### Version 4 (Sprite Rendering Coordinates Integration)
```markdown
Modify the renderer call arguments to pass the player's latest information (coordinates and direction) so that enemies can be drawn in 3D space.
```

### Version 5 (Angry Professor Boss Kill Integration)
```markdown
Add an "Angry Professor" boss enemy. Make him the strongest and toughest, but slow and spawn in very low numbers.
```

### Version 6 (Poison Traps, Auto Doors, Secret Doors, and Items Integration)
```markdown
Create poison traps at random positions on the map floor that slowly drain health and slow down movement when stepped on. Create automatic doors that are normally closed but open when approached to act as shortcuts. Also create a secret room that only opens when you are almost touching the wall, containing either an A+ grade item that grants lots of score, or a cafeteria meal item that restores health. The two items must not spawn together in the same room.
```

### Version 7 (Display Remaining Enemy Count next to Kills and Balance Poison Tick Damage)
```markdown
Show the number of remaining enemies next to the kill counter. Make the poison puddles slightly larger, and make the health drain slower. Do not place traps in one-way paths (dead-ends). Also make the auto doors open only when standing close, similar to secret rooms.
```

### Version 8 (End Game when All Enemies are Defeated)
```markdown
Slow down player movement speed a bit, and end the game when all enemies are defeated.
```

### Version 9 (Start Screen Difficulty Controls & Sliding Doors Integration)
```markdown
Make poison trap damage reduce health in integers. Make auto doors and secret rooms open slightly slower. Let the user adjust difficulty on the start screen using number keys.
```

### Version 10 (Restore Ammo limit & Fix Encoding Issues)
```markdown
Reduce max ammo back to the original 50 rounds and fix character encoding issues.
```

### Version 11 (English Translation Request)
```markdown
Just make everything in English
```

### Version 12 (Dynamic Ammo limits per Difficulty)
```markdown
Increase the starting/maximum ammo count depending on difficulty (Easy: 60, Medium: 120, Hard: 200).
```

### Version 13 (Ammo limit adjustment)
```markdown
There are too many bullets, make it 30, 60, 90.
```

### Version 14 (Ammo limit reduction)
```markdown
Make the bullet counts 25, 50, 75.
```

## 3. Feedback & Refinement
* **Melee Damage Integration**: Solved the issue where melee damage was not hurting the player by calling `enemy_manager.check_melee_hits()` every frame and sending the result to `self.game_systems.health.take_damage`.
* **Renderer Call Parameters**: Updated arguments for `self.renderer.render_frame` to include the player's 2D world coordinates (px, py) and orientation angle (self.player.angle).
* **Boss Kill Score Integration**: Configured Grade P (Angry Professor) boss kill events to trigger `"boss"` score gains, giving a larger multiplier and bonus score.
* **Special Elements Integration**: Integrated `self.game_map.update_doors` to handle automatic/secret sliding door animations. Programmed the player's poison status check in the update loop to apply `take_poison_damage` ticks. Added item pickup checks on the player coordinate (A+ and meal tray), playing sounds and applying score/health changes accordingly.
* **HUD Remaining Enemies Display**: Passed `len(enemies)` to `gs.draw()` within the rendering cycle to display the live count.
* **Poison Tick Damage Speed Balancing**: Adjusted poison damage rate from `12.0 HP/sec` to `5.0 HP/sec` to prevent players from losing health too quickly.
* **Game Victory Cleared Condition**: Set the game to transition to game-over state with `is_victory = True` as soon as `len(active_enemies) == 0`.
* **English Translation**: Replaced all Korean console logs, menu selections, and game difficulty configs in the terminal print statements to English to make the output clean and universal, eliminating CP949 encoding errors entirely.
* **Start Screen Transition Reset**: Modified the transition from `STATE_START` to call `self.game_systems._reset()`, which ensures that the selected difficulty is properly applied to compile the correct starting and maximum ammo limits for the player before spawning the player and enemies.
* **Ammo Count Fine-Tuning**: Tuned starting/maximum ammo values to 25 (Easy), 50 (Medium), and 75 (Hard) per user feedback.

