# Quick Start Guide

Get up and running with the Advanced Aeromedical Evidence Review & Research System in 5 minutes!

## 🚀 Prerequisites

- Python 3.8+ installed
- Git installed
- API keys ready (see below)

## 📦 Installation (2 minutes)

1. **Clone and enter the project:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 🔑 Configuration (1 minute)

Create a `.env` file in the project root:

```env
# Minimum required
OPENAI_API_KEY=sk-...your-key...
FLOWISE_API_KEY=...your-key...

# For PRISMA features (optional)
PPLX_API_KEY=pplx-...your-key...
XAI_API_KEY=xai-...your-key...
```

## 🎯 First Run (2 minutes)

1. **Start the application:**
   ```bash
   python run.py
   ```

2. **Try these example queries:**

   **General Research:**
   ```
   > What are the latest advances in pilot fatigue management?
   ```

   **Aeromedical Risk Assessment:**
   ```
   > /aero
   > Assess the risk for a 45-year-old pilot with controlled diabetes
   ```

   **PRISMA Systematic Review:**
   ```
   > /prisma
   > Follow the guided workflow...
   ```

## 📝 Essential Commands

| Command | What it does |
|---------|--------------|
| `/help` | Show all commands |
| `/modes` | List available AI agents |
| `/smart` | Auto-select best agent (default) |
| `/export` | Save last response |
| `/jobs` | Check background tasks |
| `/quit` | Exit application |

## 🔄 Workflow Example

1. **Ask a question** in smart mode (auto-selected agent)
2. **Review the response** with automatic query optimization
3. **Export results** with `/export` for documentation
4. **Try different agents** with `/transfer <mode>` to compare

## 💡 Pro Tips

- **Smart Mode**: Let the system choose the best agent automatically
- **Background Jobs**: Deep research runs in background - check with `/jobs`
- **Query Optimization**: Every query is automatically enhanced for scientific accuracy
- **Export Often**: Use `/export` to save important responses

## 🆘 Need Help?

- Type `?` or `/help` for command reference
- Check `DOCUMENTATION.md` for detailed guide
- See `TROUBLESHOOTING.md` for common issues

## 🎉 Ready to Research!

You're all set! The system will automatically:
- Optimize your queries for scientific research
- Select the best AI agent for your needs
- Provide citations and structured outputs
- Handle complex systematic reviews

Happy researching! 🔬