# Fi MCP with Backend

This project provides a minimal, hackathon-ready mock implementation of the Fi MCP server (in Go) and a Python backend that interacts with it and external APIs (e.g., Gemini).

---

## Directory Structure

- `fi-mcp-dev/` — Go-based mock MCP server
  - Serves dummy financial data and simulates authentication
  - Data is stored in `test_data_dir/`
- `python-backend/` — Python FastAPI backend
  - Handles API requests, integrates with Gemini, and proxies to the MCP server

---

## MCP Server Setup (`fi-mcp-dev`)

1. **Prerequisites**
   - Go 1.23 or later ([installation instructions](https://go.dev/doc/install))

2. **Navigate to MCP server directory**
   ```bash
   cd fi-mcp-dev
   ```

3. **Install Go dependencies**
   ```bash
   go mod tidy
   ```

4. **Start the MCP server**
   ```bash
   FI_MCP_PORT=8080 go run .
   ```
   The server will start on [http://localhost:8080](http://localhost:8080)

---

## Python Backend Setup (`python-backend`)

1. **Navigate to Python backend directory**
   ```bash
   cd python-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # On Linux/macOS
   source venv/bin/activate
   # On Windows
   venv\Scripts\activate
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**

   Create a `.env` file in `python-backend/` with the following keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   FI_MCP_SERVER_URL=http://localhost:8080
   MCP_AUTH_PHONE_NUMBER=your_test_phone_number
   ```

6. **Start the Python server**
   ```bash
   python main.py
   ```

---

## Notes

- The Go server uses dummy data from `fi-mcp-dev/test_data_dir/` for different phone numbers.
- The Python backend expects the MCP server to be running and accessible at the URL specified in `FI_MCP_SERVER_URL`.
- For development and hackathons only. **Do not use in production.**

---