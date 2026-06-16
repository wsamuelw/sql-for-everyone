# How to Multiply — Monster Battle Arena

## Overview

A single-file HTML game where kids learn multiplication by battling cute monsters. Correct answers power attacks; wrong answers take damage. Monsters evolve and new ones unlock as kids progress through times tables.

**Target age:** 6-8 years old
**Platform:** Single HTML file, deployable to GitHub Pages (same pattern as `how-to-spell`)
**Input:** Multiple choice (3 options per question)

## Core Loop

1. Kid sees a multiplication question (e.g. "2 x 6 = ?")
2. Kid picks one of 3 answer buttons
3. Correct = their monster attacks the enemy, enemy HP drops
4. Wrong = the enemy attacks, kid's HP drops
5. Beat the enemy = earn coins + XP, next enemy appears
6. Kid's HP reaches 0 = retry the level (no harsh punishment)

Each enemy defeated = 1 level up. One question = one battle action. Fast, simple, repeatable.

## Screens

### 1. Title Screen

- Game logo/title
- "Battle!" button (main mode)
- "Collection" button (view monsters)
- Simple animated monster mascot on screen

### 2. Battle Screen

**Top bar:**
- Current level number
- Coins earned
- Current times table (e.g. "x1 Table")

**Battle area (middle):**
- Player monster (left) with name + HP bar
- Enemy monster (right) with name + HP bar
- "VS" divider
- Attack animations: correct = monster lunges forward, shake enemy; wrong = enemy lunges, shake player

**Question panel (bottom):**
- The multiplication question in large text
- 3 answer buttons (coloured, tappable)
- Correct answer is randomly placed among the 3 options
- On correct: green flash, "+attack" text, sound effect
- On wrong: red flash, enemy attack animation

**Victory state:**
- "YOU WIN!" overlay
- Coins earned, XP gained
- "Next Battle" button

**Defeat state:**
- "Try Again?" overlay
- No coin penalty, just retry
- Encouraging message ("Almost! You'll get it next time!")

### 3. Monster Collection Screen

- Grid of monsters (3 columns)
- Owned monsters: coloured border, name, level, star rating
- Locked monsters: dashed border, "???", "Beat Level X to unlock"
- Tap a monster to see its stats and evolution progress

### 4. Times Table Select (unlocked progressively)

- Shows which tables are unlocked (bright) vs locked (dimmed)
- Start with x1 table unlocked
- Unlock x2 after reaching level 5, x5 after level 10, x10 after level 15, etc.
- Kid can pick which unlocked table to practice

## Monster System

### Starting Monster

- **Flamey** — a cute fire blob monster, given at start
- Stats: HP 10, Attack 2

### Unlockable Monsters (earned at boss levels)

| Monster | Emoji | Unlock Level | Type | HP | Attack |
|---------|-------|-------------|------|-----|--------|
| Flamey | 🔥 | Start | Fire | 10 | 2 |
| Rocky | 🪨 | Level 5 (boss) | Earth | 12 | 2 |
| Sparky | ⚡ | Level 10 (boss) | Electric | 8 | 4 |
| Frosty | ❄️ | Level 15 (boss) | Ice | 14 | 3 |
| Shadow | 👻 | Level 20 (boss) | Dark | 10 | 5 |

### Evolution

- Each monster has 2 evolution stages
- Evolves after 20 battles used
- Evolution increases stats by ~50% and changes appearance (emoji swap + name change, e.g. "Flamey" -> "Mega Flamey")
- Evolution progress tracked per monster

### Monster Selection

- Kid picks which owned monster to bring into battle
- Different monsters have different HP/attack tradeoffs

## Difficulty Progression

### Times Table Unlock Order

1. x1 table (always unlocked)
2. x2 table (unlock at level 5)
3. x5 table (unlock at level 10)
4. x10 table (unlock at level 15)
5. x3 table (unlock at level 20)
6. x4 table (unlock at level 25)
7. x6 table (unlock at level 30)
8. x7 table (unlock at level 35)
9. x8 table (unlock at level 40)
10. x9 table (unlock at level 45)
11. x11 table (unlock at level 50)
12. x12 table (unlock at level 55)

### Enemy Scaling

- Enemy HP increases with level (base 8 + level x 1.5)
- Enemy attack increases with level (base 1 + level x 0.3)
- Questions only come from the currently selected times table
- Wrong answer options are close to the correct answer (e.g. for 2x6=12, wrong options might be 10 and 14)
- Wrong answer generation: pick 2 numbers within +/- 4 of the correct answer, never the correct answer itself, never negative

### Boss Battles

- Every 5 levels is a boss battle
- Boss has 2x normal HP and 1.5x attack
- Beating a boss unlocks a new monster
- Boss has a unique appearance (larger emoji, special border)

## Coins & Rewards

- Win a battle: earn 10 coins
- Boss battle: earn 25 coins
- Streak bonus: 3+ correct in a row = +5 bonus coins per correct answer

### What Coins Buy (future expansion, not v1)

- Cosmetic items (hats, accessories for monsters)
- Monster skins
- v1 scope: coins are displayed but shop is locked with "Coming Soon!"

## Visual Style

**Theme:** Cartoon Battle — bright, fun, expressive
- Cute round monsters with big eyes
- Comic-style attack effects ("POW!", "BOOM!")
- Bright primary colours on a grassy field background
- Large touch targets for small fingers
- Satisfying animations on correct/wrong answers

**Colour palette:** TBD (deferred to implementation)

**Typography:** System fonts, large and readable (min 16px for answers, 24px+ for questions)

## Technical Requirements

- Single self-contained HTML file (no external dependencies)
- No backend, no data collection, no ads
- All game state in localStorage (progress, coins, monster levels)
- Responsive: works on phone, tablet, desktop
- Touch-friendly: buttons minimum 44px tap target
- Offline capable (no network requests after initial load)
- Accessible: sufficient colour contrast, readable font sizes
- Sound effects optional (can be added later, not v1)

## File Structure

Single file: `index.html`

## Out of Scope (v1)

- Sound effects / music
- Shop / cosmetic items
- Multiplayer
- Parent dashboard / progress reports
- Account system
- Different question formats (typing, drag-and-drop)
