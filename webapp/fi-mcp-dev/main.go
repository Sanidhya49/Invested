package main

import (
	"context"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/joho/godotenv"
	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"

	"github.com/epifi/fi-mcp-lite/middlewares"
	"github.com/epifi/fi-mcp-lite/pkg"
	"github.com/samber/lo"
)

var authMiddleware *middlewares.AuthMiddleware

func manualMcpStreamHandler(w http.ResponseWriter, r *http.Request) {
	// 1. Get Session ID from header.
	sessionId := r.Header.Get("X-Session-ID")
	log.Printf("MANUAL HANDLER: Checking session for ID '%s'\n", sessionId)

	// 2. In stateless mode, accept any session and use phone number from request
	phoneNumber := "8888888888" // Default fallback phone number
	log.Printf("MANUAL HANDLER: STATELESS MODE - Using default phone: %s\n", phoneNumber)

	// 3. Decode the request body to get the tool name and phone number.
	var requestBody struct {
		ToolName    string `json:"tool_name"`
		PhoneNumber string `json:"phone_number"`
	}
	if err := json.NewDecoder(r.Body).Decode(&requestBody); err != nil {
		http.Error(w, "Could not decode request body", http.StatusBadRequest)
		return
	}
	toolName := requestBody.ToolName

	// Use phone number from request if provided, otherwise use default
	if requestBody.PhoneNumber != "" {
		phoneNumber = requestBody.PhoneNumber
		log.Printf("MANUAL HANDLER: Using phone number from request: %s\n", phoneNumber)
	}

	// 4. Check if phone number is allowed.
	if !lo.Contains(pkg.GetAllowedMobileNumbers(), phoneNumber) {
		http.Error(w, "Phone number is not allowed", http.StatusForbidden)
		return
	}

	// 5. Read and return the dummy data file.
	filePath := "test_data_dir/" + phoneNumber + "/" + toolName + ".json"
	data, err := os.ReadFile(filePath)
	if err != nil {
		log.Printf("MANUAL HANDLER: Error reading test data file: %v\n", err)
		http.Error(w, "Could not read tool data", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(data)
}

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Println("Error loading .env file:", err)
	} else {
		log.Println(".env file loaded successfully.")
	}

	mcpFilePathDebug := os.Getenv("MCP_FILE_PATH")
	log.Printf("DEBUG: MCP_FILE_PATH read from env: %q", mcpFilePathDebug)

	authMiddleware = middlewares.NewAuthMiddleware()
	middlewares.SetDefaultAuthMiddleware(authMiddleware)
	s := server.NewMCPServer(
		"Hackathon MCP",
		"0.1.0",
		server.WithInstructions("A financial portfolio management MCP server that provides secure access to users' financial data through Fi Money, a financial hub for all things money. This MCP server enables users to:\n- Access comprehensive net worth analysis with asset/liability breakdowns\n- Retrieve detailed transaction histories for mutual funds and Employee Provident Fund accounts\n- View credit reports with scores, loan details, and account histories, this also contains user's date of birth that can be used for calculating their age\n\nIf the person asks, you can tell about Fi Money that it is money management platform that offers below services in partnership with regulated entities:\n\nAVAILABLE SERVICES:\n- Digital savings account with zero Forex cards\n- Invest in Indian Mutual funds, US Stocks (partnership with licensed brokers), Smart and Fixed Deposits.\n- Instant Personal Loans \n- Faster UPI and Bank Transfers payments\n- Credit score monitoring and reports\n\nIMPORTANT LIMITATIONS:\n- This MCP server retrieves only actual user data via Net worth tracker and based on consent provided by the user  and does not generate hypothetical or estimated financial information\n- In this version of the MCP server, user's historical bank transactions, historical stocks transaction data, salary (unless categorically declared) is not present. Don't assume these data points for any kind of analysis.\n\nCRITICAL INSTRUCTIONS FOR FINANCIAL DATA:\n\n1. DATA BOUNDARIES: Only provide information that exists in the user's Fi Money Net worth tracker. Never estimate, extrapolate, or generate hypothetical financial data.\n\n2. SPENDING ANALYSIS: If user asks about spending patterns, categories, or analysis tell the user we currently don't offer that data through the MCP:\n   - For comprehensive spending analysis and categorization, please use the Fi Money mobile app which provides detailed spending insights and budgeting tools.\"\n\n3. MISSING DATA HANDLING: If requested data is not available:\n   - Clearly state what data is missing\n   - Explain how user can connect additional accounts in Fi Money app\n   - Never fill gaps with estimated or generic information\n"),
		server.WithToolCapabilities(true),
		server.WithResourceCapabilities(true, true),
		server.WithLogging(),
		// server.WithToolHandlerMiddleware(authMiddleware.AuthMiddleware),
	)

	// Register tools with their specific handlers
	log.Println("DEBUG: Registering GetBankTransactions tool handler")
	s.AddTool(mcp.NewTool("GetBankTransactions", mcp.WithDescription("Retrieves a user's bank transaction history.")), pkg.GetBankTransactionsHandler)

	// Register GetNetWorth tool handler
	log.Println("DEBUG: Registering GetNetWorth tool handler")
	s.AddTool(mcp.NewTool("GetNetWorth", mcp.WithDescription("Retrieves a user's net worth summary.")), pkg.GetNetWorthHandler)

	// Register GetMFTransactions tool handler
	log.Println("DEBUG: Registering GetMFTransactions tool handler")
	s.AddTool(mcp.NewTool("GetMFTransactions", mcp.WithDescription("Retrieves a user's mutual fund transaction history.")), pkg.GetMFTransactionsHandler)

	// Register GetStockTransactions tool handler
	log.Println("DEBUG: Registering GetStockTransactions tool handler")
	s.AddTool(mcp.NewTool("GetStockTransactions", mcp.WithDescription("Retrieves a user's stock transaction history.")), pkg.GetStockTransactionsHandler)

	// Register GetEPFDetails tool handler
	log.Println("DEBUG: Registering GetEPFDetails tool handler")
	s.AddTool(mcp.NewTool("GetEPFDetails", mcp.WithDescription("Retrieves a user's EPF details.")), pkg.GetEPFDetailsHandler)

	// Register GetCreditReport tool handler
	log.Println("DEBUG: Registering GetCreditReport tool handler")
	s.AddTool(mcp.NewTool("GetCreditReport", mcp.WithDescription("Retrieves a user's credit report.")), pkg.GetCreditReportHandler)

	// Register GetGoals tool handler
	log.Println("DEBUG: Registering GetGoals tool handler")
	s.AddTool(mcp.NewTool("GetGoals", mcp.WithDescription("Retrieves all financial goals for a user.")), pkg.GetGoalsHandler)

	// Register AddGoal tool handler
	log.Println("DEBUG: Registering AddGoal tool handler")
	s.AddTool(mcp.NewTool("AddGoal", mcp.WithDescription("Adds a new financial goal for a user.")), pkg.AddGoalHandler)

	// Register UpdateGoal tool handler
	log.Println("DEBUG: Registering UpdateGoal tool handler")
	s.AddTool(mcp.NewTool("UpdateGoal", mcp.WithDescription("Updates an existing financial goal for a user.")), pkg.UpdateGoalHandler)

	// Register DeleteGoal tool handler
	log.Println("DEBUG: Registering DeleteGoal tool handler")
	s.AddTool(mcp.NewTool("DeleteGoal", mcp.WithDescription("Deletes a financial goal for a user.")), pkg.DeleteGoalHandler)

	for _, tool := range pkg.ToolList {
		if tool.Name != "GetBankTransactions" && tool.Name != "GetNetWorth" && tool.Name != "GetMFTransactions" && tool.Name != "GetStockTransactions" && tool.Name != "GetEPFDetails" && tool.Name != "GetCreditReport" && tool.Name != "GetGoals" && tool.Name != "AddGoal" && tool.Name != "UpdateGoal" && tool.Name != "DeleteGoal" {
			s.AddTool(mcp.NewTool(tool.Name, mcp.WithDescription(tool.Description)), dummyHandler)
		}
	}

	httpMux := http.NewServeMux()
	httpMux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))

	// Use our own handler for /mcp/stream
	httpMux.HandleFunc("/mcp/stream", manualMcpStreamHandler)
	streamableServer := server.NewStreamableHTTPServer(s,
		server.WithEndpointPath("/mcp"),
		server.WithStateLess(true), // Ensure stateless mode is enabled
	)
	log.Println("DEBUG: StreamableHTTPServer started in STATELESS mode (no session validation)")
	httpMux.Handle("/mcp/", streamableServer)
	// Keep the handlers for the web-based login flow.
	httpMux.HandleFunc("/mockWebPage", webPageHandler)
	httpMux.HandleFunc("/login", loginHandler)

	httpMux.HandleFunc("/user/", func(w http.ResponseWriter, r *http.Request) {
		log.Printf("INFO: [UserFileHandler] Received request for user data: %s", r.URL.Path)
		parts := strings.Split(r.URL.Path, "/")
		if len(parts) < 4 || parts[1] != "user" {
			log.Printf("WARNING: [UserFileHandler] Invalid user data path: %s", r.URL.Path)
			http.Error(w, "Invalid user data path", http.StatusBadRequest)
			return
		}

		phoneNumber := parts[2]
		fileName := parts[3]

		mcpFilePath := os.Getenv("MCP_FILE_PATH")
		if mcpFilePath == "" {
			log.Println("ERROR: [UserFileHandler] MCP_FILE_PATH is not set in .env. Cannot serve user data.")
			http.Error(w, "Server configuration error: MCP_FILE_PATH not set", http.StatusInternalServerError)
			return
		}

		filePath := filepath.Join(mcpFilePath, "test_data_dir", phoneNumber, fileName)
		log.Printf("DEBUG: [UserFileHandler] Attempting to serve file from: %s", filePath)

		http.ServeFile(w, r, filePath)
	})

	// --- NEW: CATCH-ALL HANDLER FOR DEBUGGING ---
	httpMux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		log.Printf("INFO: [CatchAllHandler] Received request to: %s %s from %s", r.Method, r.URL.Path, r.RemoteAddr)
		// For any request not matched by other handlers, this will catch it.
		// It's important that this is the last handler added if others are specific.
		// If it's the /mcp/call path that's failing, this might not show specifics
		// but will at least confirm the request hit the server.
		http.Error(w, "Not Found", http.StatusNotFound) // Return 404 for unmatched paths
	})
	// --- END NEW ---

	port := pkg.GetPort()
	log.Println("starting server on port:", port)
	if servErr := http.ListenAndServe(fmt.Sprintf(":%s", port), httpMux); servErr != nil {
		log.Fatalln("error starting server", servErr)
	}
}

func dummyHandler(_ context.Context, _ mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	return mcp.NewToolResultText("dummy handler"), nil
}

func webPageHandler(w http.ResponseWriter, r *http.Request) {
	sessionId := r.URL.Query().Get("sessionId")
	if sessionId == "" {
		http.Error(w, "sessionId is required", http.StatusBadRequest)
		return
	}

	tmpl, err := template.ParseFiles("static/login.html")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	data := struct {
		SessionId            string
		AllowedMobileNumbers []string
	}{
		SessionId:            sessionId,
		AllowedMobileNumbers: pkg.GetAllowedMobileNumbers(),
	}

	err = tmpl.Execute(w, data)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	sessionId := r.FormValue("sessionId")
	phoneNumber := r.FormValue("phoneNumber")

	if sessionId == "" || phoneNumber == "" {
		http.Error(w, "sessionId and phoneNumber are required", http.StatusBadRequest)
		return
	}

	//	authMiddleware.AddSession(sessionId, phoneNumber)

	tmpl, err := template.ParseFiles("static/login_successful.html")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	err = tmpl.Execute(w, nil)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}
