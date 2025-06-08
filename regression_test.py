import requests
import json
import time
from datetime import datetime, timedelta

# Backend URL from the frontend .env file
BACKEND_URL = "https://cf2530ec-d455-4e05-aef3-ef00e108bc21.preview.emergentagent.com/api"

# Test results
test_results = {
    # Authentication tests
    "login_admin": False,
    
    # Dashboard tests
    "dashboard_clubly_founder": False,
    
    # Event tests
    "events_api": False,
    
    # Organization tests
    "organizations_api": False
}

# Store tokens for different user roles
tokens = {
    "admin": None
}

# Test login with admin
def test_login_admin():
    print("\n=== Testing login with admin (clubly_founder) ===")
    
    payload = {
        "login": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["admin"] = data.get("token")
        print(f"✅ Login successful with admin. User role: {data['user']['ruolo']}")
        test_results["login_admin"] = True
    else:
        print(f"❌ Login failed with admin. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["login_admin"]

# Test clubly founder dashboard API
def test_dashboard_clubly_founder():
    print("\n=== Testing clubly founder dashboard API ===")
    
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test clubly founder dashboard without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/dashboard/clubly-founder", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Clubly founder dashboard API successful")
        print(f"   Organizations: {len(data.get('organizations', []))}")
        print(f"   Events: {len(data.get('events', []))}")
        print(f"   Capo promoters: {len(data.get('users', {}).get('capo_promoter', []))}")
        print(f"   Promoters: {len(data.get('users', {}).get('promoter', []))}")
        test_results["dashboard_clubly_founder"] = True
    else:
        print(f"❌ Clubly founder dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_clubly_founder"]

# Test events API
def test_events_api():
    print("\n=== Testing events API ===")
    
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test events API without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Test 1: Get all events
    print("Test 1: Get all events")
    response = requests.get(f"{BACKEND_URL}/events", headers=headers)
    
    if response.status_code == 200:
        events = response.json()
        print(f"✅ Get events successful. Events count: {len(events)}")
        get_events_success = len(events) > 0
        
        if get_events_success and len(events) > 0:
            # Test 2: Get specific event
            event_id = events[0]["id"]
            print(f"Test 2: Get specific event (ID: {event_id})")
            
            response = requests.get(f"{BACKEND_URL}/events/{event_id}", headers=headers)
            
            if response.status_code == 200:
                event = response.json()
                print(f"✅ Get specific event successful. Event name: {event.get('name')}")
                get_specific_event_success = True
            else:
                print(f"❌ Get specific event failed. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                get_specific_event_success = False
        else:
            get_specific_event_success = False
    else:
        print(f"❌ Get events failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        get_events_success = False
        get_specific_event_success = False
    
    # Test 3: Create a new event
    print("Test 3: Create a new event")
    
    # Get tomorrow's date
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    event_payload = {
        "name": f"Regression Test Event {int(time.time())}",
        "date": tomorrow,
        "start_time": "22:00",
        "location": "Test Club, Milano",
        "organization": "Night Events Milano",
        "end_time": "04:00",
        "lineup": ["DJ Test", "DJ Sample"],
        "guests": ["VIP Guest"],
        "total_tables": 10,
        "tables_available": 10,
        "max_party_size": 8
    }
    
    response = requests.post(f"{BACKEND_URL}/events", json=event_payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Create event successful. Event ID: {data.get('event_id')}")
        create_event_success = True
    else:
        print(f"❌ Create event failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        create_event_success = False
    
    # Overall success if all tests passed
    test_results["events_api"] = get_events_success and get_specific_event_success and create_event_success
    
    return test_results["events_api"]

# Test organizations API
def test_organizations_api():
    print("\n=== Testing organizations API ===")
    
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test organizations API without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Test 1: Get all organizations
    print("Test 1: Get all organizations")
    response = requests.get(f"{BACKEND_URL}/organizations", headers=headers)
    
    if response.status_code == 200:
        organizations = response.json()
        print(f"✅ Get organizations successful. Organizations count: {len(organizations)}")
        get_orgs_success = len(organizations) > 0
        
        if get_orgs_success and len(organizations) > 0:
            # Test 2: Get specific organization
            org_id = organizations[0]["id"]
            print(f"Test 2: Get specific organization (ID: {org_id})")
            
            response = requests.get(f"{BACKEND_URL}/organizations/{org_id}", headers=headers)
            
            if response.status_code == 200:
                org = response.json()
                print(f"✅ Get specific organization successful. Organization name: {org.get('name')}")
                get_specific_org_success = True
            else:
                print(f"❌ Get specific organization failed. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                get_specific_org_success = False
        else:
            get_specific_org_success = False
    else:
        print(f"❌ Get organizations failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        get_orgs_success = False
        get_specific_org_success = False
    
    # Overall success if both tests passed
    test_results["organizations_api"] = get_orgs_success and get_specific_org_success
    
    return test_results["organizations_api"]

# Run all tests
def run_regression_tests():
    print("\n=== Running regression tests for Clubly backend ===\n")
    
    # Authentication tests
    test_login_admin()
    
    # Dashboard tests
    test_dashboard_clubly_founder()
    
    # Event tests
    test_events_api()
    
    # Organization tests
    test_organizations_api()
    
    # Print summary
    print("\n=== Regression Test Results Summary ===")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Calculate overall success rate
    success_count = sum(1 for result in test_results.values() if result)
    total_count = len(test_results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\nOverall success rate: {success_rate:.2f}% ({success_count}/{total_count} tests passed)")

if __name__ == "__main__":
    run_regression_tests()
