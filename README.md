# Soul Sister Simulator

A high-level Magic: The Gathering deck simulator focused on the "Soul Sisters" archetype, built for Commander (EDH) gameplay. This project simulates deck performance, life gain, triggers, and board development over multiple games, providing detailed statistics and insights for deck optimization.

## Features
- **Magic: The Gathering Simulation**: Models a full Commander deck, including lands, creatures, artifacts, enchantments, and a commander in the command zone.
- **Trigger System**: Supports complex triggers (e.g., life gain, ETB, death, custom events) and a stack-based resolution system.
- **Mana System**: Realistic mana production, land drops, and spell casting logic.
- **Commander Support**: Handles commander casting, tax, and command zone rules.
- **Statistics Engine**: Runs many simulations and outputs per-turn averages for life, board state, hand size, graveyard, and damage dealt.
- **Configurable**: Easily adjust simulation parameters and decklist.
- **Verbose and Silent Modes**: Choose between detailed logs or summary statistics.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/soul-sister-simulator.git
   cd soul-sister-simulator
   ```
2. (Optional) Create a virtual environment and activate it.
3. Install requirements (if any):
   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Single Simulation (Verbose or Silent)
Run a single game simulation for a specified number of turns:
```sh
python -m soul_sister_simulator.simulation_run --turns 10 --verbose
```
- Use `--verbose` for detailed logs (default is silent summary).

### Batch Simulation (Statistics)
Run many simulations and print per-turn averages:
```sh
python -m soul_sister_simulator.simulation_run --turns 10 --many
```
- The number of games is set in `config.py` (`NUM_SIMULATIONS`).

### Configuration
- **Decklist**: Edit `decklist.py` and `cards_def.py` to change the deck.
- **Simulation Parameters**: Edit `config.py` to adjust number of simulations, trigger probabilities, and other constants.

## Project Structure
- `soul_sister_simulator/`
  - `simulation_run.py` — Main simulation entry point
  - `game_state.py` — Game state, turn logic, and trigger stack
  - `actions.py` — All card and trigger actions
  - `cards_def.py` — Card database and definitions
  - `decklist.py` — Decklist and deck builder
  - `config.py` — Simulation and deck configuration
  - `hand.py`, `deck.py`, `battlefield.py`, etc. — Core game objects

## Contributing
Contributions, bug reports, and feature requests are welcome! Please open an issue or submit a pull request.

## License
MIT License. See [LICENSE](LICENSE) for details.

---

**Soul Sister Simulator** is an independent project and is not affiliated with or endorsed by Wizards of the Coast or Magic: The Gathering. 