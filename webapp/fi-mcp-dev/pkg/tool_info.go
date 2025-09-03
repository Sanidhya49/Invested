package pkg

import (
	"context"
	"encoding/json" // Added for json.Unmarshal and json.MarshalIndent
	"fmt"
	"log"
	"os"
	"path/filepath"

	// "encoding/json" // No longer needed here as we don't marshal into complex result format

	"github.com/mark3labs/mcp-go/mcp"
)

// Tool represents a tool definition
type Tool struct {
	Name        string
	Description string
}

// ToolList contains all defined tools.
var ToolList = []Tool{
	{
		Name:        "GetBankTransactions",
		Description: "Retrieves a user's bank transaction history.",
	},
	{
		Name:        "GetNetWorth",
		Description: "Retrieves a user's net worth summary.",
	},
	{
		Name:        "GetMFTransactions",
		Description: "Retrieves a user's mutual fund transaction history.",
	},
	{
		Name:        "GetStockTransactions",
		Description: "Retrieves a user's stock transaction history.",
	},
	{
		Name:        "GetEPFDetails",
		Description: "Retrieves a user's EPF details.",
	},
	{
		Name:        "GetCreditReport",
		Description: "Retrieves a user's credit report.",
	},
	{
		Name:        "GetGoals",
		Description: "Retrieves all financial goals for a user.",
	},
	{
		Name:        "AddGoal",
		Description: "Adds a new financial goal for a user.",
	},
	{
		Name:        "UpdateGoal",
		Description: "Updates an existing financial goal for a user.",
	},
	{
		Name:        "DeleteGoal",
		Description: "Deletes a financial goal for a user.",
	},
	// Add other tool definitions here as you implement them.
}

// GetBankTransactionsHandler handles the GetBankTransactions tool call.
func GetBankTransactionsHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	phoneNumber, err := req.RequireString("phoneNumber")
	if err != nil {
		return nil, fmt.Errorf("missing or invalid 'phoneNumber' in GetBankTransactions request inputs: %w", err)
	}

	mcpFilePath := os.Getenv("MCP_FILE_PATH")
	if mcpFilePath == "" {
		log.Println("ERROR: MCP_FILE_PATH is not set in .env. Cannot serve bank transactions.")
		return nil, fmt.Errorf("server configuration error: MCP_FILE_PATH not set")
	}

	filePath := filepath.Join(mcpFilePath, "test_data_dir", phoneNumber, "fetch_bank_transactions.json")
	log.Printf("DEBUG: GetBankTransactionsHandler attempting to read from: %s", filePath)

	data, err := os.ReadFile(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			log.Printf("ERROR: Bank transactions file not found for %s at %s", phoneNumber, filePath)
			return mcp.NewToolResultText("No bank transactions found for this user."), nil
		}
		log.Printf("ERROR: Failed to read bank transactions file for %s: %v", phoneNumber, err)
		return nil, fmt.Errorf("failed to read bank transactions: %w", err)
	}

	// CORRECTED: Revert to using NewToolResultText for the JSON string
	// Python side will now parse this text as JSON.
	return mcp.NewToolResultText(string(data)), nil
}

// GetNetWorthHandler handles the GetNetWorth tool call.
func GetNetWorthHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	phoneNumber, err := req.RequireString("phoneNumber")
	if err != nil {
		return nil, fmt.Errorf("missing or invalid 'phoneNumber' in GetNetWorth request inputs: %w", err)
	}

	mcpFilePath := os.Getenv("MCP_FILE_PATH")
	if mcpFilePath == "" {
		log.Println("ERROR: MCP_FILE_PATH is not set in .env. Cannot serve net worth.")
		return nil, fmt.Errorf("server configuration error: MCP_FILE_PATH not set")
	}

	filePath := filepath.Join(mcpFilePath, "test_data_dir", phoneNumber, "fetch_net_worth.json")
	log.Printf("DEBUG: GetNetWorthHandler attempting to read from: %s", filePath)

	data, err := os.ReadFile(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			log.Printf("ERROR: Net worth file not found for %s at %s", phoneNumber, filePath)
			return mcp.NewToolResultText("No net worth data found for this user."), nil
		}
		log.Printf("ERROR: Failed to read net worth file for %s: %v", phoneNumber, err)
		return nil, fmt.Errorf("failed to read net worth: %w", err)
	}

	return mcp.NewToolResultText(string(data)), nil
}

