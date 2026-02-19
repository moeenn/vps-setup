#! /bin/python3

import subprocess
import os
import sys

# -------------------------------------------------------------------------------------------------
#
# script configs.
#
# -------------------------------------------------------------------------------------------------
HOSTNAME: str = "mysite.com"
APP_PORT = 3000
APP_DIR = os.path.join("/", "home", "admin", "app")
APP_START_CMD = "npm run start"
APP_SERVICE_NAME = "MySite"
BASE_PACKAGES = ["rsync", "kakoune", "docker.io", "docker-compose"]
OPEN_PORTS = [
    ("allow", 80),  # http.
    ("allow", 443),  # https.
    ("limit", 22),  # ssh (rate limited for security).
]


# -------------------------------------------------------------------------------------------------
#
# globals and helpers.
#
# -------------------------------------------------------------------------------------------------
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"


def validate_config() -> None:
    if not "." in HOSTNAME:
        print(f"{COLOR_RED}warning: invalid hostname (i.e. {HOSTNAME}).{COLOR_RESET}")

    if APP_PORT == 0:
        print(f"{COLOR_RED}warning: invalid app port (i.e. {APP_PORT}).{COLOR_RESET}")

    if not os.path.exists(APP_DIR):
        print(f"{COLOR_RED}warning: app dir (i.e. {APP_DIR}) does not exits.{COLOR_RESET}")

    if len(APP_START_CMD) < 4:
        print(f"{COLOR_RED}warning: app start command may be invalid (i.e. {APP_START_CMD}).{COLOR_RESET}")

    if len(APP_SERVICE_NAME) < 4:
        print(f"{COLOR_RED}warning: app (systemd) service name may be invalid (i.e. {APP_SERVICE_NAME}).{COLOR_RESET}")


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


# -------------------------------------------------------------------------------------------------
#
# openration steps.
#
# -------------------------------------------------------------------------------------------------
def upgrade_system() -> None:
    print(f"{COLOR_BLUE}upgrading system{COLOR_RESET}")
    exec(["sudo", "apt-get", "update", "-y"])
    exec(["sudo", "apt-get", "upgrade", "-y"])


def install_base_packages() -> None:
    print(f"{COLOR_BLUE}installing base packages")
    exec(["sudo", "apt-get", "install", "-y"] + BASE_PACKAGES)


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


def reload_nginx() -> None:
    print(f"{COLOR_BLUE}reloading Nginx configs{COLOR_RESET}")
    exec(["sudo", "nginx", "-s", "reload"])


def create_and_link_nginx_site_config(hostname: str, app_port: int) -> None:
    sa_base_path = os.path.join("/", "etc", "nginx", "sites-available")
    se_base_path = os.path.join("/", "etc", "nginx", "sites-enabled")

    if not os.path.exists(sa_base_path):
        print(
            f"{COLOR_YELLOW}Sites Available folder does not exist: creating...{COLOR_RESET}"
        )
        exec(["sudo", "mkdir", "-p", sa_base_path])

    if not os.path.exists(se_base_path):
        print(
            f"{COLOR_YELLOW}Sites Enabled folder does not exist: creating...{COLOR_RESET}"
        )
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
    reload_nginx()


def setup_nginx() -> None:
    print(f"{COLOR_BLUE}installing nginx{COLOR_RESET}")
    exec(["sudo", "apt-get", "install", "-y", "nginx"])
    exec(["sudo", "systemctl", "enable", "nginx"])
    exec(["sudo", "systemctl", "start", "nginx"])
    create_and_link_nginx_site_config(HOSTNAME, APP_PORT)


def setup_firewall() -> None:
    print(f"{COLOR_BLUE}installing firewall{COLOR_RESET}")
    exec(["sudo", "apt-get", "install", "-y", "ufw"])

    print(f"{COLOR_BLUE} - closing all incoming connections{COLOR_RESET}")
    exec(["sudo", "ufw", "default", "deny", "incoming"])

    print(f"{COLOR_BLUE} - closing all outgoing connections{COLOR_RESET}")
    exec(["sudo", "ufw", "default", "deny", "outgoing"])

    print(f"{COLOR_BLUE} - openging ports specific ports{COLOR_RESET}")
    for cmd, port in OPEN_PORTS:
        exec(["sudo", "ufw", cmd, str(port)])

    print(f"{COLOR_BLUE} - enabling firewall{COLOR_RESET}")
    exec(["sudo", "ufw", "enable"])


def set_timezone() -> None:
    print(f"{COLOR_BLUE}setting system timezone to UTC")
    exec(["sudo", "timedatectl", "set-timezone", "UTC"])


def get_systemd_service_config(
    service_name: str, app_dir: str, app_start_cmd: str
) -> str:
    return f"""
[Unit]
Description={service_name}
After=network.target

[Service]
ExecStart={app_start_cmd}
WorkingDirectory={app_dir}
Type=simple
Restart=always

[Install]
WantedBy=default.target
    """.strip()


def reload_systemd() -> None:
    print(f"{COLOR_BLUE}reloading SystemD configs{COLOR_RESET}")
    exec(["sudo", "systemctl", "daemon-reload"])


def setup_systemd_service() -> None:
    print(f"{COLOR_BLUE}setting up systemd service{COLOR_RESET}")
    config_path = os.path.join(
        "/", "etc", "systemd", "system", f"{APP_SERVICE_NAME}.service"
    )
    if os.path.exists(config_path):
        print(f"{COLOR_YELLOW}systemd service already exists{COLOR_RESET}")
        if confirm("Overwrite service"):
            exec(["sudo", "rm", "-f", config_path])
    else:
        exec(["sudo", "touch", config_path])
        content = get_systemd_service_config(APP_SERVICE_NAME, APP_DIR, APP_START_CMD)
        exec(["sudo", "echo", content, ">", config_path])
        reload_systemd()


# -------------------------------------------------------------------------------------------------
#
# entry-point.
#
# -------------------------------------------------------------------------------------------------


def main() -> None:
    validate_config()

    steps = [
        ("Upgrade system", upgrade_system),
        ("Install base packages", install_base_packages),
        ("Set timezone (UTC)", set_timezone),
        ("Setup Nginx", setup_nginx),
        ("Reload Nginx", reload_nginx),
        ("Setup firewall", setup_firewall),
        ("Setup SystemD Service", setup_systemd_service),
        ("Reload SystemD", reload_systemd),
    ]

    while True:
        print(f"\n{COLOR_YELLOW}Please select an option (q to exit):{COLOR_RESET}")
        for i, (name, _func) in enumerate(steps):
            print(f"{i + 1}. {name}")

        selection = read_selection(len(steps))
        target_step = steps[selection - 1]
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
