#! /bin/python3

import subprocess


COLOR_RESET = "\033[0m"
COLOR_RED = "\033[31m"
COLOR_BLUE = "\033[34m"


def exec(cmd: list[str]) -> None:
    print(f"{COLOR_BLUE}running: {' '.join(cmd)}{COLOR_RESET}")
    subprocess.run(cmd)


def read_selection(max_value: int) -> int:
    while True:
        try:
            selection = input("selection: ")
            parsed = int(selection)
            if parsed < 1 or parsed > max_value:
                raise Exception(f"invalid selection: {parsed}")
            return parsed
        except Exception as ex:
            print(f"{COLOR_RED}error: {ex}{COLOR_RESET}")


def upgrade_system() -> None:
    print(f"{COLOR_BLUE}upgrading system")
    exec(["sudo", "apt-get", "update", "-y"])
    exec(["sudo", "apt-get", "upgrade", "-y"])


def install_base_packages() -> None:
    print(f"{COLOR_BLUE}installing base packages")
    packages = ["rsync", "kakoune", "nginx", "docker.io", "docker-compose"]
    exec(["sudo", "apt-get", "install", "-y"] + packages)


def setup_nginx() -> None:
    print(f"{COLOR_BLUE}installing nginx{COLOR_RESET}")
    exec(["sudo", "apt-get", "install", "-y", "nginx"])


def setup_firewall() -> None:
    print(f"{COLOR_BLUE}installing firewall{COLOR_RESET}")
    exec(["sudo", "apt-get", "install", "-y", "ufw"])

    print(f"{COLOR_BLUE} - closing all incoming connections{COLOR_RESET}")
    exec(["sudo", "ufw", "default", "deny", "incoming"])

    print(f"{COLOR_BLUE} - closing all outgoing connections{COLOR_RESET}")
    exec(["sudo", "ufw", "default", "deny", "outgoing"])

    print(f"{COLOR_BLUE} - openging ports specific ports{COLOR_RESET}")
    exec(["sudo", "ufw", "allow", "80"])   # http port.
    exec(["sudo", "ufw", "allow", "443"])  # https port.
    exec(["sudo", "ufw", "limit", "22"])   # ssh port with rate-limiting.

    print(f"{COLOR_BLUE} - enabling firewall{COLOR_RESET}")
    exec(["sudo", "ufw", "enable"])


def set_timezone() -> None:
    print(f"{COLOR_BLUE}setting system timezone to UTC")
    exec(["sudo", "timedatectl", "set-timezone", "UTC"])


def main() -> None:
    steps = {
        1: ("Upgrade system", upgrade_system),
        2: ("Install base packages", install_base_packages),
        3: ("Set timezone (UTC)", set_timezone),
        4: ("Setup Nginx", setup_nginx),
        5: ("Setup firewall", setup_firewall),
    }

    print("Please select an option:")
    for i, (name, _func) in steps.items():
        print(f"{i}. {name}")

    selection = read_selection(len(steps))
    target_step = steps[selection]
    if target_step is None:
        raise Exception(f"failed to run selection: {selection}")

    target_step[1]()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n{COLOR_BLUE}ctrl+c: exiting...{COLOR_RESET}")
    except Exception as ex:
        print(f"{COLOR_RED}error: {ex}.{COLOR_RESET}")
