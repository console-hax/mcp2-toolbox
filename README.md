# mcp2-toolbox

Unified CLI for console-hax workflows and MemCard Pro 2 device management.

## Features

- **Device Discovery**: Automatic mDNS/Zeroconf discovery of MCP2 devices
- **Project Management**: Scaffold new PS2 visualizer projects
- **Build Automation**: Watch and build projects with automatic PCSX2 integration
- **Configuration Management**: Interactive setup and persistent configuration
- **Cross-Platform**: Support for both Linux and Windows development workflows

## Installation

### From Source

```bash
git clone <repository-url>
cd mcp2-toolbox
pip install -e .
```

### Dependencies

The tool requires Python 3.7+ and the following packages:

- `zeroconf` - For device discovery
- `requests` - For HTTP operations
- `psutil` - For system monitoring
- `PyYAML` - For configuration management

## Quick Start

1. **Discover devices**:

   ```bash
   mcp2-toolbox list
   ```

2. **Configure defaults**:

   ```bash
   mcp2-toolbox config
   ```

3. **Create a new project**:

   ```bash
   mcp2-toolbox new my-visualizer
   ```

4. **Watch and build**:

   ```bash
   mcp2-toolbox watch --project ./my-visualizer
   ```

## Commands

### Device Management

- `mcp2-toolbox list` - List discovered MCP2 devices via mDNS
- `mcp2-toolbox ui` - Interactive device selection interface

### Project Management

- `mcp2-toolbox new <name> [dest]` - Create new PS2 visualizer project
- `mcp2-toolbox watch [options]` - Watch and build project automatically
- `mcp2-toolbox run [options]` - Run project in PCSX2 emulator

### Configuration

- `mcp2-toolbox config` - Interactive configuration setup
- `mcp2-toolbox hook-install [repo]` - Install git hooks for auto-build

## Configuration

Configuration is stored in `~/.config/console-hax/mcp2-toolbox.yml`:

```yaml
project: "/path/to/default/project"
elf: "/path/to/default/elf"
build: "./tools/build_ee.sh --docker --fast"
pcsx2_exe: "/path/to/pcsx2.exe"  # Windows only
```

## Environment Variables

- `CONSOLE_HAX_BASE` - Override default base path for console-hax projects
- `MCP2_TOOLBOX_VERBOSE` - Enable verbose logging

## Usage Examples

### Basic Usage

```bash
# List available devices
mcp2-toolbox list

# Create and configure a new project
mcp2-toolbox new my-project
mcp2-toolbox config

# Watch for changes and auto-build
mcp2-toolbox watch --project ./my-project --elf ./my-project/bin/app.elf
```

### Advanced Usage

```bash
# Use custom base path
mcp2-toolbox --base-path /custom/path list

# Enable verbose logging
mcp2-toolbox --verbose watch --project ./my-project

# Windows development
mcp2-toolbox watch --win --pcsx2-exe "C:\PCSX2\pcsx2.exe"
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Quality

```bash
# Format code
black mcp2_toolbox/

# Lint code
flake8 mcp2_toolbox/

# Type checking
mypy mcp2_toolbox/
```

## Troubleshooting

### Device Discovery Issues

- Ensure devices are on the same network
- Check firewall settings for mDNS traffic
- Verify Zeroconf service is running

### Build Issues

- Ensure Docker is running (for Docker-based builds)
- Check project paths are correct
- Verify PCSX2 installation path

### Configuration Issues

- Check YAML syntax in config file
- Ensure all required paths exist
- Verify file permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add license information]

## Changelog

### v0.1.0

- Initial release
- Device discovery via mDNS/Zeroconf
- Project scaffolding and management
- Build automation with PCSX2 integration
- Configuration management
