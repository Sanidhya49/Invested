package pkg

import (
	"os"
)

// GetAllowedMobileNumbers returns a slice of directory names in test_data_dir
func GetAllowedMobileNumbers() []string {
	dirEntries, err := os.ReadDir("test_data_dir")
	if err != nil {
		return nil
	}
	var numbers []string
	for _, entry := range dirEntries {
		if entry.IsDir() {
			numbers = append(numbers, entry.Name())
		}
	}
	return numbers
}
