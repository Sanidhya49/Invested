# fi-mcp-dev

A minimal, hackathon-ready version of the Fi MCP server. This project provides a lightweight mock server for use in hackathons, demos, and development, simulating the core features of the production Fi MCP server with dummy data and simplified authentication.

## Purpose

- **fi-mcp-dev** is designed for hackathon participants and developers who want to experiment with the Fi MCP API without accessing real user data or production systems.
- It serves dummy financial data and uses a dummy authentication flow, making it safe and easy to use in non-production environments.

## Features

- **Simulates Fi MCP API**: Implements endpoints for net worth, credit report, EPF details, mutual fund transactions, and bank transactions.
- **Dummy Data**: All responses are served from static JSON files in `test_data_dir/`, representing various user scenarios.
- **Dummy Authentication**: Simple login flow using allowed phone numbers (directory names in `test_data_dir/`). No real OTP or user verification.
- **Hackathon-Ready**: No real integrations, no sensitive data, and easy to reset or extend.

## Directory Structure

- `main.go` — Entrypoint, sets up the server and endpoints.
- `middlewares/auth.go` — Implements dummy authentication and session management.
- `test_data_dir/` — Contains directories named after allowed phone numbers. Each directory holds JSON files for different API responses (e.g., `fetch_net_worth.json`).
- `static/` — HTML files for the login and login-successful pages.

## Dummy Data Scenarios

The dummy data covers a variety of user states. Example scenarios:

- **All assets connected**: Banks, EPF, Indian stocks, US stocks, credit report, large or small mutual fund portfolios.
- **All assets except bank account**: No bank account, but other assets present.
- **Multiple banks and UANs**: Multiple bank accounts and EPF UANs, partial transaction coverage.
- **No assets connected**: Only a savings account balance is present.
- **No credit report**: All assets except credit report.

## Test Data Scenarios

