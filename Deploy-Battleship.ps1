# PowerShell Battleship Game
# Features: CPU AI Player
# TODO: Add "Sonar" feature to reveal a 3x3 area once per game

# Debug mode - pass this parameter to see ship locations
param(
  [switch]$Debug,
  [switch]$ShipTypeOnHit,
  [switch]$HidePlayerShips,
  [switch]$ShowCPUShips
)

# Game Configuration
$BOARD_SIZE = 10
$SHIPS = @(
    @{Name="Aircraft Carrier"; Size=5},
    @{Name="Battleship"; Size=4},
    @{Name="Cruiser"; Size=3},
    @{Name="Submarine"; Size=3},
    @{Name="Destroyer"; Size=2}
)

# Game State
$PlayerBoard = @{}
$CPUBoard = @{}
$PlayerShips = @{}
$CPUShips = @{}
$GameStats = @{
    PlayerHits = 0
    PlayerMisses = 0
    CPUHits = 0
    CPUMisses = 0
    PlayerShipsSunk = 0
    CPUShipsSunk = 0
    Turns = 0
}

# Colors for display
$Colors = @{
    Water = "Blue"
    Hit = "Red"
    Miss = "Yellow"
    Ship = "Green"
    Sunk = "DarkRed"
    Text = "White"
    Border = "Gray"
}

function Initialize-Boards {
    # Initialize empty boards
    for ($row = 0; $row -lt $BOARD_SIZE; $row++) {
        for ($col = 0; $col -lt $BOARD_SIZE; $col++) {
            $coord = "$([char](65+$row))$($col+1)"
            $PlayerBoard[$coord] = @{State="Water"; Ship= $null}
            $CPUBoard[$coord] = @{State="Water"; Ship= $null}
        }
    }
    
    # Place ships for both players - use script scope variables
    Place-Ships -Board $PlayerBoard -ShipHash $PlayerShips
    Place-Ships -Board $CPUBoard -ShipHash $CPUShips
}

function Place-Ships {
    param($Board, $ShipHash)
    
    $random = New-Object System.Random
    
    foreach ($ship in $SHIPS) {
        $placed = $false
        while (-not $placed) {
            $orientation = $random.Next(0, 2)  # 0 = horizontal, 1 = vertical
            $startRow = $random.Next(0, $BOARD_SIZE)
            $startCol = $random.Next(0, $BOARD_SIZE)
            
            if ($orientation -eq 0) {  # Horizontal
                if ($startCol + $ship.Size -le $BOARD_SIZE) {
                    $valid = $true
                    for ($i = 0; $i -lt $ship.Size; $i++) {
                        $coord = "$([char](65+$startRow))$($startCol+$i+1)"
                        if ($Board[$coord].State -ne "Water") {
                            $valid = $false
                            break
                        }
                    }
                    if ($valid) {
                        $shipCoords = @()
                        for ($i = 0; $i -lt $ship.Size; $i++) {
                            $coord = "$([char](65+$startRow))$($startCol+$i+1)"
                            $Board[$coord] = @{State="Ship"; Ship=$ship.Name}
                            $shipCoords += $coord
                        }
                        $ShipHash[$ship.Name] = @{Size=$ship.Size; Hits=0; Coordinates=$shipCoords}
                        $placed = $true
                    }
                }
            } else {  # Vertical
                if ($startRow + $ship.Size -le $BOARD_SIZE) {
                    $valid = $true
                    for ($i = 0; $i -lt $ship.Size; $i++) {
                        $coord = "$([char](65+$startRow+$i))$($startCol+1)"
                        if ($Board[$coord].State -ne "Water") {
                            $valid = $false
                            break
                        }
                    }
                    if ($valid) {
                        $shipCoords = @()
                        for ($i = 0; $i -lt $ship.Size; $i++) {
                            $coord = "$([char](65+$startRow+$i))$($startCol+1)"
                            $Board[$coord] = @{State="Ship"; Ship=$ship.Name}
                            $shipCoords += $coord
                        }
                        $ShipHash[$ship.Name] = @{Size=$ship.Size; Hits=0; Coordinates=$shipCoords}
                        $placed = $true
                    }
                }
            }
        }
    }
}

function Show-Animation {
    param($Message, $Delay = 500)
    
    Write-Host "`n" -NoNewline
    foreach ($char in $Message.ToCharArray()) {
        Write-Host $char -NoNewline -ForegroundColor $Colors.Text
        Start-Sleep -Milliseconds 50
    }
    Write-Host "`n"
    Start-Sleep -Milliseconds $Delay
}

