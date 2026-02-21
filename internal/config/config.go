package config

import "path"

type OpenPortType string

const (
	OpenPortTypeAllow OpenPortType = "allow"
	OpenPortTypeLimit OpenPortType = "limit"
)

type OpenPort struct {
	Type OpenPortType
	Port int
}

type Config struct {
	Hostname       string
	AppPort        int
	AppDir         string
	AppServiceName string
	BasePackages   []string
	OpenPorts      []OpenPort
}

func DefaultConfig() *Config {
	return &Config{
		Hostname:       "example.com",
		AppPort:        3000,
		AppDir:         path.Join("/", "admin", "app"),
		AppServiceName: "MyApp",
		BasePackages:   []string{"rsync", "kakoune", "docker.io", "docker-compose"},
		OpenPorts: []OpenPort{
			{Type: OpenPortTypeAllow, Port: 80},  // http.
			{Type: OpenPortTypeAllow, Port: 443}, // https.
			{Type: OpenPortTypeLimit, Port: 22},  // ssh (rate limited),
		},
	}
}
