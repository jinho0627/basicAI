# 📝 renderer.py AI Prompt Log

This file is a log of AI prompts used when creating or modifying the `renderer.py` code.

## 1. Role & Objective
* Render projected 3D wall columns, calculate texture scales, and draw billboarding sprites (enemies, projectiles, items, traps) in the correct perspective.
* Avoid fish-eye distortion, handle screen-clipping edge noise, and perform Z-buffering to correctly mask sprites behind walls.

## 2. Prompts Used
### Version 1 (Initial Renderer)
```markdown
[Please write the prompt used for initial creation here]
```

### Version 2 (Sprite Rendering & Edge Flicker Glitch Fixes)
```markdown
1. Add functionality to render enemies and enemy projectiles in 3D space on the game window.
2. When rotating the camera, if an enemy sprite reaches the screen edges, they stretch to cover the entire height and flicker. Please fix this noise issue.
```

### Version 3 (Angry Professor Boss Sprite & F Sheet Projectiles)
```markdown
Add an "Angry Professor" boss enemy. Make him the strongest and toughest, but slow and spawn in very low numbers.
```

### Version 4 (Poison Trap, Sliding Door, and Item Sprites)
```markdown
Create poison traps at random positions on the map floor that slowly drain health and slow down movement when stepped on. Create automatic doors that are normally closed but open when approached to act as shortcuts. Also create a secret room that only opens when you are almost touching the wall, containing either an A+ grade item that grants lots of score, or a cafeteria meal item that restores health. The two items must not spawn together in the same room.
```

### Version 5 (Scale up Poison Puddle Sprites)
```markdown
Show the number of remaining enemies next to the kill counter. Make the poison puddles slightly larger, and make the health drain slower. Do not place traps in one-way paths (dead-ends). Also make the auto doors open only when standing close, similar to secret rooms.
```

### Version 6 (Sliding Door vertical scale adjustments)
```markdown
Make poison trap damage reduce health in integers. Make auto doors and secret rooms open slightly slower. Let the user adjust difficulty on the start screen using number keys.
```

## 3. Feedback & Refinement
* **Billboarding Sprite Projection**: Cached Grade C, D, and F enemy images as pre-rendered surfaces. Sorted items by distance (Painter's Algorithm) and scaled their size dynamically to draw them in 3D perspective.
* **1D Z-Buffer Occlusion**: Used a list of wall-slice distances (calculated during raycasting) to discard sprite slices that lie behind walls, preventing sprites from bleeding through walls.
* **Fish-Eye/Flicker Edge Fixes**: Fixed the issue where sprites inflated to cover the entire screen height when they approached the lateral edges ($90^\circ$ relative to player). Replaced simple orthogonal projection with Euclidean distance scaling and skipped drawing sprites whose relative camera angles fell outside the Field of View plus a minor safety threshold.
* **Angry Professor & Test Sheets**: Designed a unique boss texture (bald hair, red tie, and glasses) for the Angry Professor (P) and created flying paper sprites representing the Grade F exam sheet projectiles he shoots.
* **Flat Floor Elements**: Implemented floor alignments for items (Gold rotating A+ coins and meal tray plates) and poison traps (flat green puddles) by setting the vertical render offset to anchor them to the wall bottom coordinates (`bottom_y`) and applying a flat squash multiplier to traps.
* **Dynamic Door textures**: Drawn automatic doors (4) with dark blue steel textures and secret doors (5) with standard gray brick textures identical to normal walls to act as camouflage.
* **Trap Visual Expansion**: Increased the horizontal and vertical scaling factors (`sf_w` from `0.7` to `1.1`, and `sf_h` from `0.3` to `0.4`) to make traps clearly recognizable and match the player slow-down zone.
* **Sliding Door Animation rendering**: Read the cell coordinate status from `game_map`. When a door is in the `'opening'` state, calculated the vertical draw limits (`draw_end`) to shrink upwards proportional to the door opening progress, creating a smooth vertical slide.
