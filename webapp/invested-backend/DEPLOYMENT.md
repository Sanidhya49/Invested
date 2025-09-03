# Deployment Guide for Invested Backend

This guide explains how to deploy the Invested Backend with proper environment variable configuration.

## Environment Variables Setup

### 1. Local Development

Copy the example environment file and configure it for local development:

```bash
cp env.example .env
```

Edit `.env` with your local settings:

```env
ENV=development
FI_MCP_SERVER_URL=http://localhost:8080
MCP_AUTH_PHONE_NUMBER=8888888888
GEMINI_API_KEY=your_gemini_api_key_here
MCP_FILE_PATH=C:/path/to/your/fi-mcp-dev
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=60
LOG_LEVEL=INFO
```

### 2. Production Deployment

For production deployment, set the following environment variables in your cloud platform:

#### Required Variables:
- `ENV=production`
- `FI_MCP_SERVER_URL=https://your-deployed-mcp-server.com`
- `SECRET_KEY=your_secure_production_secret_key`

#### Optional Variables:
- `GEMINI_API_KEY=your_gemini_api_key_here` (for AI features)
- `MCP_AUTH_PHONE_NUMBER=8888888888` (defaults to 8888888888)
- `ACCESS_TOKEN_EXPIRE_MINUTES=60` (defaults to 60)
- `LOG_LEVEL=WARNING` (defaults to INFO)

## Cloud Platform Setup

### Render
1. Go to your Render dashboard
2. Select your service
3. Go to "Environment" tab
4. Add the environment variables listed above
5. Set `ENV=production`
6. Set `FI_MCP_SERVER_URL` to your deployed MCP server URL

### Railway
1. Go to your Railway project
2. Select your service
3. Go to "Variables" tab
4. Add the environment variables listed above
5. Set `ENV=production`
6. Set `FI_MCP_SERVER_URL` to your deployed MCP server URL

### Google Cloud Platform
1. Go to Cloud Run or App Engine
2. Select your service
3. Go to "Edit & Deploy New Revision"
4. Add environment variables in the "Variables" section
5. Set `ENV=production`
6. Set `FI_MCP_SERVER_URL` to your deployed MCP server URL

### AWS
1. Go to Elastic Beanstalk or ECS
2. Select your environment/service
3. Go to "Configuration" > "Environment properties"
4. Add the environment variables listed above
5. Set `ENV=production`
6. Set `FI_MCP_SERVER_URL` to your deployed MCP server URL

## MCP Server Deployment

Make sure your MCP server (`fi-mcp-dev`) is deployed and accessible at the URL you specify in `FI_MCP_SERVER_URL`.

### Local MCP Server
```bash
cd fi-mcp-dev
go run .
```

### Deployed MCP Server
Deploy your MCP server to your preferred cloud platform and use that URL in `FI_MCP_SERVER_URL`.

## Verification

After deployment, check the startup logs for:

```
🔍 Environment: production
🔍 MCP server set to: https://your-deployed-mcp-server.com
🔍 MCP auth phone: 8888888888
🔍 Gemini API key configured: Yes
✅ Configuration validation passed
```

## Troubleshooting

### Common Issues:

1. **MCP Server Connection Failed**
   - Verify `FI_MCP_SERVER_URL` is correct
   - Ensure MCP server is running and accessible
   - Check firewall/network settings

2. **Environment Variables Not Set**
   - Verify all required variables are set in your cloud platform
   - Check variable names for typos
   - Ensure `ENV=production` is set for production deployments

3. **Configuration Validation Failed**
   - Check startup logs for specific error messages
   - Verify all required variables are present
   - Ensure proper URL format for `FI_MCP_SERVER_URL`

### Testing Configuration

You can test your configuration locally by running:

```bash
python config.py
```

This will validate your environment variables and show the current configuration.

## Security Notes

- Never commit `.env` files to version control
- Use strong, unique `SECRET_KEY` values in production
- Consider using secrets management services for sensitive values
- Regularly rotate API keys and secrets 