function Display-Board {
    param($Board, $Title)
    
    Write-Host "`n$Title`n" -ForegroundColor $Colors.Text
    Write-Host "   " -NoNewline
    for ($i = 1; $i -le $BOARD_SIZE; $i++) {
        Write-Host " $i " -NoNewline -ForegroundColor $Colors.Border
    }
    Write-Host ""
    
    for ($row = 0; $row -lt $BOARD_SIZE; $row++) {
        Write-Host " $([char](65+$row)) " -NoNewline -ForegroundColor $Colors.Border
        for ($col = 0; $col -lt $BOARD_SIZE; $col++) {
            $coord = "$([char](65+$row))$($col+1)"
            $cell = $Board[$coord]
            
            switch ($cell.State) {
                "Water" { $color = $Colors.Water; $symbol = "~" }
                "Hit" { $color = $Colors.Hit; $symbol = "X" }
                "Miss" { $color = $Colors.Miss; $symbol = "O" }
                "Ship" { 
                    # Show ships based on parameters and which board is being displayed
                    $showShips = $false
                    if ($Title -eq "Your Board" -and (-not $HidePlayerShips -or $Debug)) {
                        $showShips = $true
                    }
                    if ($Title -eq "CPU Board" -and ($ShowCPUShips -or $Debug)) {
                        $showShips = $true
                    }
                    
                    if ($showShips) {
                        $color = $Colors.Ship
                        $symbol = $cell.Ship.Substring(0,1).ToUpper()
                    } else {
                        $color = $Colors.Water; $symbol = "~"
                    }
                }
                "Sunk" { $color = $Colors.Sunk; $symbol = "#" }
            }
            
            Write-Host " $symbol " -NoNewline -ForegroundColor $color
        }
        Write-Host ""
    }
    Write-Host ""
}

function Display-GameStats {
    Write-Host "=== GAME STATISTICS ===" -ForegroundColor $Colors.Text
    Write-Host "Turns: $($GameStats.Turns)" -ForegroundColor $Colors.Text
    Write-Host "Player: $($GameStats.PlayerHits) hits, $($GameStats.PlayerMisses) misses" -ForegroundColor $Colors.Text
    Write-Host "CPU:    $($GameStats.CPUHits) hits, $($GameStats.CPUMisses) misses" -ForegroundColor $Colors.Text
    Write-Host "Ships Sunk - Player: $($GameStats.PlayerShipsSunk)/5, CPU: $($GameStats.CPUShipsSunk)/5" -ForegroundColor $Colors.Text
    Write-Host "=======================" -ForegroundColor $Colors.Text
}

function Get-Player-Move {
    while ($true) {
        $move = Read-Host "Enter your target (e.g., A1): "
        $move = $move.ToUpper()
        
        if ($move -match "^[A-J][1-9]|10$") {
            if ($CPUBoard[$move].State -eq "Water" -or $CPUBoard[$move].State -eq "Ship") {
                return $move
            } else {
                Write-Host "You already targeted that coordinate!" -ForegroundColor $Colors.Miss
            }
        } else {
            Write-Host "Invalid coordinate! Use format like A1, B5, J10" -ForegroundColor $Colors.Miss
        }
    }
}

function Get-CPU-Move {
    # Basic AI: Hunt mode if hit recently, otherwise random
    $random = New-Object System.Random
    
    # Check if we have a recent hit to hunt around
    $recentHits = $PlayerBoard.GetEnumerator() | Where-Object { $_.Value.State -eq "Hit" }
    if ($recentHits) {
        # Try to find adjacent cells to hit
        foreach ($hit in $recentHits) {
            $coord = $hit.Key
            $row = [int][char]$coord[0] - 65
            $col = [int]$coord.Substring(1) - 1
            
            $directions = @(@(0,1), @(0,-1), @(1,0), @(-1,0))
            foreach ($dir in $directions) {
                $newRow = $row + $dir[0]
                $newCol = $col + $dir[1]
                
                if ($newRow -ge 0 -and $newRow -lt $BOARD_SIZE -and $newCol -ge 0 -and $newCol -lt $BOARD_SIZE) {
                    $newCoord = "$([char](65+$newRow))$($newCol+1)"
                    if ($PlayerBoard[$newCoord].State -eq "Water" -or $PlayerBoard[$newCoord].State -eq "Ship") {
                        return $newCoord
                    }
                }
            }
        }
    }
    
    # Random move if no good hunting spots
    while ($true) {
        $row = $random.Next(0, $BOARD_SIZE)
        $col = $random.Next(0, $BOARD_SIZE)
        $coord = "$([char](65+$row))$($col+1)"
        
        if ($PlayerBoard[$coord].State -eq "Water" -or $PlayerBoard[$coord].State -eq "Ship") {
            return $coord
        }
    }
}

