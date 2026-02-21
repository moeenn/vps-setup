package env

import (
	"errors"
	"os"
	"path"
	"strings"
)

func GetUsername() (*string, error) {
	username := os.Getenv("USER")
	trimmed := strings.TrimSpace(username)
	if len(trimmed) == 0 {
		return nil, errors.New("failed to read $USER from environment")
	}

	return &trimmed, nil
}

func GetHomePath(username string) string {
	return path.Join("/", "home", username)
}
