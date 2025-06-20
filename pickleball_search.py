#!/usr/bin/env python3
"""
Montreal Pickleball Court Finder

This script searches for available pickleball courts in Montreal using
the official city API endpoint.
"""

import json
import logging
import re
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PickleballSearcher:
    """Montreal pickleball court search utility."""
    
    BASE_URL = "https://loisirs.montreal.ca/IC3/api/U6510/public/search/"
    REQUIRED_HEADERS = {
        "X-Tenant-Id": "1",
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0 (compatible; PickleballCourtFinder/1.0)"
    }
    DEFAULT_BOROUGHS = "9,2,19,1,8"  # All Montreal boroughs
    REQUEST_TIMEOUT = 30
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.REQUIRED_HEADERS)
    
    def _validate_date(self, date_iso: str) -> bool:
        """Validate ISO date format (YYYY-MM-DD)."""
        try:
            datetime.strptime(date_iso, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _validate_time(self, time_24h: str) -> bool:
        """Validate 24-hour time format (HH:MM)."""
        pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
        return bool(re.match(pattern, time_24h))
    
    def _format_api_date(self, date_iso: str) -> str:
        """Convert ISO date to API format with timezone."""
        return f"{date_iso}T00:00:00.000-04:00"
    
    def _parse_price(self, price_str: str) -> str:
        """Parse price string to standard decimal format."""
        if not price_str:
            return "0.00"
        
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[^\d,.]', '', str(price_str))
        
        # Handle French format (8,10) to English format (8.10)
        if ',' in cleaned and '.' not in cleaned:
            cleaned = cleaned.replace(',', '.')
        
        try:
            return f"{float(cleaned):.2f}"
        except (ValueError, TypeError):
            return "0.00"
    
    def _parse_time_range(self, time_str: str) -> tuple:
        """Parse time range string like '17:00 - 18:00'."""
        if not time_str or ' - ' not in time_str:
            return None, None
        
        try:
            start_time, end_time = time_str.split(' - ')
            return start_time.strip(), end_time.strip()
        except ValueError:
            return None, None
    
    def _build_request_payload(self, date_iso: str, time_24h: str) -> Dict:
        """Build the API request payload."""
        return {
            "limit": 20,
            "offset": 0,
            "sortColumn": "facility.name",
            "isSortOrderAsc": True,
            "searchString": "pickleball",
            "facilityTypeIds": None,
            "boroughIds": self.DEFAULT_BOROUGHS,
            "siteId": None,
            "dates": [self._format_api_date(date_iso)],
            "startTime": time_24h,
            "endTime": None
        }
    
    def _parse_api_response(self, response_data: Dict, date_iso: str) -> List[Dict]:
        """Parse API response and extract court information."""
        courts = []
        
        try:
            # The actual API response structure
            results = response_data.get('results', [])
            
            for item in results:
                # Extract facility information
                facility = item.get('facility', {})
                facility_name = facility.get('name', 'Unknown Court')
                
                # Extract site/location information
                site = facility.get('site', {})
                location_name = site.get('name', 'Unknown Location')
                
                # Extract borough information
                boroughs = site.get('boroughs', [])
                borough_name = boroughs[0].get('name', 'Unknown Borough') if boroughs else 'Unknown Borough'
                
                # Parse datetime strings
                start_datetime = item.get('startDateTime', '')
                end_datetime = item.get('endDateTime', '')
                
                # Extract time from ISO datetime
                start_time = 'Unknown'
                end_time = 'Unknown'
                if start_datetime:
                    try:
                        dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                        # Convert to Montreal time (UTC-4 in summer, UTC-5 in winter)
                        # For simplicity, using UTC-4 (EDT)
                        montreal_dt = dt.replace(tzinfo=None) - timedelta(hours=4)
                        start_time = montreal_dt.strftime('%H:%M')
                    except:
                        pass
                        
                if end_datetime:
                    try:
                        dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
                        montreal_dt = dt.replace(tzinfo=None) - timedelta(hours=4)
                        end_time = montreal_dt.strftime('%H:%M')
                    except:
                        pass
                
                # Extract price and reservation info
                total_price = item.get('totalPrice', 0)
                can_reserve_obj = item.get('canReserve', {})
                can_reserve = can_reserve_obj.get('value', True) if isinstance(can_reserve_obj, dict) else bool(can_reserve_obj)
                
                court_info = {
                    "name": facility_name,
                    "location": location_name,
                    "borough": borough_name,
                    "date": date_iso,
                    "start_time": start_time,
                    "end_time": end_time,
                    "price": f"{total_price:.2f}",
                    "currency": "CAD",
                    "can_reserve": can_reserve,
                    "reservation_id": item.get('facilityScheduleId', item.get('facilityPricingId', None))
                }
                
                courts.append(court_info)
                
        except Exception as e:
            logger.error(f"Error parsing API response: {e}")
            logger.error(f"Response data keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
        
        return courts
    
    def search_pickleball_courts(self, date_iso: str, time_24h: str = "17:00") -> Dict:
        """
        Search for available pickleball courts in Montreal.
        
        Args:
            date_iso (str): Date in ISO format (YYYY-MM-DD)
            time_24h (str): Time in 24-hour format (HH:MM)
            
        Returns:
            Dict: Structured response with search results
        """
        start_time = datetime.now()
        
        search_params = {
            "date": date_iso,
            "time": time_24h,
            "boroughs": self.DEFAULT_BOROUGHS
        }
        
        # Input validation
        if not self._validate_date(date_iso):
            return {
                "search_params": search_params,
                "results": [],
                "total_found": 0,
                "status": "error",
                "message": f"Invalid date format: {date_iso}. Expected YYYY-MM-DD",
                "error_type": "invalid_input"
            }
        
        if not self._validate_time(time_24h):
            return {
                "search_params": search_params,
                "results": [],
                "total_found": 0,
                "status": "error",
                "message": f"Invalid time format: {time_24h}. Expected HH:MM",
                "error_type": "invalid_input"
            }
        
        # Check if date is not in the past
        search_date = datetime.strptime(date_iso, "%Y-%m-%d").date()
        if search_date < datetime.now().date():
            return {
                "search_params": search_params,
                "results": [],
                "total_found": 0,
                "status": "error", 
                "message": f"Cannot search for past dates: {date_iso}",
                "error_type": "invalid_input"
            }
        
        try:
            # Build and send request
            payload = self._build_request_payload(date_iso, time_24h)
            logger.info(f"Searching courts for {date_iso} at {time_24h}")
            
            response = self.session.post(
                self.BASE_URL,
                json=payload,
                timeout=self.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            
            # Handle UTF-8 BOM in response
            response_text = response.text
            if response_text.startswith('\ufeff'):
                response_text = response_text[1:]
            
            response_data = json.loads(response_text)
            
            # Parse results
            courts = self._parse_api_response(response_data, date_iso)
            response_time = f"{(datetime.now() - start_time).total_seconds():.1f}s"
            
            if courts:
                return {
                    "search_params": search_params,
                    "results": courts,
                    "total_found": len(courts),
                    "status": "success",
                    "message": f"Found {len(courts)} available courts",
                    "api_response_time": response_time
                }
            else:
                return {
                    "search_params": search_params,
                    "results": [],
                    "total_found": 0,
                    "status": "success",
                    "message": "No available courts found for the specified date and time",
                    "api_response_time": response_time
                }
                
        except requests.exceptions.Timeout:
            return {
                "search_params": search_params,
                "results": [],
                "total_found": 0,
                "status": "error",
                "message": f"Request timeout after {self.REQUEST_TIMEOUT} seconds",
                "error_type": "network_error"
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "search_params": search_params,
                "results": [],
                "total_found": 0,
                "status": "error",
                "message": "Network connection error. Please check your internet connection.",
                "error_type": "network_error"
            }
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            return {
                "search_params": search_params,
                "results": [],
                "total_found": 0,
                "status": "error",
                "message": f"API request failed with status {status_code}",
                "error_type": "api_error"
            }
            
        except json.JSONDecodeError:
            return {
                "search_params": search_params,
                "results": [],
                "total_found": 0,
                "status": "error",
                "message": "Invalid API response format",
                "error_type": "api_error"
            }
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "search_params": search_params,
                "results": [],
                "total_found": 0,
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "error_type": "api_error"
            }


# Convenience function for direct usage
def search_pickleball_courts(date_iso: str, time_24h: str = "17:00") -> Dict:
    """
    Search for available pickleball courts in Montreal.
    
    Args:
        date_iso (str): Date in ISO format (YYYY-MM-DD)
        time_24h (str): Time in 24-hour format (HH:MM), defaults to "17:00"
        
    Returns:
        Dict: Structured response with search results
        
    Example:
        >>> result = search_pickleball_courts("2025-06-20", "17:00")
        >>> print(json.dumps(result, indent=2))
    """
    searcher = PickleballSearcher()
    return searcher.search_pickleball_courts(date_iso, time_24h)


def main():
    """Main function with command line argument parsing."""
    import argparse
    from datetime import date, timedelta
    
    parser = argparse.ArgumentParser(
        description="Search for available pickleball courts in Montreal",
        epilog="""
Examples:
  %(prog)s 2025-06-20 17:00    # Search for courts on June 20th at 5 PM
  %(prog)s 2025-06-21 09:30    # Search for courts on June 21st at 9:30 AM
  %(prog)s tomorrow 18:00      # Search for courts tomorrow at 6 PM
  %(prog)s today 12:00         # Search for courts today at noon
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "date",
        help="Date to search for courts (YYYY-MM-DD format, or 'today'/'tomorrow')"
    )
    
    parser.add_argument(
        "time",
        help="Start time in 24-hour format (HH:MM)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in raw JSON format"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of results shown (default: show all)"
    )
    
    args = parser.parse_args()
    
    # Handle special date keywords
    if args.date.lower() == "today":
        search_date = date.today().strftime("%Y-%m-%d")
    elif args.date.lower() == "tomorrow":
        search_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        search_date = args.date
    
    # Perform the search
    result = search_pickleball_courts(search_date, args.time)
    
    if args.json:
        # Raw JSON output
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Formatted output
        print("🏓 Montreal Pickleball Court Search")
        print("=" * 50)
        print(f"📅 Date: {result['search_params']['date']}")
        print(f"⏰ Time: {result['search_params']['time']}")
        print(f"📍 Boroughs: {result['search_params']['boroughs']}")
        
        if result['status'] == 'success':
            print(f"✅ Status: {result['message']}")
            print(f"⚡ Response time: {result['api_response_time']}")
            
            courts = result['results']
            if args.limit:
                courts = courts[:args.limit]
            
            if courts:
                print(f"\n🏟️  Available Courts ({len(courts)} shown):")
                print("-" * 50)
                
                for i, court in enumerate(courts, 1):
                    print(f"{i:2}. {court['name']}")
                    print(f"    📍 {court['location']} ({court['borough']})")
                    print(f"    ⏰ {court['start_time']} - {court['end_time']}")
                    print(f"    💰 ${court['price']} {court['currency']}")
                    print(f"    📅 Reservable: {'Yes' if court['can_reserve'] else 'No'}")
                    if court['reservation_id']:
                        print(f"    🆔 ID: {court['reservation_id']}")
                    print()
                
                if result['total_found'] > len(courts):
                    remaining = result['total_found'] - len(courts)
                    print(f"... and {remaining} more courts (use --limit to show more)")
            else:
                print(f"\n❌ No courts found for {search_date} at {args.time}")
        else:
            print(f"❌ Error: {result['message']}")
            if 'error_type' in result:
                print(f"   Type: {result['error_type']}")
            return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())