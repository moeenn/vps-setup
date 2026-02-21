package operations

import (
	"fmt"
	"vpsetup/internal/colors"
	"vpsetup/internal/config"
	"vpsetup/internal/pm"
)

func InstallBasePackages(cfg *config.Config) error {
	p, err := pm.GetPackageManager()
	if err != nil {
		return err
	}

	fmt.Printf("%s[info] installing base packages. %s\n", colors.BLUE, colors.RESET)
	if err := p.Install(cfg.BasePackages...); err != nil {
		return fmt.Errorf("failed to install base packages: %w", err)
	}

	return nil
}
