# mcp2-toolbox

Unified CLI for console-hax workflows.

## Install

```bash
pip install -e .
```

## Commands

- mcp2-toolbox list — mDNS discovery for devices (MCP2 / HTTP)
- mcp2-toolbox ui — interactive target selection (uses gum if available)
- mcp2-toolbox new <name> [dest] — scaffold a new PS2 visualizer from classic template
- mcp2-toolbox watch [--win] [--project P] [--elf E] [--build CMD] [--pcsx2-exe PATH]
- mcp2-toolbox run [--win] [--elf E] [--pcsx2-exe PATH]
- mcp2-toolbox hook-install [repo] — installs post-commit to auto build+run on Windows

Defaults assume base path at `/home/hairglasses/Docs/console-hax`.


