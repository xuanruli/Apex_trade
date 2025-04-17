# Big Bucks Project Requirements

## Core Requirements

## User Interface
### Home Page for Unauthenticated Users
- The system shall have a home page for unauthenticated users. 
- The home page shall have a button to direct users to the authentication page. 
- The system shall provide a link to a list of assets available on the platform. 
- The system shall provide a link to the market page.

### User Authentication Page
- The system shall have an authentication page where users can enter their username and password.
- The authentication page shall provide a signup button leading to the registration page.
- The system shall enforce two-factor authentication for users.

### New User Registration Page
- The system shall provide a registration page when users click the signup button.
- The registration page shall require users to enter and confirm a username and password.

### Authenticated Home Page for Regular Users
- The system shall display a list of stocks including symbol, current price, cost basis, and total profit/loss.
- The system shall provide a search bar for users to find new assets.
- The system shall display account details, including total account worth, daily return, and beta.
- The system shall provide a button leading to the Analysis page.

### Market Page
- The system shall display graphs on returns of major stock exchanges and global assets.
- The system shall display trending financial news.
- The system shall provide links to the Analysis page.

### Analysis Page
- The system shall display a dashboard of the portfolio earnings over its lifetime.
- The system shall display relevant statistics such as beta and recommendations for investment decisions.

### History Screen
- The system shall display a history page listing past transactions, including asset name, ticker symbol, buy/sell action, price, and total amount.
- The system shall allow users to click on an item to navigate to the asset’s information page.

### Asset Information Page
- The system shall display the asset name, trading price, and daily volume.
- The system shall display a graph illustrating stock movements.
- The system shall allow users to buy or sell stocks, which will update their portfolio.
- The system shall display relevant news below the stock price movement graph.

### Report Page
- The system shall allow users to generate a document aggregating recommendations made by the platform and send it via email.
- The system shall allow users to email a list of their portfolio holdings and analysis.

## Data Integration
- The system shall integrate with an external data provider using a RESTful API for real-time and historical stock market data.
- The system shall use Alpha Vantage as the primary data source.
- The system shall send GET requests to Alpha Vantage with specified parameters.
- The system shall parse and extract relevant data fields (OHLC, volume, RSI).
- The system shall provide error handling for failed API requests.
- If an invalid symbol is entered, the system shall return a "Symbol Not Found" message.

## Charting
- The system shall provide financial charting capabilities using Plotly.
- The system shall support the following chart types:
  - Candlestick Chart (OHLC Data)
  - Bar Chart (Trading Volume)
  - Line Chart (RSI - Relative Strength Index)
- The system shall provide an API endpoint to retrieve and display charts.

## Users
- The system shall allow normal users to input ticker symbols, view stock charts, and manage their portfolio.
- The system shall allow users to track profit and loss and view their efficient frontier.
- The system shall allow administrative users to monitor portfolios, issue margin calls, and calculate users’ P&L.

## Administrative Functionality
- The system shall allow administrators to view all users and their portfolio details.
- The system shall allow administrators to disable user accounts.
- The system shall allow users to reset their passwords.
- The system shall allow administrators to view all system transactions.
- The system shall provide analytical tools for administrators to assess portfolio risk and performance.

## Infrastructure
- The system shall maintain a running instance on Duke’s Virtual Machines.
- The system shall start automatically when the virtual machine reboots.

## Database
- The system shall store all relevant data in a relational database.
- The system shall initially use SQLite and migrate to MySQL or PostgreSQL in the future.
- The system shall include tables for users, transactions, stock data, and market analytics.
- The system shall support real-time data streaming for live price updates.

## CI/CD Pipeline
- The system shall implement CI/CD automation for building, testing, security scanning, and deployment.
- The system shall trigger builds on every commit.
- The system shall execute automated test suites for frontend, backend, and database.
- The system shall integrate GitLab SAST for security scanning.
- The system shall automatically deploy to the Virtual Cloud Machine.
- The system shall include rollback mechanisms for failed deployments.

## Security Analysis
- The system shall include a Data Flow Diagram (DFD) identifying assets, actors, and threats.
- The system shall perform a STRIDE analysis to assess security risks.
- The system shall run Semgrep for static security scanning.
- The system shall run OWASP ZAP for dynamic security testing.

## System Architecture
- The system shall provide a System Context Diagram illustrating major components and data flows.
- The system shall provide a Container Diagram showing key system components and interactions.
- The system shall provide a Component Diagram detailing API routes, database models, and business logic.
- The system shall provide a Code Diagram outlining the structure of the codebase.

## Logging and Monitoring
- The system shall log security events using a structured JSON format.
- The system shall log database changes, including additions and deletions.
- The system shall log database queries to assist debugging.

## OAuth2 Integration
- The system shall support authentication via Google, Apple, and Microsoft.
- The system shall provide traditional email/password authentication as a fallback.
- The system shall automatically register OAuth users upon first login.
- The system shall retrieve and store user email, full name, profile picture (optional), and date of birth (if available).

## Containerize Your Application
- The system shall include a Dockerfile for containerization.
- The system shall use Docker Compose to manage deployments.
- The system shall define services for the Flask backend and a persistent SQLite volume.
