package main

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/epifi/fi-mcp-lite/pkg"
)

func TestTestDataDirIntegrity(t *testing.T) {
	// Get allowed phone numbers
	phoneNumbers := pkg.GetAllowedMobileNumbers()
	if len(phoneNumbers) == 0 {
		t.Fatal("No allowed phone numbers found in test_data_dir")
	}

	// Get tool names from ToolList
	var toolNames []string
	for _, tool := range pkg.ToolList {
		toolNames = append(toolNames, tool.Name)
	}
	if len(toolNames) == 0 {
		t.Fatal("No tools found in ToolList")
	}

	// For each phone number and tool, check if the file exists and is readable
	for _, phone := range phoneNumbers {
		for _, tool := range toolNames {
			filePath := filepath.Join("test_data_dir", phone, tool+".json")
			data, err := os.ReadFile(filePath)
			if err != nil {
				t.Errorf("Missing or unreadable file: %s, error: %v", filePath, err)
			} else if len(data) == 0 {
				t.Errorf("File is empty: %s", filePath)
			}
		}
	}
}