function Process-Move {
    param($Board, $Coord, $Ships, $IsPlayerMove)
    
    $cell = $Board[$Coord]
    
    if ($cell.State -eq "Ship") {
        # Hit!
        $Board[$Coord].State = "Hit"
        $shipName = $cell.Ship
        $Ships[$shipName].Hits++
        
        if ($IsPlayerMove) {
            $GameStats.PlayerHits++
            if ($ShipTypeOnHit) {
                Show-Animation "HIT! You hit the CPU's $shipName!" 300
            } else {
                Show-Animation "HIT!" 300
            }
        } else {
            $GameStats.CPUHits++
            if ($ShipTypeOnHit) {
                Show-Animation "CPU HIT! Your $shipName was hit!" 300
            } else {
                Show-Animation "CPU HIT!" 300
            }
        }
        
        # Check if ship is sunk
        if ($Ships[$shipName].Hits -eq $Ships[$shipName].Size) {
            foreach ($shipCoord in $Ships[$shipName].Coordinates) {
                $Board[$shipCoord].State = "Sunk"
            }
            
            if ($IsPlayerMove) {
                $GameStats.CPUShipsSunk++
                Show-Animation "SUNK! You sank the CPU's $shipName!" 500
            } else {
                $GameStats.PlayerShipsSunk++
                Show-Animation "SUNK! CPU sank your $shipName!" 500
            }
        }
        
        return $true
    } else {
        # Miss
        $Board[$Coord].State = "Miss"
        
        if ($IsPlayerMove) {
            $GameStats.PlayerMisses++
            Show-Animation "MISS!" 200
        } else {
            $GameStats.CPUMisses++
            Show-Animation "CPU MISS!" 200
        }
        
        return $false
    }
}

function Check-Game-Over {
    if ($GameStats.CPUShipsSunk -eq 5) {
        Show-Animation "VICTORY! You sank all CPU ships!" 1000
        return $true
    }
    if ($GameStats.PlayerShipsSunk -eq 5) {
        Show-Animation "DEFEAT! CPU sank all your ships!" 1000
        return $true
    }
    return $false
}

function Show-Welcome {
    Clear-Host
    Write-Host "    =================" -ForegroundColor $Colors.Text
    Write-Host "        BATTLESHIP   " -ForegroundColor $Colors.Text
    Write-Host "    =================" -ForegroundColor $Colors.Text
    Write-Host ""
    Show-Animation "Preparing for naval combat..." 800
    Show-Animation "Deploying ships..." 600
    Show-Animation "Enemy detected..." 400
    Start-Sleep -Milliseconds 500
}

function Show-Game-End {
    Clear-Host
    Write-Host ""
    Write-Host "    GAME OVER" -ForegroundColor $Colors.Text
    Write-Host "    =========" -ForegroundColor $Colors.Text
    Write-Host ""
    
    Display-GameStats
    
    if ($GameStats.CPUShipsSunk -eq 5) {
        Write-Host ""
        Show-Animation "Congratulations Admiral! You are victorious!" 1000
    } else {
        Write-Host ""
        Show-Animation "Better luck next time, Captain!" 1000
    }
    
    Write-Host ""
    Write-Host "Final Boards:" -ForegroundColor $Colors.Text
    Display-Board -Board $PlayerBoard -Title "Your Board"
    Display-Board -Board $CPUBoard -Title "CPU Board"
}

function Show-Debug-Info {
    if (-not $Debug) { return }
    
    Write-Host "=== DEBUG MODE ===" -ForegroundColor "Magenta"
    Write-Host "Player Ships:" -ForegroundColor "Magenta"
    foreach ($shipName in $PlayerShips.Keys) {
        Write-Host "  $shipName`: $($PlayerShips[$shipName].Coordinates -join ', ')" -ForegroundColor "Magenta"
    }
    Write-Host "CPU Ships:" -ForegroundColor "Magenta"
    foreach ($shipName in $CPUShips.Keys) {
        Write-Host "  $shipName`: $($CPUShips[$shipName].Coordinates -join ', ')" -ForegroundColor "Magenta"
    }
    Write-Host "=================" -ForegroundColor "Magenta"
}

# Main Game Loop
function Start-Game {
    Show-Welcome
    Initialize-Boards
    
    while ($true) {
        Clear-Host
        $GameStats.Turns++
        
        Write-Host "Turn $($GameStats.Turns)" -ForegroundColor $Colors.Text
        Display-GameStats
        
        Display-Board -Board $PlayerBoard -Title "Your Board" -ShowPlayerShips $true
        Display-Board -Board $CPUBoard -Title "CPU Board" -ShowPlayerShips $false
        
        Show-Debug-Info
        
        # Player's turn
        $playerMove = Get-Player-Move
        $hit = Process-Move -Board $CPUBoard -Coord $playerMove -Ships $CPUShips -IsPlayerMove $true
        
        if (Check-Game-Over) { break }
        
        # CPU's turn
        $cpuMove = Get-CPU-Move
        Show-Animation "CPU targeting $cpuMove..." 300
        $hit = Process-Move -Board $PlayerBoard -Coord $cpuMove -Ships $PlayerShips -IsPlayerMove $false
        
        if (Check-Game-Over) { break }
        
        Start-Sleep -Milliseconds 800
    }
    
    Show-Game-End
}

# Start the game
Start-Game