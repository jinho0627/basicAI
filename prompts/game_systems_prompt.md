# 📝 game_systems.py AI Prompt Log

This file is a log of AI prompts used when creating or modifying the `game_systems.py` code.

## 1. Role & Objective
* Design UI & systems (weapon, ammo, health, score, HUD overlays) for a Doom clone.
* Build synth audio generators using pygame's sound buffer to generate classic 8-bit sound effects.
* Provide an state interface for start menu, playing HUD, and game over screens.

## 2. Prompts Used
### Version 1 (Initial Creation)
```markdown
[Please write the prompt used for initial creation here]
```

### Version 2 (Refinement and Debugging)
- Improved weapon fire cooldown, added sound mixer exceptions, and fixed HUD HP/AMMO bar ratio displays.

### Version 3 (Poison Trap Visual Indicator & Item Collection)
```markdown
Create poison traps at random positions on the map floor that slowly drain health and slow down movement when stepped on. Create automatic doors that are normally closed but open when approached to act as shortcuts. Also create a secret room that only opens when you are almost touching the wall, containing either an A+ grade item that grants lots of score, or a cafeteria meal item that restores health. The two items must not spawn together in the same room.
```

### Version 4 (Display Remaining Enemy Count next to Kills and Balance Poison Tick Damage)
```markdown
Show the number of remaining enemies next to the kill counter. Make the poison puddles slightly larger, and make the health drain slower. Do not place traps in one-way paths (dead-ends). Also make the auto doors open only when standing close, similar to secret rooms.
```

### Version 5 (Increase Max Ammo limit)
```markdown
Increase the trigger range of auto doors and secret rooms to at least 1 unit, they don't open well. Reduce the number of poison traps, and increase the maximum starting/max ammo size.
```

### Version 6 (Victory Screen upon All Enemies Defeated)
```markdown
Slow down player movement speed a bit, and end the game when all enemies are defeated.
```

### Version 7 (Integer HP Display & Difficulty Selection with Number Keys)
```markdown
Make poison trap damage reduce health in integers. Make auto doors and secret rooms open slightly slower. Let the user adjust difficulty on the start screen using number keys.
```

### Version 8 (Restore Max Ammo limit to 50 rounds)
```markdown
Reduce max ammo back to the original 50 rounds and fix character encoding issues.
```

### Version 9 (Difficulty-dependent Ammo Limit)
```markdown
Increase the starting/maximum ammo count depending on difficulty (Easy: 60, Medium: 120, Hard: 200).
```

### Version 10 (Ammo limit adjustment)
```markdown
There are too many bullets, make it 30, 60, 90.
```

### Version 11 (Ammo limit reduction)
```markdown
Make the bullet counts 25, 50, 75.
```

## 3. Feedback & Refinement
* **Green Poison Screen Flash overlay**: Implemented the `_poison_flash` timer and `take_poison_damage(dmg)` in `HealthSystem`. While the player is poisoned, health is drained over time, and a semi-transparent green overlay (using `poison_alpha`) flashes on the HUD instead of the red damage flash.
* **Meal Tray & A+ Score Integration**: Programmed meal trays to invoke `health.heal(40)` along with a pickup sound, and A+ grade items to award 1000 points.
* **HUD Remaining Enemies**: Added a `remaining_enemies` parameter to `HUD.draw` and `GameSystems.draw` to display the active enemy count in the format `KILLS: X (LEFT: Y)`.
* **Poison Tick Damage Speed Balancing**: Adjusted poison damage rate from `12.0 HP/sec` to `5.0 HP/sec` to prevent players from losing health too quickly.
* **Ammo Count Capacity Restoration**: Restored the starting/maximum ammo size (`MAX_AMMO`) back to `50` rounds per user request.
* **Victory Screen & Audio**: Added victory screen routing. When all enemies are eliminated (`is_victory = True`), the game over screen shows a yellow `"VICTORY!"` title instead of the red `"GAME OVER"`, and plays a positive `score` sound instead of a player death noise.
* **Integer HP HUD Rendering**: Since poison damage can result in fractional HP, applied `int(math.ceil(health.hp))` to display health as clean integer digits.
* **Start Screen Difficulty Controls**: Enabled keys `1`, `2`, and `3` on the start screen (`StartScreen.handle_event`) to select `'EASY'`, `'MEDIUM'`, and `'HARD'` respectively, dynamically updating `gs.difficulty` and showing them color-coded (Green for Easy, Yellow for Medium, Red for Hard).
* **Difficulty-dependent Ammo Scaling**: Modified the `Weapon` constructor to receive game difficulty and configure maximum/starting ammo dynamically (adjusted to 25 for Easy, 50 for Medium, 75 for Hard per user request). Preserved difficulty setting inside `GameSystems._reset()` instead of defaulting it back to `'MEDIUM'`.


