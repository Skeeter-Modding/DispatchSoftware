# SRM Dispatch - Smyrna Ready Mix Dispatch System

A comprehensive AI-powered dispatch management system for dump truck and aggregate hauling operations.

**Created by:** [Skeeter-Modding](https://github.com/Skeeter-Modding)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-Proprietary-red.svg)

---

## Features

### Core Dispatch Operations
- **Driver Management** - Track drivers, contact info, home locations
- **Fleet Management** - Trucks with capacity, type, and GPS device linking
- **Daily Assignments** - Link drivers to trucks for daily operations
- **Job Management** - Manage construction sites and delivery locations
- **Order Management** - Create orders with tonnage tracking and fulfillment status
- **Load Dispatch** - Create and track individual loads with real-time status

### AI-Powered Intelligence
- **AI Dispatch Optimization** - Smart truck-to-order matching based on:
  - Productivity calculations (tons/day per route)
  - Deadhead distance minimization
  - Workload balancing across drivers
  - Truck type suitability for materials
- **AI Assistant** - Conversational assistant powered by Groq (Llama 3.3 70B)
  - Ask questions about operations in natural language
  - Get real-time status updates
  - Query drivers, loads, orders, and trucks
- **Automatic Tonnage Splitting** - Large orders automatically split across multiple trucks

### Real-Time Tracking
- **Samara GPS Integration** - Automatic location updates from GPS devices
- **Geofence Detection** - Auto-update load status based on location
- **Status Workflow**: `Assigned → En Route → At Job → Delivering → Complete`
- **Live Dashboard** - Real-time overview with auto-refresh

### Order Fulfillment
- **Tonnage Tracking** - Track tons ordered vs. delivered
- **Partial Load Handling** - Support for multi-day order fulfillment
- **Priority Management** - Urgent, high, normal, low priority levels

---

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Skeeter-Modding/DispatchSoftware.git
   cd DispatchSoftware
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** (optional for AI features)
   ```bash
   export GROQ_API_KEY=your_groq_api_key
   export SECRET_KEY=your_secret_key
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the system**
   Open browser to: `http://localhost:5500`

### Deploy to Render

1. Connect your GitHub repository to [Render](https://render.com)
2. Create a new Web Service
3. Set environment variables:
   - `GROQ_API_KEY` - Your Groq API key for AI features
   - `SECRET_KEY` - A secure random string
4. Deploy

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask 3.0 (Python 3.11+) |
| Database | SQLite |
| AI/LLM | Groq API (Llama 3.3 70B) |
| Frontend | Bootstrap 5, Vanilla JS |
| Icons | Font Awesome 6 |
| Deployment | Render, Gunicorn |

---

## Security Features

- **Rate Limiting** - 100 requests/minute per IP on AI endpoints
- **Prompt Injection Protection** - Input sanitization and hardened system prompts
- **XSS Prevention** - Output sanitization and Content Security Policy
- **Security Headers** - X-Frame-Options, X-Content-Type-Options, etc.
- **SQL Injection Protection** - Parameterized queries throughout
- **Input Validation** - Whitelist validation on status updates

---

## Project Structure

```
DispatchSoftware/
├── app.py                    # Main Flask application
├── ai_knowledge.py           # AI dispatch engine and scoring
├── requirements.txt          # Python dependencies
├── database/
│   ├── schema.sql           # Database schema
│   └── srm_dispatch.db      # SQLite database
└── templates/
    ├── base.html            # Base template
    ├── dashboard.html       # Main dashboard
    ├── dispatch.html        # Dispatch interface
    ├── orders.html          # Order management
    ├── loads.html           # Load tracking
    ├── ai_assistant.html    # AI chat interface
    ├── drivers.html         # Driver management
    ├── trucks.html          # Fleet management
    └── samara.html          # GPS integration
```

---

## API Endpoints

### AI Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai/optimize` | POST | Get AI dispatch recommendations |
| `/api/ai/chat` | POST | Chat with AI assistant |
| `/api/ai/apply-recommendation` | POST | Apply an AI recommendation |

### Load Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/loads/<id>/status` | POST | Update load status |
| `/api/loads/create` | POST | Create new load |

### Orders
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/orders` | GET/POST | List/create orders |
| `/api/orders/<id>` | DELETE | Delete order |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | For AI | Groq API key for AI assistant |
| `SECRET_KEY` | Recommended | Flask session secret key |

---

## Usage

### Daily Workflow

1. **Morning Setup**
   - Go to Dispatch → Create driver assignments
   - Link drivers to trucks for the day

2. **Create Orders**
   - Orders → New Order
   - Set customer, material, tonnage, priority

3. **AI Optimization**
   - Click "AI Optimize" on Orders page
   - Review recommendations (shows truck assignments, tons/day capacity)
   - Click "Apply" or "Apply All" to create loads

4. **Monitor Operations**
   - Dashboard for overview
   - Loads page for detailed tracking
   - AI Assistant for questions

### AI Assistant Examples

Ask the AI assistant questions like:
- "What's the status today?"
- "Who's driving today?"
- "How many pending orders do we have?"
- "Tell me about loads going to Brunswick"

---

## Contributing

This is a proprietary system for Smyrna Ready Mix operations.

---

## License

Proprietary - Smyrna Ready Mix Internal Use

---

## Author

**Created by [Skeeter-Modding](https://github.com/Skeeter-Modding)**

For support, open an issue on GitHub.