// GetMFTransactionsHandler handles the GetMFTransactions tool call.
func GetMFTransactionsHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	phoneNumber, err := req.RequireString("phoneNumber")
	if err != nil {
		return nil, fmt.Errorf("missing or invalid 'phoneNumber' in GetMFTransactions request inputs: %w", err)
	}

	mcpFilePath := os.Getenv("MCP_FILE_PATH")
	if mcpFilePath == "" {
		log.Println("ERROR: MCP_FILE_PATH is not set in .env. Cannot serve MF transactions.")
		return nil, fmt.Errorf("server configuration error: MCP_FILE_PATH not set")
	}

	filePath := filepath.Join(mcpFilePath, "test_data_dir", phoneNumber, "fetch_mf_transactions.json")
	log.Printf("DEBUG: GetMFTransactionsHandler attempting to read from: %s", filePath)

	data, err := os.ReadFile(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			log.Printf("ERROR: MF transactions file not found for %s at %s", phoneNumber, filePath)
			return mcp.NewToolResultText("No mutual fund transactions found for this user."), nil
		}
		log.Printf("ERROR: Failed to read MF transactions file for %s: %v", phoneNumber, err)
		return nil, fmt.Errorf("failed to read mutual fund transactions: %w", err)
	}

	return mcp.NewToolResultText(string(data)), nil
}

// GetStockTransactionsHandler handles the GetStockTransactions tool call.
func GetStockTransactionsHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	phoneNumber, err := req.RequireString("phoneNumber")
	if err != nil {
		return nil, fmt.Errorf("missing or invalid 'phoneNumber' in GetStockTransactions request inputs: %w", err)
	}

	mcpFilePath := os.Getenv("MCP_FILE_PATH")
	if mcpFilePath == "" {
		log.Println("ERROR: MCP_FILE_PATH is not set in .env. Cannot serve stock transactions.")
		return nil, fmt.Errorf("server configuration error: MCP_FILE_PATH not set")
	}

	filePath := filepath.Join(mcpFilePath, "test_data_dir", phoneNumber, "fetch_stock_transactions.json")
	log.Printf("DEBUG: GetStockTransactionsHandler attempting to read from: %s", filePath)

	data, err := os.ReadFile(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			log.Printf("ERROR: Stock transactions file not found for %s at %s", phoneNumber, filePath)
			return mcp.NewToolResultText("No stock transactions found for this user."), nil
		}
		log.Printf("ERROR: Failed to read stock transactions file for %s: %v", phoneNumber, err)
		return nil, fmt.Errorf("failed to read stock transactions: %w", err)
	}

	return mcp.NewToolResultText(string(data)), nil
}

// GetEPFDetailsHandler handles the GetEPFDetails tool call.
func GetEPFDetailsHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	phoneNumber, err := req.RequireString("phoneNumber")
	if err != nil {
		return nil, fmt.Errorf("missing or invalid 'phoneNumber' in GetEPFDetails request inputs: %w", err)
	}

	mcpFilePath := os.Getenv("MCP_FILE_PATH")
	if mcpFilePath == "" {
		log.Println("ERROR: MCP_FILE_PATH is not set in .env. Cannot serve EPF details.")
		return nil, fmt.Errorf("server configuration error: MCP_FILE_PATH not set")
	}

	filePath := filepath.Join(mcpFilePath, "test_data_dir", phoneNumber, "fetch_epf_details.json")
	log.Printf("DEBUG: GetEPFDetailsHandler attempting to read from: %s", filePath)

	data, err := os.ReadFile(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			log.Printf("ERROR: EPF details file not found for %s at %s", phoneNumber, filePath)
			return mcp.NewToolResultText("No EPF details found for this user."), nil
		}
		log.Printf("ERROR: Failed to read EPF details file for %s: %v", phoneNumber, err)
		return nil, fmt.Errorf("failed to read EPF details: %w", err)
	}

	return mcp.NewToolResultText(string(data)), nil
}

