package main

import (
	"context"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
	"github.com/samber/lo"

	"github.com/epifi/fi-mcp-lite/middlewares"
	"github.com/epifi/fi-mcp-lite/pkg"
)

var authMiddleware *middlewares.AuthMiddleware

func main() {
	// We still create this server object, but we will NOT use it for the /mcp/stream endpoint.
	authMiddleware = middlewares.NewAuthMiddleware()
	s := server.NewMCPServer(
		"Hackathon MCP", "0.1.0",
		server.WithToolHandlerMiddleware(authMiddleware.AuthMiddleware),
	)
	for _, tool := range pkg.ToolList {
		s.AddTool(mcp.NewTool(tool.Name, mcp.WithDescription(tool.Description)), dummyHandler)
	}

	// Set up all HTTP endpoints.
	httpMux := http.NewServeMux()
	httpMux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))

	// Use our own simple, working handler for the /mcp/stream endpoint instead of the library's.
	httpMux.HandleFunc("/mcp/stream", manualMcpStreamHandler)

	// Keep the handlers for the web-based login flow.
	httpMux.HandleFunc("/mockWebPage", webPageHandler)
	httpMux.HandleFunc("/login", loginHandler)

	port := pkg.GetPort()
	log.Println("starting server on port:", port)
	if servErr := http.ListenAndServe(fmt.Sprintf(":%s", port), httpMux); servErr != nil {
		log.Fatalln("error starting server", servErr)
	}
}

// This is our new handler that replaces the broken library functionality.
func manualMcpStreamHandler(w http.ResponseWriter, r *http.Request) {
	// 1. Get Session ID from header.
	sessionId := r.Header.Get("X-Session-ID")
	log.Printf("MANUAL HANDLER: Checking session for ID '%s'\n", sessionId)

	// 2. Check session in our global store.
	phoneNumber, ok := middlewares.GetSession(sessionId)
	if !ok {
		log.Printf("MANUAL HANDLER: Session NOT FOUND for ID '%s'\n", sessionId)
		http.Error(w, "Invalid session ID", http.StatusBadRequest)
		return
	}
	log.Printf("MANUAL HANDLER: Session FOUND for ID '%s'. Using phone: %s\n", sessionId, phoneNumber)

	// 3. Decode the request body to get the tool name.
	var requestBody struct {
		ToolName string `json:"tool_name"`
	}
	if err := json.NewDecoder(r.Body).Decode(&requestBody); err != nil {
		http.Error(w, "Could not decode request body", http.StatusBadRequest)
		return
	}
	toolName := requestBody.ToolName

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

// dummyHandler is kept for compatibility but is not used in the main flow.
func dummyHandler(_ context.Context, _ mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	return mcp.NewToolResultText("dummy handler"), nil
}

// webPageHandler remains the same.
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

// loginHandler remains the same.
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
	middlewares.AddSession(sessionId, phoneNumber)
	log.Printf("MCP SERVER: Session successfully added for ID '%s' with phone '%s'\n", sessionId, phoneNumber)
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
