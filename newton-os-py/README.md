# Newton OS (PyQt6)

**A verified object environment where everything is an NObject.**

> "Squares and circles suck."

## Philosophy

Newton OS is built on three principles:

1. **Everything is an NObject** - Windows, files, apps, relationships, even properties
2. **Query by constraint, not by path** - Find objects by what they ARE, not where they are
3. **Continuous curves** - Squircles everywhere, no harsh corners

## Quick Start

```bash
# Install PyQt6
pip install -r requirements.txt

# Run Newton OS
python main.py
```

## Architecture

```
newton-os-py/
├── core/
│   ├── nobject.py     # The atomic unit - QObject with signals
│   ├── graph.py       # TheGraph - universal object registry
│   └── shapes.py      # Squircle geometry (superellipse)
├── shell/
│   ├── window.py      # NWindow - draggable, resizable
│   ├── dock.py        # NDock - magnifying app launcher
│   ├── menubar.py     # NMenuBar - system menus
│   └── desktop.py     # NDesktop - the shell
├── apps/
│   ├── inspector.py   # Browse TheGraph
│   └── console.py     # Newton Agent interface
└── main.py            # Entry point
```

## NObject

Every object inherits from `NObject`:

```python
from core.nobject import NObject

# Create an object
obj = NObject(object_type="MyThing")

# Set properties (tracked, verified)
obj.set_property('name', 'Example')
obj.set_property('count', 42)

# Add tags for querying
obj.add_tag('important')

# Verify against constraints (uses Newton Agent)
obj.verify({'ge': {'count': 10}})
```

## TheGraph

Query objects by constraint:

```python
from core.graph import TheGraph

# Find all windows
windows = TheGraph.query(type='NWindow')

# Find by property
titled = TheGraph.query(properties={'title': 'Console'})

# Find by constraint
large = TheGraph.query(constraint={'ge': {'width': 500}})

# Find by tag
apps = TheGraph.query(tags=['app', 'visible'])

# Complex query
result = TheGraph.query(
    type='NWindow',
    tags=['visible'],
    constraint={'lt': {'z': 100}},
    limit=10
)
```

## Squircles

All UI uses continuous-curvature squircles:

```python
from core.shapes import squircle_path, Squircle
from PyQt6.QtCore import QRectF

# Create squircle path
path = squircle_path(QRectF(0, 0, 100, 100), n=4.0)

# Or use the Squircle class
sq = Squircle(
    rect=QRectF(0, 0, 100, 100),
    n=4.5,
    fill_color=QColor(255, 255, 255),
    corner_radius=12
)
sq.draw(painter)
```

## Newton Integration

The Console app provides direct Newton Agent access:

- **ask** - Query Newton Agent
- **verify** - Verify claims
- **calculate** - Logic engine expressions
- **query** - Object graph queries

## Features

- ✓ Draggable, resizable windows
- ✓ Traffic light window controls
- ✓ Magnifying dock
- ✓ Functional menu bar
- ✓ Object inspector
- ✓ Newton Console
- ✓ Real-time graph updates
- ✓ Qt Signals for reactivity

## The Law

```
newton(current, goal) → current == goal
```

When true → execute  
When false → halt

This isn't a feature. It's the architecture.
