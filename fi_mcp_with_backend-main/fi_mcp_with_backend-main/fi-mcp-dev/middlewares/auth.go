package middlewares

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
	"github.com/samber/lo"

	"github.com/epifi/fi-mcp-lite/pkg"
)

var (
	loginRequiredJson = `{"status": "login_required","login_url": "%s","message": "Needs to login first by going to the login url.\nShow the login url as clickable link if client supports it. Otherwise display the URL for users to copy and paste into a browser. \nAsk users to come back and let you know once they are done with login in their browser"}`
)

// Use a global map to solve the architectural issue.
var globalSessionStore = make(map[string]string)

// This struct is kept for compatibility but its internal store is no longer used.
type AuthMiddleware struct{}

func NewAuthMiddleware() *AuthMiddleware {
	return &AuthMiddleware{}
}

// This function is now used by the /login handler in main.go.
func AddSession(sessionId, phoneNumber string) {
	globalSessionStore[sessionId] = phoneNumber
}

// This new function is used by our manual handler in main.go.
func GetSession(sessionId string) (string, bool) {
	phone, ok := globalSessionStore[sessionId]
	return phone, ok
}

// This middleware function is no longer used by the main API flow but is kept for compatibility.
func (m *AuthMiddleware) AuthMiddleware(next server.ToolHandlerFunc) server.ToolHandlerFunc {
	return func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		sessionId := server.ClientSessionFromContext(ctx).SessionID()

		log.Printf("MCP MIDDLEWARE: Checking session for ID '%s'\n", sessionId)

		phoneNumber, ok := globalSessionStore[sessionId]
		if !ok {
			log.Printf("MCP MIDDLEWARE: Session NOT FOUND for ID '%s'\n", sessionId)
			loginUrl := m.getLoginUrl(sessionId)
			return mcp.NewToolResultText(fmt.Sprintf(loginRequiredJson, loginUrl)), nil
		}

		log.Printf("MCP MIDDLEWARE: Session FOUND for ID '%s'. Using phone: %s\n", sessionId, phoneNumber)

		if !lo.Contains(pkg.GetAllowedMobileNumbers(), phoneNumber) {
			return mcp.NewToolResultError("phone number is not allowed"), nil
		}

		ctx = context.WithValue(ctx, "phone_number", phoneNumber)
		toolName := req.Params.Name
		data, readErr := os.ReadFile("test_data_dir/" + phoneNumber + "/" + toolName + ".json")
		if readErr != nil {
			log.Println("error reading test data file", readErr)
			return mcp.NewToolResultError("error reading test data file"), nil
		}
		return mcp.NewToolResultText(string(data)), nil
	}
}

func (m *AuthMiddleware) getLoginUrl(sessionId string) string {
	return fmt.Sprintf("http://localhost:%s/mockWebPage?sessionId=%s", pkg.GetPort(), sessionId)
}
