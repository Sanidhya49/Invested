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
	loginRequiredJson     = `{"status": "login_required","login_url": "%s","message": "Needs to login first by going to the login url.\nShow the login url as clickable link if client supports it. Otherwise display the URL for users to copy and paste into a browser. \nAsk users to come back and let you know once they are done with login in their browser"}`
	defaultAuthMiddleware *AuthMiddleware
)

type AuthMiddleware struct {
	sessionStore map[string]string
}

func NewAuthMiddleware() *AuthMiddleware {
	return &AuthMiddleware{
		sessionStore: make(map[string]string),
	}
}

func (m *AuthMiddleware) AuthMiddleware(next server.ToolHandlerFunc) server.ToolHandlerFunc {
	return func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		// fetch sessionId from context
		// this gets populated for every tool call
		sessionId := server.ClientSessionFromContext(ctx).SessionID()
		phoneNumber, ok := m.sessionStore[sessionId]
		if !ok {
			loginUrl := m.getLoginUrl(sessionId)
			return mcp.NewToolResultText(fmt.Sprintf(loginRequiredJson, loginUrl)), nil
		}
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

// GetLoginUrl fetches dynamic login url for given sessionId
func (m *AuthMiddleware) getLoginUrl(sessionId string) string {
	return fmt.Sprintf("http://localhost:%s/mockWebPage?sessionId=%s", pkg.GetPort(), sessionId)
}

func (m *AuthMiddleware) AddSession(sessionId, phoneNumber string) {
	m.sessionStore[sessionId] = phoneNumber
}

// Set the defaultAuthMiddleware for global session access
func SetDefaultAuthMiddleware(m *AuthMiddleware) {
	defaultAuthMiddleware = m
}

// GetSession retrieves a session from the default AuthMiddleware instance
func GetSession(sessionId string) (string, bool) {
	if defaultAuthMiddleware == nil {
		return "", false
	}
	phone, ok := defaultAuthMiddleware.sessionStore[sessionId]
	return phone, ok
}