// GetCreditReportHandler handles the GetCreditReport tool call.
func GetCreditReportHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	phoneNumber, err := req.RequireString("phoneNumber")
	if err != nil {
		return nil, fmt.Errorf("missing or invalid 'phoneNumber' in GetCreditReport request inputs: %w", err)
	}

	mcpFilePath := os.Getenv("MCP_FILE_PATH")
	if mcpFilePath == "" {
		log.Println("ERROR: MCP_FILE_PATH is not set in .env. Cannot serve credit report.")
		return nil, fmt.Errorf("server configuration error: MCP_FILE_PATH not set")
	}

	filePath := filepath.Join(mcpFilePath, "test_data_dir", phoneNumber, "fetch_credit_report.json")
	log.Printf("DEBUG: GetCreditReportHandler attempting to read from: %s", filePath)

	data, err := os.ReadFile(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			log.Printf("ERROR: Credit report file not found for %s at %s", phoneNumber, filePath)
			return mcp.NewToolResultText("No credit report found for this user."), nil
		}
		log.Printf("ERROR: Failed to read credit report file for %s: %v", phoneNumber, err)
		return nil, fmt.Errorf("failed to read credit report: %w", err)
	}

	return mcp.NewToolResultText(string(data)), nil
}

// GetGoalsHandler handles the GetGoals tool call.
func GetGoalsHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	phoneNumber, err := req.RequireString("phoneNumber")
	if err != nil {
		return nil, fmt.Errorf("missing or invalid 'phoneNumber' in GetGoals request inputs: %w", err)
	}
	mcpFilePath := os.Getenv("MCP_FILE_PATH")
	if mcpFilePath == "" {
		log.Println("ERROR: MCP_FILE_PATH is not set in .env. Cannot serve goals.")
		return nil, fmt.Errorf("server configuration error: MCP_FILE_PATH not set")
	}
	filePath := filepath.Join(mcpFilePath, "test_data_dir", phoneNumber, "goals.json")
	log.Printf("DEBUG: GetGoalsHandler attempting to read from: %s", filePath)
	data, err := os.ReadFile(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			log.Printf("INFO: goals.json not found for %s, returning empty list", phoneNumber)
			return mcp.NewToolResultText("[]"), nil
		}
		log.Printf("ERROR: Failed to read goals.json for %s: %v", phoneNumber, err)
		return nil, fmt.Errorf("failed to read goals: %w", err)
	}
	return mcp.NewToolResultText(string(data)), nil
}

// AddGoalHandler handles the AddGoal tool call.
func AddGoalHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	phoneNumber, err := req.RequireString("phoneNumber")
	if err != nil {
		return nil, fmt.Errorf("missing or invalid 'phoneNumber' in AddGoal request inputs: %w", err)
	}
	args, ok := req.Params.Arguments.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("invalid arguments format in AddGoal request inputs")
	}
	goalRaw, ok := args["goal"]
	if !ok {
		return nil, fmt.Errorf("missing 'goal' in AddGoal request inputs")
	}
	mcpFilePath := os.Getenv("MCP_FILE_PATH")
	if mcpFilePath == "" {
		log.Println("ERROR: MCP_FILE_PATH is not set in .env. Cannot serve goals.")
		return nil, fmt.Errorf("server configuration error: MCP_FILE_PATH not set")
	}
	filePath := filepath.Join(mcpFilePath, "test_data_dir", phoneNumber, "goals.json")
	var goals []map[string]interface{}
	data, err := os.ReadFile(filePath)
	if err == nil {
		_ = json.Unmarshal(data, &goals)
	}
	// If file doesn't exist, start with empty goals
	goalMap, ok := goalRaw.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("invalid 'goal' format in AddGoal request inputs")
	}
	goals = append(goals, goalMap)
	newData, err := json.MarshalIndent(goals, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("failed to marshal updated goals: %w", err)
	}
	err = os.WriteFile(filePath, newData, 0644)
	if err != nil {
		return nil, fmt.Errorf("failed to write updated goals: %w", err)
	}
	return mcp.NewToolResultText(string(newData)), nil
}

