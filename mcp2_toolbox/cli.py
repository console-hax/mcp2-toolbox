import os
import sys
import json
import time
import shlex
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Dict

try:
    import yaml
except Exception:
    yaml = None

try:
    from zeroconf import ServiceBrowser, Zeroconf
except Exception:
    Zeroconf = None


@dataclass
class Device:
    name: str
    ip: str


def load_config():
    path = os.path.expanduser("~/.config/console-hax/mcp2-toolbox.yml")
    if not os.path.exists(path):
        return {}
    if not yaml:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def discover(timeout_sec: float = 2.0) -> List[Device]:
    devices: List[Device] = []
    if not Zeroconf:
        return devices
    zc = Zeroconf()
    found = {}

    class Listener:
        def add_service(self, zc, t, name):
            info = zc.get_service_info(t, name)
            if info and info.addresses:
                ip = ".".join(map(str, info.addresses[0]))
                found[name] = ip

    ServiceBrowser(zc, ["_http._tcp.local.", "_memcardpro._tcp.local."], Listener())
    time.sleep(timeout_sec)
    zc.close()
    for name, ip in found.items():
        devices.append(Device(name=name, ip=ip))
    return devices


def cmd_list():
    devs = discover()
    for d in devs:
        print(f"{d.name}\t{d.ip}")
    if not devs:
        print("No MCP2 devices found (mdns). Try manual IP.")


def gum_available() -> bool:
    return os.system("which gum >/dev/null 2>&1") == 0


def cmd_ui():
    devs = discover()
    opts = [f"{d.name} ({d.ip})" for d in devs] or ["Manual IP"]
    if gum_available():
        choice = os.popen(f"echo '{os.linesep.join(opts)}' | gum choose").read().strip()
    else:
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


def main():
    if len(sys.argv) < 2:
        print("usage: mcp2-toolbox <list|ui|new|watch|run|hook-install> [args]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "list":
        cmd_list()
        return
    if cmd == "ui":
        cmd_ui()
        return
    if cmd == "new":
        cmd_new(sys.argv[2:])
        return
    if cmd == "watch":
        cmd_watch(sys.argv[2:])
        return
    if cmd == "run":
        cmd_run(sys.argv[2:])
        return
    if cmd == "hook-install":
        cmd_hook_install(sys.argv[2:])
        return
    print("unknown command")


if __name__ == "__main__":
    main()


