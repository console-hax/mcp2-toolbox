import os
import sys
import json
import time
from dataclasses import dataclass
from typing import List, Optional

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


def main():
    if len(sys.argv) < 2:
        print("usage: mcp2-toolbox <list|ui>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "list":
        cmd_list()
        return
    if cmd == "ui":
        cmd_ui()
        return
    print("unknown command")


if __name__ == "__main__":
    main()


