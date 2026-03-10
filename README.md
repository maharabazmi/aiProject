# A* Escape: The Living Network

A pygame-based game featuring intelligent pathfinding and grid-based navigation. Navigate through a dynamic grid while avoiding enemies that use A* pathfinding algorithms to pursue you.

## Features

- **Grid-based Gameplay**: Navigate a 30x20 tile grid with walls and interactive elements
- **Intelligent Enemies**: Enemies equipped with A* pathfinding algorithm for dynamic pursuit
- **Genetic Map Generation**: Procedurally generated levels using genetic algorithms
- **High-Performance Rendering**: 60 FPS gameplay with pygame
- **Minimalist UI**: Clean, high-contrast visual design optimized for clarity

## Requirements

- Python 3.7+
- pygame
- NumPy (for genetic map generation)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aiiip.git
   cd aiiip
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install pygame numpy
   ```

## Running the Game

Start the game by running:
```bash
python main.py
```

The game window will open with the title "A* Escape: The Living Network" at 1200x800 resolution running at 60 FPS.

## Project Structure

- `main.py` - Main game loop and entry point
- `gamestate.py` - Game state management
- `grid.py` - Grid structure and pathfinding logic
- `player.py` - Player character implementation
- `enemy.py` - Enemy AI and behavior
- `genetic_map_gen.py` - Procedural level generation using genetic algorithms
- `settings.py` - Game configuration and constants

## Game Controls

*(Add your control scheme here once implemented)*

## Features in Development

- [ ] Player movement controls
- [ ] Enemy AI pathfinding
- [ ] Map generation and obstacles
- [ ] UI improvements
- [ ] Game states (menu, gameplay, game over)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
