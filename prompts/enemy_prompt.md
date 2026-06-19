# 📝 enemy.py AI Prompt Log

This file is a log of AI prompts used when creating or modifying the `enemy.py` code.

## 1. Role & Objective
* Define the Finite State Machine (FSM) behavioral patterns of enemy characters in a Python-based 3D FPS game (Doom clone).
* Implement ranged/melee attack mechanisms and projectile creation.
* Set base attributes for enemies based on grades (F, D, C) and adjust score/health multipliers per difficulty level.

## 2. Prompts Used
### Version 1 (Initial Creation & Grade-based Attributes)
```markdown
I'm going to make a game called Doom in Python, and I'm Team B member: in charge of map and enemy AI.

Key tasks:
- Enemy spawn and movement
- Game difficulty adjustment

Example file in GitHub:
enemy.py

Since I only need to do this, clean up and remove all other unrelated files. Make the enemies stronger in the order of F, D, and C grades. F grade should have double the health and double the attack power of C grade, but spawn in fewer numbers. D grade should have the same stats as C grade, but only shoot guns without melee attacks. The points for defeating them should be 300, 200, and 100 respectively. Set the health and score multipliers based on difficulty to 1, 1.5, and 2.
Change the difficulty levels to Easy, Medium, and Hard, spawning 5, 10, and 15 enemies respectively.
```

### Version 2 (Refinement, Rendering Noise Fix, and Enemy AI Improvement)
```markdown
1. Change the enemy images to the alphabets F, D, C and let's play the game with F, D, C grades attacking.
2. In the demo game, the enemies only approach depending on the direction I look at. Make them approach naturally even if I look elsewhere or watch them from a distance.
3. If I look at the wall when enemies approach, they clip inside the wall and disappear. That's wrong, so whether I look at them or not, make them follow the path just like the player so they appear naturally in my line of sight. Keep their original detection range as initially designed.
4. The enemies still clip into the wall when I look towards the wall. Make them follow the wall paths just like the player so that they show up in my vision correctly.
5. Make Grade D enemies fire air cannon-like projectiles from a distance.
6. The enemies still disappear from sight into the walls. Can you treat enemies as a solid block and render them as such so they don't visually clip inside walls?
```

### Version 3 (Fix Bug where Melee Damage was not Applied)
```markdown
While playing, it seems that attacks from enemies other than D are not being reflected in player health immediately.
```

### Version 4 (Add Strongest Enemy: Angry Professor)
```markdown
Add an "Angry Professor" boss enemy. Make him the strongest and toughest, but slow and spawn in very low numbers.
```

### Version 5 (Angry Professor Speed and HP buff)
```markdown
And for the Professor enemy, increase the movement speed slightly and increase the health a bit more.
```

## 3. Feedback & Refinement
* **Enemy FSM Implementation**: Built state machines for PATROL, CHASE, ATTACK, and DEAD and integrated with A* pathfinding to trace the player without colliding with walls.
* **Grade Differentiation**: Grade D enemies have no melee attack and shoot air cannon projectiles instead. Grade F enemies have low spawn rates but double the HP and damage of Grade C.
* **Visual/Collision Glitch Fixes**: Fixed issues where enemies spawned or walked through wall interiors by using precise grid path node tracking.
* **Melee Damage Integration**: Resolved the issue where melee damage from C/F grade enemies was not hurting the player. Added `pending_damage` inside `Enemy` and created `EnemyManager.check_melee_hits()` to fetch accumulated melee damage and apply it to player health in `main.py`.
* **Angry Professor (Grade P)**: Added a boss-grade enemy with massive base HP (originally 300, buffed to 400) and attack damage (30), but slower speed (originally 0.5, buffed to 0.8) than normal enemies. Spawns in low numbers (1~2 depending on difficulty) and fires Grade F test sheet projectiles.

