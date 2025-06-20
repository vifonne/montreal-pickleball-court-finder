#!/usr/bin/env python3
"""
Test examples for Montreal Pickleball Court Finder

This module contains test functions and usage examples for the pickleball_search module.
Run this file to see example usage and test different scenarios.
"""

import json
from datetime import date, timedelta
from pickleball_search import search_pickleball_courts, PickleballSearcher


def test_valid_search():
    """Test a valid search with proper date and time."""
    print("=== Test: Valid Search ===")
    
    # Search for courts tomorrow at 5 PM
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    result = search_pickleball_courts(tomorrow, "17:00")
    
    print(f"Search Date: {tomorrow}")
    print(f"Search Time: 17:00")
    print(f"Status: {result['status']}")
    print(f"Total Found: {result['total_found']}")
    print(f"Message: {result['message']}")
    
    if result['results']:
        print("\nFirst Court Found:")
        court = result['results'][0]
        print(f"  Name: {court['name']}")
        print(f"  Location: {court['location']}")
        print(f"  Borough: {court['borough']}")
        print(f"  Time: {court['start_time']} - {court['end_time']}")
        print(f"  Price: ${court['price']} {court['currency']}")
        print(f"  Can Reserve: {court['can_reserve']}")
    
    print("-" * 50)
    return result


def test_invalid_date_format():
    """Test error handling for invalid date format."""
    print("=== Test: Invalid Date Format ===")
    
    result = search_pickleball_courts("2025/06/20", "17:00")  # Wrong format
    
    print(f"Input Date: 2025/06/20 (invalid format)")
    print(f"Status: {result['status']}")
    print(f"Error Type: {result.get('error_type', 'N/A')}")
    print(f"Message: {result['message']}")
    print("-" * 50)
    return result


def test_invalid_time_format():
    """Test error handling for invalid time format."""
    print("=== Test: Invalid Time Format ===")
    
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    result = search_pickleball_courts(tomorrow, "25:00")  # Invalid hour
    
    print(f"Input Time: 25:00 (invalid format)")
    print(f"Status: {result['status']}")
    print(f"Error Type: {result.get('error_type', 'N/A')}")
    print(f"Message: {result['message']}")
    print("-" * 50)
    return result


def test_past_date():
    """Test error handling for past dates."""
    print("=== Test: Past Date ===")
    
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    result = search_pickleball_courts(yesterday, "17:00")
    
    print(f"Input Date: {yesterday} (past date)")
    print(f"Status: {result['status']}")
    print(f"Error Type: {result.get('error_type', 'N/A')}")
    print(f"Message: {result['message']}")
    print("-" * 50)
    return result


def test_different_times():
    """Test searches at different times of day."""
    print("=== Test: Different Times ===")
    
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    times = ["08:00", "12:00", "17:00", "20:00"]
    
    for time_slot in times:
        print(f"\nSearching for {time_slot}:")
        result = search_pickleball_courts(tomorrow, time_slot)
        print(f"  Status: {result['status']}")
        print(f"  Courts Found: {result['total_found']}")
        if result['status'] == 'error':
            print(f"  Error: {result['message']}")
    
    print("-" * 50)


def test_multiple_days():
    """Test searches across multiple days."""
    print("=== Test: Multiple Days ===")
    
    for i in range(1, 4):  # Next 3 days
        search_date = (date.today() + timedelta(days=i)).strftime("%Y-%m-%d")
        result = search_pickleball_courts(search_date, "17:00")
        
        print(f"\nDate: {search_date}")
        print(f"  Status: {result['status']}")
        print(f"  Courts Found: {result['total_found']}")
        if result['results']:
            locations = set(court['location'] for court in result['results'])
            print(f"  Unique Locations: {len(locations)}")
    
    print("-" * 50)


def test_price_parsing():
    """Test the price parsing functionality."""
    print("=== Test: Price Parsing ===")
    
    searcher = PickleballSearcher()
    
    test_prices = [
        "8,10 $",
        "8.10",
        "10,50 CAD",
        "15.75 $",
        "",
        None,
        "Free",
        "12,00"
    ]
    
    for price in test_prices:
        parsed = searcher._parse_price(price)
        print(f"  '{price}' -> '{parsed}'")
    
    print("-" * 50)


