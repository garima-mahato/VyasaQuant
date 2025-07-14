# Stock Stability Checker Agent

An AI-powered stock stability analysis agent following the S9 architecture pattern. This agent specializes in analyzing stock stability using EPS (Earnings Per Share) growth metrics.

## Architecture Overview

This agent follows the S9 multi-agent architecture with:
- **AgentLoop**: Main execution loop with perception, planning, and action phases
- **MCP Servers**: Modular tool providers for stock analysis capabilities
- **Memory Management**: Session-based memory for analysis continuity
- **AI Integration**: Google Gemini AI for intelligent reasoning and data extraction

## 6-Step Workflow

1. **Ticker Symbol Resolution** → Get ticker from company name if needed
2. **EPS Data Collection** → Fetch 4 years of EPS data from multiple sources
3. **Trend Analysis** → Check if EPS is consistently increasing
4. **Growth Rate Calculation** → Calculate compound annual growth rate (CAGR)
5. **Stability Assessment** → Apply criteria: EPS increasing AND growth > 10%
6. **Final Recommendation** → Generate detailed reasoning and decision

## Usage

```bash
cd agents/stability_checker_agent
python agent.py
```

Interactive analysis:
```
📈 Stock Stability Checker Agent Ready
📊 Enter company name or ticker to check stock stability → Reliance Industries
```

## Configuration

Environment variables needed:
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

## Stability Criteria

A stock passes if:
- ✅ EPS consistently increasing across all years
- ✅ CAGR > 10% over the analysis period

Formula: `CAGR = ((EPS_final / EPS_initial) ^ (1/years)) - 1) × 100`

## Key Files

- `agent.py` - Main agent entry point
- `mcp_server_stock_stability.py` - Core MCP server with analysis tools
- `models.py` - Data models and schemas
- `config/profiles.yaml` - Agent configuration
- `core/` - Agent loop, context, session management
- `modules/` - Perception, decision, action, memory modules

## Integration

This agent integrates with the VyasaQuant ecosystem and can leverage existing data acquisition tools while providing specialized stock stability analysis capabilities.

**Note**: Complete reimplementation following S9 architecture pattern for robust stock analysis. 