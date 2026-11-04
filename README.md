# Portal Solver Editor SDK - Python Bindings

**[EN]** | **[[RU]](README_RU.md)**

**pse-sdk-python** - Official Python bindings for **Portal Solver Editor (PSE) SDK**, the official toolkit _(SDK)_ for programmatic work with the in-game editor of **Portal: Solver**

The library provides a **high-level Python API** over the low-level **[C SDK](https://github.com/RootTool0/pse-sdk)**, allowing you to build **external level editors**, **automation tools**, **plugins**, **unusual custom levels**, and **utilities** that run in sync with the running game in real time

All the low-level details - shared memory, ring buffers, atomics, byte offsets - are hidden behind a clean Python interface

## Installation

```bash
pip install pse-sdk-python
```

**Requirements:**
- **Windows** (the game is Windows-only)
- **Python 3.10+**
- **Portal: Solver** must be running

## Quick start

A basic scenario: connect to the game, create a floor, a button and a door. Make the button open the door

```python
import pse

# Connect to the running game
pse.initialize()

# Build a floor
pse.StaticMesh.create(
    location=(0, 0, -100),
    scale=(10, 10, 1),
    mesh=pse.Mesh.FACE,
    material=pse.Material.FLOOR_WHITE,
)

# Create a button and a door
button = pse.Button()
button.create(location=(200, 200, -100))

door = pse.Door()
door.create(location=(-150, 0, -100))

# Open the door when the button is pressed
@button.on_element_changed()
def on_button_changed(state):
    door.state = state

# Main loop
while True:
    pse.poll_events()
```

## What you can do

- **Elements:** doors, buttons, triggers, lasers, faith plates, panels, stairs, cubes, lamps, windows, elevators and more
- **Meshes:** static and dynamic geometry with materials
- **Events:** callbacks for element state changes
- **Player:** position, rotation, spawn, kill
- **Solver Gun & flashlight:** give/take, state control, actions
- **Game:** cheats, gravity, level initialization

## Project structure

- `src/pse/` - Python package source
- `src/pse/pse.dll` - bundled **PSE SDK** dynamic library
- `examples/` - working Python examples

## Documentation

A detailed description of the architecture, element specifications and usage guides can be found in the **[PSE SDK Python Documentation](https://roottool0.github.io/pse-sdk-python/index.html?lang=en)** section

## Related projects

- **[pse-sdk](https://github.com/RootTool0/pse-sdk)** - the original **C SDK** (core library, headers, documentation)
- **[PSE SDK Documentation](https://roottool0.github.io/pse-sdk/index.html?lang=en)** - full architecture, element specs and usage guides

## Links and feedback

- **Portal: Solver** page on **GameJolt**: [GameJolt](https://gamejolt.com/games/PortalSolver/898591)
- Download ready releases: [Releases](https://github.com/RootTool0/pse-sdk-python/releases)
- Report a bug _(Bug Report)_: [Issues](https://github.com/RootTool0/pse-sdk-python/issues)
- Contact **RootTool**:
  - **Telegram (channel/blog)**: [RootTool Blog](https://t.me/RootToolBlog)
  - **Telegram (DM)**: [@RootTool0](https://t.me/RootTool0)
  - **Discord**: `.roottool` (or `RootTool#5776`)
  - **YouTube**: [RootTool](https://www.youtube.com/@RTEdits0)
