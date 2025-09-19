import os
import sys
import json
import time
import shlex
import subprocess
import logging
import argparse
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

try:
    from zeroconf import ServiceBrowser, Zeroconf
except ImportError:
    Zeroconf = None


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Device:
    name: str
    ip: str


class MCP2ToolboxError(Exception):
    """Base exception for MCP2 Toolbox errors."""
    pass


class ConfigurationError(MCP2ToolboxError):
    """Configuration-related errors."""
    pass


class DeviceError(MCP2ToolboxError):
    """Device-related errors."""
    pass


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file with proper error handling."""
    config_path = os.path.expanduser("~/.config/console-hax/mcp2-toolbox.yml")
    
    if not os.path.exists(config_path):
        logger.debug(f"Config file not found: {config_path}")
        return {}
    
    if not yaml:
        logger.warning("PyYAML not available, cannot load config")
        return {}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            logger.debug(f"Loaded config from {config_path}")
            return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file {config_path}: {e}")
        raise ConfigurationError(f"Invalid YAML in config file: {e}")
    except Exception as e:
        logger.error(f"Error loading config file {config_path}: {e}")
        raise ConfigurationError(f"Failed to load config: {e}")


def discover(timeout_sec: float = 2.0) -> List[Device]:
    """Discover MCP2 devices using mDNS/Zeroconf."""
    devices: List[Device] = []
    
    if not Zeroconf:
        logger.warning("Zeroconf not available, cannot discover devices")
        return devices
    
    try:
        zc = Zeroconf()
        found = {}

        class Listener:
            def add_service(self, zc, t, name):
                try:
                    info = zc.get_service_info(t, name)
                    if info and info.addresses:
                        ip = ".".join(map(str, info.addresses[0]))
                        found[name] = ip
                        logger.debug(f"Discovered device: {name} at {ip}")
                except Exception as e:
                    logger.warning(f"Error processing service {name}: {e}")

        ServiceBrowser(zc, ["_http._tcp.local.", "_memcardpro._tcp.local."], Listener())
        logger.info(f"Discovering devices for {timeout_sec} seconds...")
        time.sleep(timeout_sec)
        zc.close()
        
        for name, ip in found.items():
            devices.append(Device(name=name, ip=ip))
        
        logger.info(f"Discovered {len(devices)} device(s)")
        return devices
        
    except Exception as e:
        logger.error(f"Error during device discovery: {e}")
        raise DeviceError(f"Device discovery failed: {e}")


def cmd_list():
    devs = discover()
    for d in devs:
        print(f"{d.name}\t{d.ip}")
    if not devs:
        print("No MCP2 devices found (mdns). Try manual IP.")


def gum_available() -> bool:
    return False


def cmd_ui():
    devs = discover()
    opts = [f"{d.name} ({d.ip})" for d in devs] or ["Manual IP"]
    print("Select device:")
    for i, o in enumerate(opts):
        print(f"  {i+1}. {o}")
    choice = opts[int(input("> ")) - 1]
    if choice == "Manual IP":
        target = input("Enter IP: ").strip()
    else:
        target = choice.split("(")[-1].strip(")")
    print(f"Using target {target}")
    # TODO: query HTTP API and show basic info


CH_BASE = "/home/hairglasses/Docs/console-hax"


def _env_with(overrides: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    env = os.environ.copy()
    if overrides:
        env.update({k: v for k, v in overrides.items() if v is not None})
    return env


def _run_script(path: str, args: Optional[List[str]] = None, env_overrides: Optional[Dict[str, str]] = None, background: bool = False) -> int:
    cmd = [path] + (args or [])
    if background:
        proc = subprocess.Popen(cmd, env=_env_with(env_overrides))
        print(f"started: pid={proc.pid} -> {' '.join(shlex.quote(c) for c in cmd)}")
        return 0
    res = subprocess.run(cmd, env=_env_with(env_overrides))
    return res.returncode


def _parse_kv(args: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--project", "--elf", "--build", "--pcsx2-exe"):
            if i + 1 >= len(args):
                raise SystemExit(f"missing value for {a}")
            key = a.lstrip("-").replace("-", "_")
            out[key] = args[i + 1]
            i += 2
            continue
        i += 1
    return out


def cmd_new(args: List[str]):
    if not args:
        print("usage: mcp2-toolbox new <name> [dest]")
        sys.exit(1)
    name = args[0]
    dest = args[1] if len(args) > 1 else os.path.join(CH_BASE, name)
    script = os.path.join(CH_BASE, "hg_ps2_bootstrap", "scripts", "new_visualizer.sh")
    rc = _run_script(script, [name, dest])
    sys.exit(rc)


def cmd_watch(args: List[str]):
    use_win = "--win" in args
    kv = _parse_kv(args)
    script = os.path.join(CH_BASE, "pcsx2_scaffold", "scripts", "watch_build_run_win.sh" if use_win else "watch_build_run.sh")
    env = {
        "TARGET_PROJECT": kv.get("project"),
        "TARGET_ELF": kv.get("elf"),
        "BUILD_CMD": kv.get("build"),
        "WIN_PCSX2_EXE": kv.get("pcsx2_exe"),
    }
    rc = _run_script(script, env_overrides=env, background=False)
    sys.exit(rc)


def cmd_run(args: List[str]):
    use_win = "--win" in args
    kv = _parse_kv(args)
    if use_win:
        script = os.path.join(CH_BASE, "pcsx2_scaffold", "scripts", "run_pcsx2_win.sh")
        call_args: List[str] = []
        if kv.get("elf"):
            call_args = ["--elf", kv["elf"]]
        env = {"WIN_PCSX2_EXE": kv.get("pcsx2_exe")}
        rc = _run_script(script, args=call_args, env_overrides=env)
        sys.exit(rc)
    else:
        script = os.path.join(CH_BASE, "pcsx2_scaffold", "scripts", "run_pcsx2.sh")
        call_args = []
        if kv.get("elf"):
            call_args = ["--elf", kv["elf"]]
        rc = _run_script(script, args=call_args)
        sys.exit(rc)


def cmd_hook_install(args: List[str]):
    repo = args[0] if args else os.path.join(CH_BASE, "hairglasses_ps2_visualizer_classic")
    script = os.path.join(CH_BASE, "pcsx2_scaffold", "scripts", "install_git_hooks.sh")
    rc = _run_script(script, [repo])
    sys.exit(rc)


def _cfg_path() -> str:
    return os.path.expanduser("~/.config/console-hax/mcp2-toolbox.yml")


def _cfg_load() -> Dict[str, str]:
    p = _cfg_path()
    if not os.path.exists(p) or not yaml:
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _cfg_save(cfg: Dict[str, str]) -> None:
    p = _cfg_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if yaml:
        with open(p, "w", encoding="utf-8") as f:
            f.write(yaml.safe_dump(cfg, sort_keys=True))


def cmd_config(args: List[str]):
    cfg = _cfg_load()
    defaults = {
        "project": cfg.get("project", os.path.join(CH_BASE, "hairglasses_ps2_visualizer_classic")),
        "elf": cfg.get("elf", os.path.join(CH_BASE, "hairglasses_ps2_visualizer_classic", "bin", "hg_ps2_visualizer.elf")),
        "build": cfg.get("build", "./tools/build_ee.sh --docker --fast"),
        "pcsx2_exe": cfg.get("pcsx2_exe", ""),
    }
    project = input(f"TARGET_PROJECT [{defaults['project']}]: ").strip() or defaults["project"]
    elf = input(f"TARGET_ELF [{defaults['elf']}]: ").strip() or defaults["elf"]
    build = input(f"BUILD_CMD [{defaults['build']}]: ").strip() or defaults["build"]
    pcsx2_exe = input(f"WIN_PCSX2_EXE (optional) [{defaults['pcsx2_exe']}]: ").strip() or defaults["pcsx2_exe"]
    new_cfg = {"project": project, "elf": elf, "build": build, "pcsx2_exe": pcsx2_exe}
    _cfg_save(new_cfg)
    print(f"wrote {_cfg_path()}")


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="MemCard Pro 2 helper tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcp2-toolbox list                    # List discovered devices
  mcp2-toolbox ui                      # Interactive device selection
  mcp2-toolbox new my-project          # Create new PS2 visualizer
  mcp2-toolbox watch --project ./my-project  # Watch and build project
  mcp2-toolbox run --elf ./bin/app.elf # Run project in PCSX2
  mcp2-toolbox config                  # Configure defaults
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='mcp2-toolbox 0.1.0'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--base-path',
        type=str,
        default=os.environ.get('CONSOLE_HAX_BASE', '/home/hairglasses/Docs/console-hax'),
        help='Base path for console-hax projects (default: %(default)s)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List discovered MCP2 devices')
    
    # UI command
    subparsers.add_parser('ui', help='Interactive device selection')
    
    # New command
    new_parser = subparsers.add_parser('new', help='Create new PS2 visualizer project')
    new_parser.add_argument('name', help='Project name')
    new_parser.add_argument('dest', nargs='?', help='Destination directory (optional)')
    
    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Watch and build project')
    watch_parser.add_argument('--win', action='store_true', help='Use Windows PCSX2')
    watch_parser.add_argument('--project', help='Project path')
    watch_parser.add_argument('--elf', help='ELF file path')
    watch_parser.add_argument('--build', help='Build command')
    watch_parser.add_argument('--pcsx2-exe', help='PCSX2 executable path')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run project in PCSX2')
    run_parser.add_argument('--win', action='store_true', help='Use Windows PCSX2')
    run_parser.add_argument('--elf', help='ELF file path')
    run_parser.add_argument('--pcsx2-exe', help='PCSX2 executable path')
    
    # Hook install command
    hook_parser = subparsers.add_parser('hook-install', help='Install git hooks')
    hook_parser.add_argument('repo', nargs='?', help='Repository path (optional)')
    
    # Config command
    subparsers.add_parser('config', help='Configure defaults')
    
    return parser


def main():
    """Main entry point with improved error handling."""
    try:
        parser = create_parser()
        args = parser.parse_args()
        
        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Update global base path
        global CH_BASE
        CH_BASE = args.base_path
        
        if not args.command:
            parser.print_help()
            return 1
        
        # Route to appropriate command
        if args.command == "list":
            cmd_list()
        elif args.command == "ui":
            cmd_ui()
        elif args.command == "new":
            cmd_new([args.name] + ([args.dest] if args.dest else []))
        elif args.command == "watch":
            watch_args = []
            if args.win:
                watch_args.append("--win")
            if args.project:
                watch_args.extend(["--project", args.project])
            if args.elf:
                watch_args.extend(["--elf", args.elf])
            if args.build:
                watch_args.extend(["--build", args.build])
            if args.pcsx2_exe:
                watch_args.extend(["--pcsx2-exe", args.pcsx2_exe])
            cmd_watch(watch_args)
        elif args.command == "run":
            run_args = []
            if args.win:
                run_args.append("--win")
            if args.elf:
                run_args.extend(["--elf", args.elf])
            if args.pcsx2_exe:
                run_args.extend(["--pcsx2-exe", args.pcsx2_exe])
            cmd_run(run_args)
        elif args.command == "hook-install":
            cmd_hook_install([args.repo] if args.repo else [])
        elif args.command == "config":
            cmd_config([])
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
            
        return 0
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except MCP2ToolboxError as e:
        logger.error(f"MCP2 Toolbox error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    main()


