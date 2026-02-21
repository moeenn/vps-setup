package shell

import (
	"errors"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"vpsetup/internal/colors"
)

func IsCommandAvailable(cmd string) bool {
	c := exec.Command("which", cmd)
	_, err := c.Output()
	return err == nil
}

func Execute(cmd *exec.Cmd) error {
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	err := cmd.Run()
	if err != nil {
		return fmt.Errorf("command failed: %w", err)
	}

	return nil
}

func Input(message string) (*string, error) {
	var input string
	fmt.Printf("%s%s:%s ", colors.YELLOW, message, colors.RESET)
	_, err := fmt.Scanln(&input)
	if err != nil {
		return nil, fmt.Errorf("failed to read user input: %w", err)
	}

	trimmed := strings.TrimSpace(input)
	if len(trimmed) == 0 {
		return nil, errors.New("empty input")
	}

	return &trimmed, nil
}