def test_time_range_parsing():
    """Test the time range parsing functionality."""
    print("=== Test: Time Range Parsing ===")
    
    searcher = PickleballSearcher()
    
    test_ranges = [
        "17:00 - 18:00",
        "09:30 - 10:30",
        "17:00",
        "",
        None,
        "Invalid range"
    ]
    
    for time_range in test_ranges:
        start, end = searcher._parse_time_range(time_range)
        print(f"  '{time_range}' -> start: '{start}', end: '{end}'")
    
    print("-" * 50)


def demo_usage():
    """Demonstrate typical usage scenarios."""
    print("=== Demo: Typical Usage Scenarios ===")
    
    # Scenario 1: Looking for courts this weekend
    weekend_date = (date.today() + timedelta(days=(5 - date.today().weekday()) % 7)).strftime("%Y-%m-%d")
    
    print(f"\n1. Weekend Search ({weekend_date} at 10:00 AM):")
    result = search_pickleball_courts(weekend_date, "10:00")
    print_summary(result)
    
    # Scenario 2: Evening search
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"\n2. Evening Search ({tomorrow} at 7:00 PM):")
    result = search_pickleball_courts(tomorrow, "19:00")
    print_summary(result)
    
    # Scenario 3: Early morning search
    print(f"\n3. Early Morning Search ({tomorrow} at 7:00 AM):")
    result = search_pickleball_courts(tomorrow, "07:00")
    print_summary(result)
    
    print("-" * 50)


def print_summary(result):
    """Print a summary of search results."""
    if result['status'] == 'success':
        print(f"  ✅ Found {result['total_found']} courts")
        if result['results']:
            boroughs = set(court['borough'] for court in result['results'])
            prices = [float(court['price']) for court in result['results'] if court['price'] != '0.00']
            print(f"  📍 Boroughs: {len(boroughs)}")
            if prices:
                print(f"  💰 Price range: ${min(prices):.2f} - ${max(prices):.2f} CAD")
    else:
        print(f"  ❌ Error: {result['message']}")


def run_all_tests():
    """Run all test functions."""
    print("🏓 Montreal Pickleball Court Finder - Test Suite")
    print("=" * 60)
    
    # Run individual tests
    test_valid_search()
    test_invalid_date_format()
    test_invalid_time_format()
    test_past_date()
    test_different_times()
    test_multiple_days()
    test_price_parsing()
    test_time_range_parsing()
    demo_usage()
    
    print("✅ All tests completed!")
    print("\nTo run a specific test, call the individual test functions:")
    print("  test_valid_search()")
    print("  test_invalid_date_format()")
    print("  demo_usage()")


def interactive_search():
    """Interactive search function for manual testing."""
    print("🏓 Interactive Pickleball Court Search")
    print("=" * 40)
    
    while True:
        try:
            # Get user input
            date_input = input("\nEnter date (YYYY-MM-DD) or 'quit': ").strip()
            if date_input.lower() == 'quit':
                break
            
            time_input = input("Enter time (HH:MM) [default: 17:00]: ").strip()
            if not time_input:
                time_input = "17:00"
                
            # Perform search
            print(f"\n🔍 Searching for courts on {date_input} at {time_input}...")
            result = search_pickleball_courts(date_input, time_input)
            
            # Display results
            print(f"\nStatus: {result['status']}")
            if result['status'] == 'success':
                print(f"Courts found: {result['total_found']}")
                print(f"Response time: {result['api_response_time']}")
                
                for i, court in enumerate(result['results'][:5], 1):  # Show first 5
                    print(f"\n{i}. {court['name']}")
                    print(f"   📍 {court['location']} ({court['borough']})")
                    print(f"   ⏰ {court['start_time']} - {court['end_time']}")
                    print(f"   💰 ${court['price']} {court['currency']}")
                    print(f"   📅 Reservable: {'Yes' if court['can_reserve'] else 'No'}")
                
                if len(result['results']) > 5:
                    print(f"\n... and {len(result['results']) - 5} more courts")
            else:
                print(f"Error: {result['message']}")
                if 'error_type' in result:
                    print(f"Error type: {result['error_type']}")
                    
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_search()
    else:
        run_all_tests()