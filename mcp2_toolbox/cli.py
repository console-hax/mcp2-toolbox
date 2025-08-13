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
    if gum_available():
        def _gum_input(prompt: str, initial: str) -> str:
            cmd = f"gum input --placeholder {shlex.quote(prompt)} --value {shlex.quote(initial)}"
            return os.popen(cmd).read().strip() or initial
        project = _gum_input("TARGET_PROJECT", defaults["project"])
        elf = _gum_input("TARGET_ELF", defaults["elf"])
        build = _gum_input("BUILD_CMD", defaults["build"])
        pcsx2_exe = _gum_input("WIN_PCSX2_EXE (optional)", defaults["pcsx2_exe"])
    else:
        project = input(f"TARGET_PROJECT [{defaults['project']}]: ").strip() or defaults["project"]
        elf = input(f"TARGET_ELF [{defaults['elf']}]: ").strip() or defaults["elf"]
        build = input(f"BUILD_CMD [{defaults['build']}]: ").strip() or defaults["build"]
        pcsx2_exe = input(f"WIN_PCSX2_EXE (optional) [{defaults['pcsx2_exe']}]: ").strip() or defaults["pcsx2_exe"]
    new_cfg = {"project": project, "elf": elf, "build": build, "pcsx2_exe": pcsx2_exe}
    _cfg_save(new_cfg)
    print(f"wrote {_cfg_path()}")


def main():
    if len(sys.argv) < 2:
        print("usage: mcp2-toolbox <list|ui|new|watch|run|hook-install|config> [args]")
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
    if cmd == "config":
        cmd_config(sys.argv[2:])
        return
    print("unknown command")


if __name__ == "__main__":
    main()


