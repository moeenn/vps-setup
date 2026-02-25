package main

import (
	"fmt"
	"strconv"
	"vpsetup/internal/colors"
	"vpsetup/internal/config"
	"vpsetup/internal/operations"
	"vpsetup/internal/shell"
)

type MenuEntry struct {
	Title  string
	Action func(config *config.Config) error
}

func main() {
	// TODO: load actual config.
	cfg := config.DefaultConfig()

	menu := []MenuEntry{
		{Title: "Disable root user", Action: nil},
		{Title: "Update system", Action: operations.SystemUpdate},
		{Title: "Install base packages", Action: operations.InstallBasePackages},
		{Title: "Setup unattended upgrades", Action: nil},
		{Title: "Set timezone (UTC)", Action: operations.SetUtcTimezone},
		{Title: "Setup Nginx", Action: nil},
		{Title: "Setup firewall (UFW)", Action: operations.SetupFirewall},
		{Title: "Setup SystemD service", Action: nil},
	}

	for {
		fmt.Printf("\n%sPlease select an option: %s\n", colors.YELLOW, colors.RESET)
		for i, entry := range menu {
			fmt.Printf("%2d. %s\n", i+1, entry.Title)
		}

		fmt.Printf(" q: Quit\n")
		userSelection, err := shell.Input("Selection")
		if err != nil {
			fmt.Printf("%serror: invalid input: %s%s.", colors.RED, err.Error(), colors.RESET)
			continue
		}

		if *userSelection == "q" || *userSelection == "Q" {
			fmt.Printf("%sExiting...%s\n", colors.BLACK, colors.RESET)
			return
		}

		parsedSelection, err := strconv.Atoi(*userSelection)
		if err != nil {
			fmt.Printf("%serror: input is not a valid number.%s\n", colors.RED, colors.RESET)
			continue
		}

		if parsedSelection < 1 || parsedSelection > len(menu) {
			fmt.Printf("%serror: %d is not a valid option.%s\n", colors.RED, parsedSelection, colors.RESET)
			continue
		}

		selectedOption := menu[parsedSelection-1]
		if selectedOption.Action == nil {
			fmt.Printf("%serror: the selected option has not been implemented yet.%s\n", colors.RED, colors.RESET)
			continue
		}

		fmt.Printf("%sRunning action: %s.%s\n", colors.BLUE, selectedOption.Title, colors.RESET)
		if err := selectedOption.Action(cfg); err != nil {
			fmt.Printf("%saction failed: %s.%s", colors.RED, err.Error(), colors.RESET)
		}
	}
}
