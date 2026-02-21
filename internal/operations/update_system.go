package operations

import (
	"fmt"
	"vpsetup/internal/colors"
	"vpsetup/internal/config"
	"vpsetup/internal/pm"
)

func SystemUpdate(_cfg *config.Config) error {
	p, err := pm.GetPackageManager()
	if err != nil {
		return err
	}

	fmt.Printf("%s[info] updating package lists. %s\n", colors.BLUE, colors.RESET)
	if err := p.Update(); err != nil {
		return fmt.Errorf("failed to update package lists: %w", err)
	}

	fmt.Printf("%s[info] upgrading system packages. %s\n", colors.BLUE, colors.RESET)
	if err := p.Upgrade(); err != nil {
		return fmt.Errorf("failed to upgrade system packages: %w", err)
	}

	return nil
}
