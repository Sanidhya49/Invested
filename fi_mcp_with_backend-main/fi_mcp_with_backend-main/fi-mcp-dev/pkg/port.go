package pkg

import (
	"os"
)

func GetPort() string {
	if port := os.Getenv("FI_MCP_PORT"); port != "" {
		return port
	}
	return "8080"
}
