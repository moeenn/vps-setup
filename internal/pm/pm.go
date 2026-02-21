package pm

import (
	"errors"
	"os/exec"
	"vpsetup/internal/shell"
)

type packageManagerType string

const (
	packageManagerTypeApt packageManagerType = "apt-get"
	packageManagerTypeDnf packageManagerType = "dnf"
)

func (pmt packageManagerType) String() string {
	return string(pmt)
}

func GetPackageManager() (PackageManager, error) {
	supported := []packageManagerType{packageManagerTypeApt, packageManagerTypeDnf}
	for _, s := range supported {
		if shell.IsCommandAvailable(s.String()) {
			switch s {
			case packageManagerTypeApt:
				return AptPackageManager{}, nil

			case packageManagerTypeDnf:
				return DnfPackageManager{}, nil
			}
		}
	}

	return nil, errors.New("no supported package manager found")
}

type PackageManager interface {
	Update() error
	Upgrade() error
	Install(packages ...string) error
}

type AptPackageManager struct{}

func (pm AptPackageManager) Update() error {
	cmd := exec.Command("sudo", "apt-get", "update", "-y")
	return shell.Execute(cmd)
}

func (pm AptPackageManager) Upgrade() error {
	cmd := exec.Command("sudo", "apt-get", "upgrade", "-y")
	return shell.Execute(cmd)
}

func (pm AptPackageManager) Install(packages ...string) error {
	args := []string{"sudo", "apt-get", "install", "-y"}
	args = append(args, packages...)
	cmd := exec.Command(args[0], args[1:]...)
	return shell.Execute(cmd)
}

type DnfPackageManager struct{}

func (pm DnfPackageManager) Update() error {
	cmd := exec.Command("sudo", "dnf", "update", "-y")
	return shell.Execute(cmd)
}

func (pm DnfPackageManager) Upgrade() error {
	cmd := exec.Command("sudo", "dnf", "upgrade", "-y")
	return shell.Execute(cmd)
}

func (pm DnfPackageManager) Install(packages ...string) error {
	args := []string{"sudo", "dnf", "install", "-y"}
	args = append(args, packages...)
	cmd := exec.Command(args[0], args[1:]...)
	return shell.Execute(cmd)
}
