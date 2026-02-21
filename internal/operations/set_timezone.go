package operations

import (
	"fmt"
	"os/exec"
	"vpsetup/internal/colors"
	"vpsetup/internal/config"
	"vpsetup/internal/shell"
)

func SetUtcTimezone(_cfg *config.Config) error {
	fmt.Printf("%s[info] Setting system timezone to UTC.%s\n", colors.BLUE, colors.RESET)
	cmd := exec.Command("sudo", "timedatectl", "set-timezone", "UTC")
	if err := shell.Execute(cmd); err != nil {
		return fmt.Errorf("failed to set timezone: %w", err)
	}

	return nil
}