| Phone Number | Description                                                                                                                                                                                                                                        |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1111111111  | No assets connected. Only saving account balance present                                                                                                                                                                                                                                            |
| 2222222222  | All assets connected (Banks account, EPF, Indian stocks, US stocks, Credit report). Large mutual fund portfolio with 9 funds                                                                                                                                                                        |
| 3333333333  | All assets connected (Banks account, EPF, Indian stocks, US stocks, Credit report). Small mutual fund portfolio with only 1 fund                                                                                                                                                                    |
| 4444444444  | All assets connected (Banks account, EPF, Indian stocks, US stocks). Small mutual fund portfolio with only 1 fund. With 2 UAN account connected . With 3 different bank with multiple account in them . Only have transactions for 2 bank accounts                                                  |
| 5555555555  | All assets connected except credit score (Banks account, EPF, Indian stocks, US stocks). Small mutual fund portfolio with only 1 fund. With 3 different bank with multiple account in them. Only have transactions for 2 bank accounts                                                              |
| 6666666666  | All assets connected except bank account (EPF, Indian stocks, US stocks). Large mutual fund portfolio with 9 funds. No bank account connected                                                                                                                                                       |
| 7777777777  | Debt-Heavy Low Performer. A user with mostly underperforming mutual funds, high liabilities (credit card & personal loans). Poor MF returns (XIRR < 5%). No diversification (all equity, few funds). Credit score < 650. High credit card usage, multiple loans. Negligible net worth or negative.  |
| 8888888888  | SIP Samurai. Consistently invests every month in multiple mutual funds via SIP. 3–5 active SIPs in MFs. Moderate returns (XIRR 8–12%).                                                                                                                                                              |
| 9999999999  | Fixed Income Fanatic. Strong preference for low-risk investments like debt mutual funds and fixed deposits. 80% of investments in debt MFs. Occasional gold ETF (Optional). Consistent but slow net worth growth (XIRR ~ 8-10%).                                                                    |
| 1010101010  | Precious Metal Believer. High allocation to gold and fixed deposits, minimal equity exposure. Gold MFs/ETFs ~50% of investment. Conservative SIPs in gold funds. FDs and recurring deposits. Minimal equity exposure.                                                                               |
| 1212121212  | Dormant EPF Earner. Has EPF account but employer stopped contributing; balance stagnant. EPF balance > ₹2 lakh. Interest not being credited. No private investment.                                                                                                                                 |
| 1414141414  | Salary Sinkhole. User’s salary is mostly consumed by EMIs and credit card bills. Salary credit every month. 70% goes to EMIs and credit card dues. Low or zero investment. Credit score ~600–650.                                                                                                   |
| 1313131313  | Balanced Growth Tracker. Well-diversified portfolio with EPF, MFs, stocks, and some US exposure. High EPF contribution. SIPs in equity & hybrid MFs. International MFs/ETFs 10–20%. Healthy net worth growth. Good credit score (750+).                                                             |
| 2020202020  | Starter Saver. Recently started investing, low ticket sizes, few transactions. Just 1–2 MFs, started < 6 months ago. SIP ₹500–₹1000. Minimal bank balance, no debt.                                                                                                                                 |
| 1515151515  | Ghost Portfolio. Has old investments but hasn’t made any changes in years. No MF purchase/redemption in 3 years. EPF stagnant or partially withdrawn. No SIPs or salary inflow. Flat or declining net worth.                                                                                        |
| 1616161616  | Early Retirement Dreamer. Optimizing investments to retire by 40. High savings rate, frugal lifestyle. Aggressive equity exposure (80–90%). Lean monthly expenses. Heavy SIPs + NPS + EPF contributions. No loans, no luxury spending. Targets 30x yearly expenses net worth.                       |
| 1717171717  | The Swinger. Regularly buys/sells MFs and stocks, seeks short-term gains. Many MF redemptions within 6 months. Equity funds only, high churn. No SIPs. Short holding periods. High txn volume in bank account.                                                                                      |
| 1818181818  | Passive Contributor. No personal income, but has EPF from a past job and joint bank accounts. Old EPF, no current contributions. No active SIPs. Transactions reflect shared household spending. No credit score record (no loans/credit card).                                                     |
| 1919191919  | Section 80C Strategist. Uses ELSS, EPF, NPS primarily to optimize taxes. ELSS SIPs in Q4 (Jan–Mar). EPF active. NPS data if available. No non-tax-saving investments. Low-risk debt funds as balance.                                                                                               |
| 2121212121  | Dual Income Dynamo. Has freelance + salary income; cash flow is uneven but investing steadily. Salary + multiple credits from UPI apps. MF investments irregular but increasing. High liquidity in bank accounts. Credit score above 700. Occasional business loans or overdraft.                   |
| 2222222222  | Sudden Wealth Receiver. Recently inherited wealth, learning how to manage it. Lump sum investments across categories. High idle cash in bank. Recent MF purchases, no SIPs yet. No credit history or debt. EPF missing or dormant.                                                                  |
| 2323232323  | Overseas Optimizer. NRI who continues to manage Indian EPF, MFs, and bank accounts. Large EPF corpus. No salary inflows, occasional foreign remittances. MF transactions in bulk. Indian address missing or outdated. No credit card usage in India.                                                |
| 2424242424  | Mattress Money Mindset. Doesn’t trust the market; everything is in bank savings and FDs. 95% net worth in FDs/savings. No mutual funds or stocks. EPF maybe present. No debt or credit score. Low but consistent net worth growth.                                                                  |
| 2525252525  | Live-for-Today. High income but spends it all. Investments are negligible or erratic. Salary > ₹2L/month. High food, shopping, travel spends. No SIPs, maybe one-time MF buy. Credit card dues often roll over. Credit score < 700, low or zero net worth.                                          |

## Example: Dummy Data File

A sample `fetch_net_worth.json` (truncated for brevity):

```json
{
  "netWorthResponse": {
    "assetValues": [
      {"netWorthAttribute": "ASSET_TYPE_MUTUAL_FUND", "value": {"currencyCode": "INR", "units": "84642"}},
      {"netWorthAttribute": "ASSET_TYPE_EPF", "value": {"currencyCode": "INR", "units": "211111"}}
    ],
    "liabilityValues": [
      {"netWorthAttribute": "LIABILITY_TYPE_VEHICLE_LOAN", "value": {"currencyCode": "INR", "units": "5000"}}
    ],
    "totalNetWorthValue": {"currencyCode": "INR", "units": "658305"}
  }
}
```

## Authentication Flow

- When a tool/API is called, the server checks for a valid session.
- If not authenticated, the user is prompted to log in via a web page (`/mockWebPage?sessionId=...`).
- Enter any allowed phone number (see directories in `test_data_dir/`). OTP is not validated.
- On successful login, the session is stored in memory for the duration of the server run.

## Running the Server

### Prerequisites
- Go 1.23 or later ([installation instructions](https://go.dev/doc/install))

### Install dependencies
```sh
go mod tidy
```

### Start the server
```sh
FI_MCP_PORT=8080 go run .
```

The server will start on [http://localhost:8080](http://localhost:8080).

## Usage
- Follow instructions in this [guide](https://fi.money/features/getting-started-with-fi-mcp) to setup client
- Replace url with locally running server, for example: `http://localhost:8080/mcp/stream`
- When prompted for login, use one of the above phone numbers
- Otp/Passcode can be anything on the webpage

