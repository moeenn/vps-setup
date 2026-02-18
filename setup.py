#! /bin/python3

import subprocess
import os
import sys


COLOR_RESET = "\033[0m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"


def exec(cmd: list[str]) -> None:
    print(f"{COLOR_BLUE}running: {' '.join(cmd)}{COLOR_RESET}")
    subprocess.run(cmd)


def confirm(message: str) -> bool:
    user_input = input(f"{message}? [Y/n] ")
    return user_input.strip().lower() in ["y", "yes"]


def read_selection(max_value: int) -> int:
    while True:
        try:
            selection = input("selection: ")
            if selection.strip() in ["q", "Q"]:
                print(f"{COLOR_BLUE}exiting...{COLOR_RESET}")
                sys.exit(0)

            parsed = int(selection)
            if parsed < 1 or parsed > max_value:
                raise Exception(f"invalid selection: {parsed}")
            return parsed
        except Exception as ex:
            print(f"{COLOR_RED}error: {ex}{COLOR_RESET}")


def read_hostname() -> str:
    while True:
        try:
            hostname = input("enter hostname: ")
            trimmed = hostname.strip()
            if len(trimmed) == 0:
                raise Exception("A hostname is required: please enter a valid value")
        except Exception as ex:
            print(f"{COLOR_RED}error: {ex}{COLOR_RESET}")


def read_app_port() -> int:
    reserved_ports = [22, 80, 443]
    while True:
        try:
            port = input("application port: ")
            parsed = int(port)
            if parsed in reserved_ports:
                raise Exception(f"cannot use port {parsed}, it is a reserved port")
        except Exception as ex:
            print(f"{COLOR_RED}error: {ex}{COLOR_RESET}")


def upgrade_system() -> None:
    print(f"{COLOR_BLUE}upgrading system")
    exec(["sudo", "apt-get", "update", "-y"])
    exec(["sudo", "apt-get", "upgrade", "-y"])


def install_base_packages() -> None:
    print(f"{COLOR_BLUE}installing base packages")
    packages = ["rsync", "kakoune", "docker.io", "docker-compose"]
    exec(["sudo", "apt-get", "install", "-y"] + packages)


def get_nginx_host_config(hostname: str, app_port: int) -> str:
    return f"""
server {{
    server_name {hostname};
    location / {{
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_pass http://127.0.0.1:{app_port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}

    gzip on;
    gzip_types text/css application/javascript image/png image/jpeg image/webp;
    gzip_proxied any;
}}
    """.strip()


def remove_default_nginx_site_config(sa_base_path: str, se_base_path) -> None:
    sa_default = os.path.join(sa_base_path, "default")
    if os.path.exists(sa_default):
        print(f"{COLOR_BLUE}removing default Nginx site available config{COLOR_RESET}")
        exec(["sudo", "rm", "-f", sa_default])

    se_default = os.path.join(se_base_path, "default")
    if os.path.exists(se_default):
        print(f"{COLOR_BLUE}removing default Nginx site enabled config{COLOR_RESET}")
        exec(["sudo", "rm", "-f", se_default])


def create_and_link_nginx_site_config(hostname: str, app_port: int) -> None:
    sa_base_path = os.path.join("/", "etc", "nginx", "sites-available")
    se_base_path = os.path.join("/", "etc", "nginx", "sites-enabled")

    if not os.path.exists(sa_base_path):
        print(f"{COLOR_YELLOW}Sites Available folder does not exist: creating...{COLOR_RESET}")
        exec(["sudo", "mkdir", "-p", sa_base_path])

    if not os.path.exists(se_base_path):
        print(f"{COLOR_YELLOW}Sites Enabled folder does not exist: creating...{COLOR_RESET}")
        exec(["sudo", "mkdir", "-p", se_base_path])

    remove_default_nginx_site_config(sa_base_path, se_base_path)
    sa_path = os.path.join(sa_base_path, hostname)
    se_path = os.path.join(se_base_path, hostname)

    print(f"{COLOR_BLUE}creating site entry at {sa_path}{COLOR_RESET}")
    exec(["sudo", "touch", sa_path])

    if os.path.exists(sa_path):
        print(f"{COLOR_YELLOW}sites available entry already exists{COLOR_RESET}")
        if confirm("delete existing site available entry"):
            exec(["sudo", "rm", "-f", sa_path])

    site_config = get_nginx_host_config(hostname, app_port)
    exec(["sudo", "echo", site_config, ">", sa_path])

    if os.path.exists(se_path):
        print(f"{COLOR_YELLOW}sites enabled entry already exists{COLOR_RESET}")
        if confirm("delete existing sites enabled entry"):
            exec(["sudo", "rm", "-f", se_path])

    print(f"{COLOR_BLUE}linking config to {sa_path}{COLOR_RESET}")
    exec(["sudo", "ln", "-s", sa_path, se_path])

    print(f"{COLOR_BLUE}reloading Nginx configs{COLOR_RESET}")
    exec(["sudo", "nginx", "-s", "reload"])


def setup_nginx() -> None:
    print(f"{COLOR_BLUE}installing nginx{COLOR_RESET}")
    exec(["sudo", "apt-get", "install", "-y", "nginx"])
    exec(["sudo", "systemctl", "enable", "nginx"])
    exec(["sudo", "systemctl", "start", "nginx"])

    hostname = read_hostname()
    app_port = read_app_port()
    create_and_link_nginx_site_config(hostname, app_port)



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


# TODO: implement.
def setup_systemd_service() -> None:
    pass


def main() -> None:
    steps = [
        ("Upgrade system", upgrade_system),
        ("Install base packages", install_base_packages),
        ("Set timezone (UTC)", set_timezone),
        ("Setup Systemd Service", setup_systemd_service),
        ("Setup Nginx", setup_nginx),
        ("Setup firewall", setup_firewall),
    ]

    while True:
        print(f"\n{COLOR_YELLOW}Please select an option (q to exit):{COLOR_RESET}")
        for i, (name, _func) in enumerate(steps):
            print(f"{i+1}. {name}")

        selection = read_selection(len(steps))
        target_step = steps[selection-1]
        if target_step is None:
            raise Exception(f"failed to run selection: {selection}")

        target_step[1]()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{COLOR_YELLOW}ctrl+c: exiting...{COLOR_RESET}")
    except Exception as ex:
        print(f"{COLOR_RED}error: {ex}.{COLOR_RESET}")
