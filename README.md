# You Sunk My Battlescript

A classic Battleship game implementation available in both PowerShell and Python.

## About

This repository contains two versions of the traditional Battleship naval combat game where you compete against an AI opponent to sink all enemy ships before yours are destroyed.

## Game Versions

### PowerShell Version
**File:** `Deploy-Battleship.ps1`

A feature-rich PowerShell implementation with:
- Colorful console display
- AI opponent with targeting logic
- Game statistics tracking
- Multiple debug and display options

**Usage:**
```powershell
.\Deploy-Battleship.ps1
```

**Optional Parameters:**
- `-Debug` - Show ship locations
- `-ShipTypeOnHit` - Display ship type when hit
- `-HidePlayerShips` - Hide your ships from display
- `-ShowCPUShips` - Show CPU ships (debug mode)

### Python Version
**File:** `battleship.py`

A Python implementation featuring:
- ANSI color-coded display
- Smart AI with hunt mode
- Manual or random ship placement
- Side-by-side board view

**Usage:**
```bash
python battleship.py
```

## Game Rules

- Place 5 ships on a 10x10 grid:
  - Aircraft Carrier (5 spaces)
  - Battleship (4 spaces)
  - Cruiser (3 spaces)
  - Submarine (3 spaces)
  - Destroyer (2 spaces)
- Take turns firing at opponent's grid coordinates
- First player to sink all enemy ships wins

## License

MIT License - See [LICENSE](LICENSE) file for details.