// UpdateGoalHandler handles the UpdateGoal tool call.
func UpdateGoalHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	phoneNumber, err := req.RequireString("phoneNumber")
	if err != nil {
		return nil, fmt.Errorf("missing or invalid 'phoneNumber' in UpdateGoal request inputs: %w", err)
	}
	args, ok := req.Params.Arguments.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("invalid arguments format in UpdateGoal request inputs")
	}
	goalID, ok := args["goal_id"].(string)
	if !ok {
		return nil, fmt.Errorf("missing or invalid 'goal_id' in UpdateGoal request inputs")
	}
	goalUpdate, ok := args["goal_update"].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("missing or invalid 'goal_update' in UpdateGoal request inputs")
	}
	mcpFilePath := os.Getenv("MCP_FILE_PATH")
	if mcpFilePath == "" {
		log.Println("ERROR: MCP_FILE_PATH is not set in .env. Cannot serve goals.")
		return nil, fmt.Errorf("server configuration error: MCP_FILE_PATH not set")
	}
	filePath := filepath.Join(mcpFilePath, "test_data_dir", phoneNumber, "goals.json")
	var goals []map[string]interface{}
	data, err := os.ReadFile(filePath)
	if err == nil {
		_ = json.Unmarshal(data, &goals)
	}
	updated := false
	for i, goal := range goals {
		if id, ok := goal["goal_id"].(string); ok && id == goalID {
			for k, v := range goalUpdate {
				goal[k] = v
			}
			goals[i] = goal
			updated = true
			break
		}
	}
	if !updated {
		return nil, fmt.Errorf("Goal not found")
	}
	newData, err := json.MarshalIndent(goals, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("failed to marshal updated goals: %w", err)
	}
	err = os.WriteFile(filePath, newData, 0644)
	if err != nil {
		return nil, fmt.Errorf("failed to write updated goals: %w", err)
	}
	return mcp.NewToolResultText(string(newData)), nil
}

// DeleteGoalHandler handles the DeleteGoal tool call.
func DeleteGoalHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	phoneNumber, err := req.RequireString("phoneNumber")
	if err != nil {
		return nil, fmt.Errorf("missing or invalid 'phoneNumber' in DeleteGoal request inputs: %w", err)
	}
	args, ok := req.Params.Arguments.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("invalid arguments format in DeleteGoal request inputs")
	}
	goalID, ok := args["goal_id"].(string)
	if !ok {
		return nil, fmt.Errorf("missing or invalid 'goal_id' in DeleteGoal request inputs")
	}
	mcpFilePath := os.Getenv("MCP_FILE_PATH")
	if mcpFilePath == "" {
		log.Println("ERROR: MCP_FILE_PATH is not set in .env. Cannot serve goals.")
		return nil, fmt.Errorf("server configuration error: MCP_FILE_PATH not set")
	}
	filePath := filepath.Join(mcpFilePath, "test_data_dir", phoneNumber, "goals.json")
	var goals []map[string]interface{}
	data, err := os.ReadFile(filePath)
	if err == nil {
		_ = json.Unmarshal(data, &goals)
	}
	newGoals := make([]map[string]interface{}, 0, len(goals))
	found := false
	for _, goal := range goals {
		if id, ok := goal["goal_id"].(string); ok && id == goalID {
			found = true
			continue
		}
		newGoals = append(newGoals, goal)
	}
	if !found {
		return nil, fmt.Errorf("Goal not found")
	}
	newData, err := json.MarshalIndent(newGoals, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("failed to marshal updated goals: %w", err)
	}
	err = os.WriteFile(filePath, newData, 0644)
	if err != nil {
		return nil, fmt.Errorf("failed to write updated goals: %w", err)
	}
	return mcp.NewToolResultText(string(newData)), nil
}
