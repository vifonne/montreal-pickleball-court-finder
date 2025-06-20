# Montreal Pickleball Court Finder

A Python script that searches for available pickleball courts in Montreal using the official city API. This tool can be hosted on GitHub and easily fetched by Claude or other AI assistants to help users find and book pickleball courts.

## Features

- 🏓 Real-time search for available pickleball courts across Montreal
- 📅 Search by specific date and time
- 🏢 Covers all Montreal boroughs
- 💰 Price information and availability status
- ⚡ Fast API response with comprehensive error handling
- 🤖 Designed for easy integration with AI assistants

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/montreal-pickleball-court-finder.git
cd montreal-pickleball-court-finder

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from pickleball_search import search_pickleball_courts
import json

# Search for courts tomorrow at 5 PM
result = search_pickleball_courts("2025-06-21", "17:00")
print(json.dumps(result, indent=2))
```

### Command Line Usage

```bash
# Basic usage - search for courts on a specific date and time
python pickleball_search.py 2025-06-20 17:00

# Use convenient date keywords
python pickleball_search.py tomorrow 18:00
python pickleball_search.py today 12:00

# Limit the number of results shown
python pickleball_search.py tomorrow 17:00 --limit 5

# Get raw JSON output (useful for Claude or other tools)
python pickleball_search.py 2025-06-21 09:00 --json

# Get help
python pickleball_search.py --help
```

## API Details

The script uses Montreal's official recreation API:
- **Endpoint**: `https://loisirs.montreal.ca/IC3/api/U6510/public/search/`
- **Method**: POST
- **Authentication**: Requires `X-Tenant-Id: 1` header
- **Coverage**: All Montreal boroughs (IDs: 9,2,19,1,8)

## Usage Examples

### Search for Available Courts

```python
from pickleball_search import search_pickleball_courts

# Search for courts on a specific date at 5 PM
result = search_pickleball_courts("2025-06-20", "17:00")

if result["status"] == "success":
    print(f"Found {result['total_found']} courts:")
    for court in result["results"]:
        print(f"- {court['name']} at {court['location']}")
        print(f"  Time: {court['start_time']}-{court['end_time']}")
        print(f"  Price: ${court['price']} {court['currency']}")
        print(f"  Can Reserve: {court['can_reserve']}")
        print()
else:
    print(f"Error: {result['message']}")
```

### Using with Claude

Claude can fetch and execute this script directly from GitHub:

```python
# Claude will fetch the script from:
# https://raw.githubusercontent.com/yourusername/montreal-pickleball-court-finder/main/pickleball_search.py

# For programmatic usage:
result = search_pickleball_courts("2025-06-20", "17:00")

# For command line usage (when Claude runs shell commands):
# python pickleball_search.py 2025-06-20 17:00 --json
```

## Input Parameters

### Command Line Arguments

- **`date`** (required): Date to search for courts
  - Format: YYYY-MM-DD (e.g., `2025-06-20`)
  - Special keywords: `today`, `tomorrow`
  - Must be today or a future date
  
- **`time`** (required): Start time in 24-hour format
  - Format: HH:MM (e.g., `17:00`)
  - Valid range: 00:00 - 23:59

### Optional Flags

- **`--json`**: Output results in raw JSON format
- **`--limit N`**: Limit number of results shown (default: show all)
- **`--help`**: Show help message and usage examples

### Function Parameters

For programmatic usage: `search_pickleball_courts(date_iso, time_24h="17:00")`

- **`date_iso`** (required): Date in ISO format (YYYY-MM-DD)
- **`time_24h`** (optional): Time in 24-hour format, defaults to "17:00"

## Output Format

### Success Response

```json
{
  "search_params": {
    "date": "2025-06-20",
    "time": "17:00",
    "boroughs": "9,2,19,1,8"
  },
  "results": [
    {
      "name": "Pickleball - Terrain extérieur",
      "location": "Parc Jarry",
      "borough": "Villeray–Saint-Michel–Parc-Extension",
      "date": "2025-06-20",
      "start_time": "17:00",
      "end_time": "18:00",
      "price": "8.10",
      "currency": "CAD",
      "can_reserve": true,
      "reservation_id": "12345"
    }
  ],
  "total_found": 1,
  "status": "success",
  "message": "Found 1 available courts",
  "api_response_time": "0.5s"
}
```

### Error Response

```json
{
  "search_params": {
    "date": "2025-06-20",
    "time": "17:00",
    "boroughs": "9,2,19,1,8"
  },
  "results": [],
  "total_found": 0,
  "status": "error",
  "message": "Network connection error. Please check your internet connection.",
  "error_type": "network_error"
}
```

## Error Types

- **`invalid_input`**: Invalid date or time format
- **`network_error`**: Connection issues or timeouts
- **`api_error`**: API endpoint errors or invalid responses
- **`no_results`**: No courts found (still returns success status)

## Testing

Run the included test examples:

```bash
python test_example.py
```

## Montreal Boroughs Covered

The script searches across all Montreal boroughs:
- Ahuntsic-Cartierville (ID: 9)
- Ville-Marie (ID: 2) 
- Villeray–Saint-Michel–Parc-Extension (ID: 19)
- Le Plateau-Mont-Royal (ID: 1)
- Rosemont–La Petite-Patrie (ID: 8)

## Integration with AI Assistants

This script is designed to work seamlessly with AI assistants like Claude:

1. **Direct Fetch**: Claude can fetch the script from the raw GitHub URL
2. **Immediate Execution**: No complex setup required
3. **Structured Output**: Returns consistent JSON format
4. **Error Handling**: Comprehensive error messages for troubleshooting

### Example Claude Usage

**User**: "Search for pickleball courts in Montreal for tomorrow at 6 PM"

**Claude will**:
1. Fetch `pickleball_search.py` from this repository
2. Execute: `python pickleball_search.py tomorrow 18:00 --json`
3. Parse the JSON response and present results in a user-friendly format

**Alternative programmatic usage**:
```python
result = search_pickleball_courts("2025-06-21", "18:00")
# Process the result dictionary
```

## Requirements

- Python 3.6+
- `requests` library (automatically installed via requirements.txt)

## License

MIT License - feel free to use and modify as needed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions:
- Open an issue on GitHub
- Check the test examples for usage patterns
- Review the error messages for troubleshooting guidance
