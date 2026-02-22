package operations

import (
	"fmt"
	"os/exec"
	"vpsetup/internal/colors"
	"vpsetup/internal/config"
	"vpsetup/internal/pm"
	"vpsetup/internal/shell"
)

func SetupFirewall(cfg *config.Config) error {
	p, err := pm.GetPackageManager()
	if err != nil {
		return err
	}

	if err := installFirewall(p); err != nil {
		return err
	}

	if err := closeIncomingOutgoing(); err != nil {
		return err
	}

	if err := openSelectivePorts(cfg.OpenPorts); err != nil {
		return err
	}

	if err := enableFirewall(); err != nil {
		return err
	}

	return nil
}

func installFirewall(p pm.PackageManager) error {
	fmt.Printf("%s[info] Installing firewall.%s\n", colors.BLUE, colors.RESET)
	err := p.Install("ufw")
	if err != nil {
		return fmt.Errorf("failed to install firewall: %w", err)
	}
	return nil
}

func closeIncomingOutgoing() error {
	fmt.Printf("%s[info] Closing incoming connections.%s\n", colors.BLUE, colors.RESET)
	cmd := exec.Command("sudo", "ufw", "default", "deny", "incoming")
	if err := shell.Execute(cmd); err != nil {
		return fmt.Errorf("failed to close incoming connections: %w", err)
	}

	fmt.Printf("%s[info] Allowing outgoing connections.%s\n", colors.BLUE, colors.RESET)
	cmd = exec.Command("sudo", "ufw", "default", "allow", "outgoing")
	if err := shell.Execute(cmd); err != nil {
		return fmt.Errorf("failed to close outgoing connections: %w", err)
	}

	return nil
}

func openSelectivePorts(ports []config.OpenPort) error {
	var cmd *exec.Cmd
	var err error
	for _, p := range ports {
		fmt.Printf("%s[info] Opening port %d.%s\n", colors.BLUE, p.Port, colors.RESET)
		cmd = exec.Command("sudo", "ufw", string(p.Type), fmt.Sprintf("%d", p.Port))
		err = shell.Execute(cmd)
		if err != nil {
			return fmt.Errorf("failed to open port %d: %w", p.Port, err)
		}
	}

	return nil
}

func enableFirewall() error {
	fmt.Printf("%s[info] Enabling firewall.%s\n", colors.BLUE, colors.RESET)
	cmd := exec.Command("sudo", "ufw", "enable")
	if err := shell.Execute(cmd); err != nil {
		return fmt.Errorf("failed to enable firewall: %w", err)
	}
	return nil
}
