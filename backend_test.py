import requests
import json
import base64
import os
import time
import random
import string
from datetime import datetime, timedelta

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://86371f8e-929c-484d-b4db-cf725ee6a471.preview.emergentagent.com/api"

# Test results
test_results = {
    "login_username": False,
    "login_email": False,
    "login_capo_promoter": False,
    "register_with_profile_photo": False,
    "dashboard_promoter": False,
    "dashboard_capo_promoter": False,
    "dashboard_clubly_founder": False,
    "get_organizations": False,
    "create_organization": False,
    "create_temporary_credentials": False,
    "complete_user_setup": False,
    # New API tests
    "user_profile_viewing": False,
    "user_search": False,
    "event_creation_by_promoter": False,
    "organization_details": False,
    # Capo promoter event update tests
    "capo_promoter_event_update_allowed_fields": False,
    "capo_promoter_event_update_restricted_fields": False,
    "promoter_event_update_authorization": False
}

# Store tokens for different user roles
tokens = {
    "admin": None,
    "capo_promoter": None,
    "promoter": None,
    "new_user": None,
    "temp_user": None
}

# Helper function to generate a random string
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Helper function to create a fake base64 image
def create_fake_base64_image():
    # This is a tiny 1x1 transparent PNG image
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

# Test login with username
def test_login_with_username():
    print("\n=== Testing login with username ===")
    
    payload = {
        "login": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["admin"] = data.get("token")
        print(f"✅ Login successful with username. User role: {data['user']['ruolo']}")
        test_results["login_username"] = True
    else:
        print(f"❌ Login failed with username. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["login_username"]

# Test login with email
def test_login_with_email():
    print("\n=== Testing login with email ===")
    
    payload = {
        "login": "admin@clubly.it",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["admin"] = data.get("token")
        print(f"✅ Login successful with email. User role: {data['user']['ruolo']}")
        test_results["login_email"] = True
    else:
        print(f"❌ Login failed with email. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["login_email"]

# Test login with capo promoter
def test_login_with_capo_promoter():
    print("\n=== Testing login with capo promoter ===")
    
    payload = {
        "login": "capo_milano",
        "password": "Password1"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["capo_promoter"] = data.get("token")
        print(f"✅ Login successful with capo promoter. User role: {data['user']['ruolo']}")
        test_results["login_capo_promoter"] = True
    else:
        print(f"❌ Login failed with capo promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["login_capo_promoter"]

# Test registration with profile photo
def test_register_with_profile_photo():
    print("\n=== Testing registration with profile photo ===")
    
    # Generate random user data
    username = f"test_user_{random_string()}"
    email = f"{username}@test.com"
    
    payload = {
        "nome": "Test",
        "cognome": "User",
        "email": email,
        "username": username,
        "password": "TestPassword123",
        "data_nascita": "1990-01-01",
        "citta": "Test City",
        "ruolo": "cliente",
        "profile_image": create_fake_base64_image()
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["new_user"] = data.get("token")
        print(f"✅ Registration successful with profile photo. User: {username}")
        test_results["register_with_profile_photo"] = True
    else:
        print(f"❌ Registration failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["register_with_profile_photo"]

# Test promoter dashboard API
def test_promoter_dashboard():
    print("\n=== Testing promoter dashboard API ===")
    
    # First, we need to login as a promoter or capo_promoter
    if not tokens["capo_promoter"]:
        test_login_with_capo_promoter()
    
    if not tokens["capo_promoter"]:
        print("❌ Cannot test promoter dashboard without capo_promoter token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/dashboard/promoter", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Promoter dashboard API successful. Organization: {data.get('organization')}")
        test_results["dashboard_promoter"] = True
    else:
        print(f"❌ Promoter dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_promoter"]

# Test capo promoter dashboard API
def test_capo_promoter_dashboard():
    print("\n=== Testing capo promoter dashboard API ===")
    
    # First, we need to login as a capo_promoter
    if not tokens["capo_promoter"]:
        test_login_with_capo_promoter()
    
    if not tokens["capo_promoter"]:
        print("❌ Cannot test capo promoter dashboard without capo_promoter token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/dashboard/capo-promoter", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Capo promoter dashboard API successful. Can create promoters: {data.get('can_create_promoters')}")
        test_results["dashboard_capo_promoter"] = True
    else:
        print(f"❌ Capo promoter dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_capo_promoter"]

# Test clubly founder dashboard API
def test_clubly_founder_dashboard():
    print("\n=== Testing clubly founder dashboard API ===")
    
    # First, we need to login as admin (clubly_founder)
    if not tokens["admin"]:
        test_login_with_username()
    
    if not tokens["admin"]:
        print("❌ Cannot test clubly founder dashboard without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/dashboard/clubly-founder", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Clubly founder dashboard API successful. Organizations count: {len(data.get('organizations', []))}")
        test_results["dashboard_clubly_founder"] = True
    else:
        print(f"❌ Clubly founder dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_clubly_founder"]

# Test get organizations API
def test_get_organizations():
    print("\n=== Testing get organizations API ===")
    
    response = requests.get(f"{BACKEND_URL}/organizations")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Get organizations API successful. Organizations count: {len(data)}")
        test_results["get_organizations"] = True
    else:
        print(f"❌ Get organizations API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["get_organizations"]

# Test create organization API
def test_create_organization():
    print("\n=== Testing create organization API ===")
    
    # First, we need to login as admin (clubly_founder)
    if not tokens["admin"]:
        test_login_with_username()
    
    if not tokens["admin"]:
        print("❌ Cannot test create organization without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Generate a random organization name
    org_name = f"Test Organization {random_string()}"
    
    payload = {
        "name": org_name,
        "location": "Test Location",
        "capo_promoter_username": "capo_milano"
    }
    
    response = requests.post(f"{BACKEND_URL}/organizations", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Create organization API successful. Organization ID: {data.get('organization_id')}")
        test_results["create_organization"] = True
    else:
        print(f"❌ Create organization API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["create_organization"]

# Test create temporary credentials API
def test_create_temporary_credentials():
    print("\n=== Testing create temporary credentials API ===")
    
    # First, we need to login as admin (clubly_founder)
    if not tokens["admin"]:
        test_login_with_username()
    
    if not tokens["admin"]:
        print("❌ Cannot test create temporary credentials without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Generate random user data
    temp_email = f"temp_user_{random_string()}@test.com"
    
    payload = {
        "nome": "Temporary",
        "email": temp_email,
        "password": "TempPassword123",
        "ruolo": "promoter",
        "organization": "Night Events Milano"
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Create temporary credentials API successful. User ID: {data.get('user_id')}")
        
        # Now login with the temporary credentials
        login_payload = {
            "login": temp_email,
            "password": "TempPassword123"
        }
        
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            tokens["temp_user"] = login_data.get("token")
            print(f"✅ Login with temporary credentials successful")
            test_results["create_temporary_credentials"] = True
        else:
            print(f"❌ Login with temporary credentials failed. Status code: {login_response.status_code}")
            print(f"Response: {login_response.text}")
    else:
        print(f"❌ Create temporary credentials API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["create_temporary_credentials"]

# Test complete user setup API
def test_complete_user_setup():
    print("\n=== Testing complete user setup API ===")
    
    # First, we need to have a temporary user token
    if not tokens["temp_user"]:
        test_create_temporary_credentials()
    
    if not tokens["temp_user"]:
        print("❌ Cannot test complete user setup without temporary user token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['temp_user']}"
    }
    
    # Generate random username
    username = f"setup_user_{random_string()}"
    
    payload = {
        "cognome": "Setup User",
        "username": username,
        "data_nascita": "1995-05-05",
        "citta": "Setup City",
        "profile_image": create_fake_base64_image()
    }
    
    response = requests.post(f"{BACKEND_URL}/user/setup", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Complete user setup API successful. Username: {data['user']['username']}")
        test_results["complete_user_setup"] = True
    else:
        print(f"❌ Complete user setup API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["complete_user_setup"]

# Test user profile viewing API
def test_user_profile_viewing():
    print("\n=== Testing user profile viewing API ===")
    
    # First, we need to login as admin
    if not tokens["admin"]:
        test_login_with_username()
    
    if not tokens["admin"]:
        print("❌ Cannot test user profile viewing without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Get a user ID to view (we'll use the admin's ID from the token)
    import jwt
    token_data = jwt.decode(tokens["admin"], options={"verify_signature": False})
    user_id = token_data.get("id")
    
    if not user_id:
        print("❌ Could not extract user ID from token")
        return False
    
    response = requests.get(f"{BACKEND_URL}/users/{user_id}/profile", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User profile viewing API successful. Username: {data.get('username')}")
        print(f"   Biography: {data.get('biografia')}")
        test_results["user_profile_viewing"] = True
    else:
        print(f"❌ User profile viewing API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["user_profile_viewing"]

# Test user search API
def test_user_search():
    print("\n=== Testing user search API ===")
    
    # First, we need to login as admin
    if not tokens["admin"]:
        test_login_with_username()
    
    if not tokens["admin"]:
        print("❌ Cannot test user search without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Test 1: Search by name
    print("Test 1: Search by name")
    payload = {
        "search_term": "admin"
    }
    
    response = requests.post(f"{BACKEND_URL}/users/search", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User search by name successful. Results: {len(data)}")
        name_search_success = len(data) > 0
    else:
        print(f"❌ User search by name failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        name_search_success = False
    
    # Test 2: Search by role
    print("Test 2: Search by role")
    payload = {
        "role_filter": "promoter"
    }
    
    response = requests.post(f"{BACKEND_URL}/users/search", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User search by role successful. Results: {len(data)}")
        role_search_success = len(data) > 0
    else:
        print(f"❌ User search by role failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        role_search_success = False
    
    # Test 3: Search by date range
    print("Test 3: Search by date range")
    # Set date range to include all users (past to future)
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
    tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
    
    payload = {
        "creation_date_from": yesterday,
        "creation_date_to": tomorrow
    }
    
    response = requests.post(f"{BACKEND_URL}/users/search", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User search by date range successful. Results: {len(data)}")
        date_search_success = len(data) > 0
    else:
        print(f"❌ User search by date range failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        date_search_success = False
    
    # Overall success if at least two of the three tests passed
    test_results["user_search"] = (name_search_success + role_search_success + date_search_success) >= 2
    
    return test_results["user_search"]

# Test event creation by promoter API
def test_event_creation_by_promoter():
    print("\n=== Testing event creation by promoter API ===")
    
    # First, we need to login as capo_promoter
    if not tokens["capo_promoter"]:
        test_login_with_capo_promoter()
    
    if not tokens["capo_promoter"]:
        print("❌ Cannot test event creation without capo_promoter token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    # Generate a random event name
    event_name = f"Test Event {random_string()}"
    
    # Get tomorrow's date
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    payload = {
        "name": event_name,
        "date": tomorrow,
        "start_time": "22:00",
        "location": "Test Club, Milano",
        "end_time": "04:00",
        "lineup": ["DJ Test", "DJ Sample"],
        "location_address": "Via Test 123, Milano",
        "total_tables": 10,
        "table_types": ["Standard", "VIP"],
        "max_party_size": 8
    }
    
    response = requests.post(f"{BACKEND_URL}/events/create-by-promoter", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Event creation by promoter API successful. Event ID: {data.get('event_id')}")
        test_results["event_creation_by_promoter"] = True
    else:
        print(f"❌ Event creation by promoter API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["event_creation_by_promoter"]

# Test organization details API
def test_organization_details():
    print("\n=== Testing organization details API ===")
    
    # First, we need to login as admin
    if not tokens["admin"]:
        test_login_with_username()
    
    if not tokens["admin"]:
        print("❌ Cannot test organization details without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # First, get all organizations to find an ID
    response = requests.get(f"{BACKEND_URL}/organizations", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not get organizations list. Status code: {response.status_code}")
        return False
    
    organizations = response.json()
    
    if not organizations:
        print("❌ No organizations found")
        return False
    
    # Use the first organization's ID
    org_id = organizations[0]["id"]
    
    # Now get the details for this organization
    response = requests.get(f"{BACKEND_URL}/organizations/{org_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Organization details API successful. Organization: {data.get('name')}")
        
        # Check if members and events are included
        has_members = "members" in data and isinstance(data["members"], list)
        has_events = "events" in data and isinstance(data["events"], list)
        
        print(f"   Members included: {'Yes' if has_members else 'No'}")
        print(f"   Events included: {'Yes' if has_events else 'No'}")
        
        test_results["organization_details"] = has_members and has_events
    else:
        print(f"❌ Organization details API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["organization_details"]

# Test capo promoter event update API - allowed fields
def test_capo_promoter_event_update_allowed_fields():
    print("\n=== Testing capo promoter event update API - allowed fields ===")
    
    # First, we need to login as capo_promoter
    if not tokens["capo_promoter"]:
        test_login_with_capo_promoter()
    
    if not tokens["capo_promoter"]:
        print("❌ Cannot test event update without capo_promoter token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    # Get capo promoter's organization
    response = requests.get(f"{BACKEND_URL}/dashboard/capo-promoter", headers=headers)
    if response.status_code != 200:
        print(f"❌ Could not get capo promoter dashboard. Status code: {response.status_code}")
        return False
    
    dashboard_data = response.json()
    organization = dashboard_data.get("organization")
    
    # Get events for this organization
    response = requests.get(f"{BACKEND_URL}/organizations/{organization}/events", headers=headers)
    if response.status_code != 200:
        print(f"❌ Could not get organization events. Status code: {response.status_code}")
        return False
    
    events = response.json()
    
    if not events:
        # If no events exist, create one
        print("No events found for this organization. Creating a test event...")
        test_event_creation_by_promoter()
        
        # Try to get events again
        response = requests.get(f"{BACKEND_URL}/organizations/{organization}/events", headers=headers)
        if response.status_code != 200 or not response.json():
            print("❌ Could not create or find any events for testing")
            return False
        
        events = response.json()
    
    # Use the first event for testing
    event_id = events[0]["id"]
    original_name = events[0]["name"]
    
    # Update allowed fields: name, lineup, start_time
    updated_name = f"{original_name} - Updated {random_string(4)}"
    updated_lineup = ["DJ Test Updated", "DJ Sample Updated"]
    updated_start_time = "23:30"
    
    payload = {
        "name": updated_name,
        "lineup": updated_lineup,
        "start_time": updated_start_time
    }
    
    response = requests.put(f"{BACKEND_URL}/events/{event_id}", json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Event update with allowed fields successful")
        
        # Verify the update by getting the event details
        response = requests.get(f"{BACKEND_URL}/events/{event_id}", headers=headers)
        if response.status_code == 200:
            updated_event = response.json()
            
            name_updated = updated_event["name"] == updated_name
            lineup_updated = updated_event["lineup"] == updated_lineup
            start_time_updated = updated_event["start_time"] == updated_start_time
            
            print(f"   Name updated: {'Yes' if name_updated else 'No'}")
            print(f"   Lineup updated: {'Yes' if lineup_updated else 'No'}")
            print(f"   Start time updated: {'Yes' if start_time_updated else 'No'}")
            
            test_results["capo_promoter_event_update_allowed_fields"] = name_updated and lineup_updated and start_time_updated
        else:
            print(f"❌ Could not verify event update. Status code: {response.status_code}")
    else:
        print(f"❌ Event update with allowed fields failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["capo_promoter_event_update_allowed_fields"]

# Test capo promoter event update API - restricted fields
def test_capo_promoter_event_update_restricted_fields():
    print("\n=== Testing capo promoter event update API - restricted fields ===")
    
    # First, we need to login as capo_promoter
    if not tokens["capo_promoter"]:
        test_login_with_capo_promoter()
    
    if not tokens["capo_promoter"]:
        print("❌ Cannot test event update without capo_promoter token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    # Get capo promoter's organization
    response = requests.get(f"{BACKEND_URL}/dashboard/capo-promoter", headers=headers)
    if response.status_code != 200:
        print(f"❌ Could not get capo promoter dashboard. Status code: {response.status_code}")
        return False
    
    dashboard_data = response.json()
    organization = dashboard_data.get("organization")
    
    # Get events for this organization
    response = requests.get(f"{BACKEND_URL}/organizations/{organization}/events", headers=headers)
    if response.status_code != 200:
        print(f"❌ Could not get organization events. Status code: {response.status_code}")
        return False
    
    events = response.json()
    
    if not events:
        print("❌ No events found for testing")
        return False
    
    # Use the first event for testing
    event_id = events[0]["id"]
    original_location = events[0]["location"]
    original_date = events[0]["date"]
    
    # Try to update restricted fields: location, date
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    payload = {
        "location": "New Test Location",
        "date": tomorrow
    }
    
    response = requests.put(f"{BACKEND_URL}/events/{event_id}", json=payload, headers=headers)
    
    # The update should succeed but the restricted fields should be ignored
    if response.status_code == 200:
        print(f"✅ Event update API call successful")
        
        # Verify the update by getting the event details
        response = requests.get(f"{BACKEND_URL}/events/{event_id}", headers=headers)
        if response.status_code == 200:
            updated_event = response.json()
            
            location_unchanged = updated_event["location"] == original_location
            date_unchanged = updated_event["date"] == original_date
            
            print(f"   Location unchanged: {'Yes' if location_unchanged else 'No'}")
            print(f"   Date unchanged: {'Yes' if date_unchanged else 'No'}")
            
            test_results["capo_promoter_event_update_restricted_fields"] = location_unchanged and date_unchanged
        else:
            print(f"❌ Could not verify event update. Status code: {response.status_code}")
    else:
        print(f"❌ Event update API call failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["capo_promoter_event_update_restricted_fields"]

# Test promoter event update authorization
def test_promoter_event_update_authorization():
    print("\n=== Testing promoter event update authorization ===")
    
    # First, we need to create a promoter account or use an existing one
    # For simplicity, we'll create a temporary promoter
    if not tokens["admin"]:
        test_login_with_username()
    
    if not tokens["admin"]:
        print("❌ Cannot create promoter without admin token")
        return False
    
    admin_headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Create temporary promoter
    temp_email = f"temp_promoter_{random_string()}@test.com"
    temp_password = "TempPassword123"
    
    payload = {
        "nome": "Temporary",
        "email": temp_email,
        "password": temp_password,
        "ruolo": "promoter",
        "organization": "Night Events Milano"
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=admin_headers)
    
    if response.status_code != 200:
        print(f"❌ Could not create temporary promoter. Status code: {response.status_code}")
        return False
    
    # Login as the temporary promoter
    login_payload = {
        "login": temp_email,
        "password": temp_password
    }
    
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
    
    if login_response.status_code != 200:
        print(f"❌ Could not login as temporary promoter. Status code: {login_response.status_code}")
        return False
    
    promoter_token = login_response.json().get("token")
    promoter_headers = {
        "Authorization": f"Bearer {promoter_token}"
    }
    
    # Get events
    response = requests.get(f"{BACKEND_URL}/events", headers=promoter_headers)
    if response.status_code != 200 or not response.json():
        print(f"❌ Could not get events. Status code: {response.status_code}")
        return False
    
    events = response.json()
    event_id = events[0]["id"]
    
    # Try to update an event as a promoter (should fail)
    payload = {
        "name": f"Test Update by Promoter {random_string(4)}"
    }
    
    response = requests.put(f"{BACKEND_URL}/events/{event_id}", json=payload, headers=promoter_headers)
    
    # The update should fail with 403 Forbidden
    if response.status_code == 403:
        print(f"✅ Promoter correctly denied access to update events (403 Forbidden)")
        test_results["promoter_event_update_authorization"] = True
    else:
        print(f"❌ Promoter authorization test failed. Expected 403, got: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["promoter_event_update_authorization"]

# Run all tests
def run_all_tests():
    print("\n=== Running all backend API tests ===\n")
    
    # Authentication tests
    test_login_with_username()
    test_login_with_email()
    test_login_with_capo_promoter()
    test_register_with_profile_photo()
    
    # Dashboard tests
    test_promoter_dashboard()
    test_capo_promoter_dashboard()
    test_clubly_founder_dashboard()
    
    # Organization tests
    test_get_organizations()
    test_create_organization()
    
    # Temporary credentials and setup tests
    test_create_temporary_credentials()
    test_complete_user_setup()
    
    # New API tests
    test_user_profile_viewing()
    test_user_search()
    test_event_creation_by_promoter()
    test_organization_details()
    
    # Capo promoter event update tests
    test_capo_promoter_event_update_allowed_fields()
    test_capo_promoter_event_update_restricted_fields()
    test_promoter_event_update_authorization()
    
    # Print summary
    print("\n=== Test Results Summary ===")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Calculate overall success rate
    success_count = sum(1 for result in test_results.values() if result)
    total_count = len(test_results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\nOverall success rate: {success_rate:.2f}% ({success_count}/{total_count} tests passed)")

# Run specific tests for the new APIs
def run_new_api_tests():
    print("\n=== Running tests for new APIs ===\n")
    
    # Authentication first
    test_login_with_username()
    test_login_with_capo_promoter()
    
    # New API tests
    test_user_profile_viewing()
    test_user_search()
    test_event_creation_by_promoter()
    test_organization_details()
    
    # Capo promoter event update tests
    test_capo_promoter_event_update_allowed_fields()
    test_capo_promoter_event_update_restricted_fields()
    test_promoter_event_update_authorization()
    
    # Print summary
    print("\n=== New API Tests Summary ===")
    new_tests = [
        "user_profile_viewing", 
        "user_search", 
        "event_creation_by_promoter", 
        "organization_details",
        "capo_promoter_event_update_allowed_fields",
        "capo_promoter_event_update_restricted_fields",
        "promoter_event_update_authorization"
    ]
    for test_name in new_tests:
        status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Calculate success rate for new tests
    success_count = sum(1 for test_name in new_tests if test_results[test_name])
    total_count = len(new_tests)
    success_rate = (success_count / total_count) * 100
    
    print(f"\nNew API tests success rate: {success_rate:.2f}% ({success_count}/{total_count} tests passed)")

# Test login API for profile_image field
def test_login_for_profile_image():
    print("\n=== Testing login API for profile_image field ===")
    
    payload = {
        "login": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["admin"] = data.get("token")
        
        # Check if profile_image field is present in the response
        if "profile_image" in data["user"]:
            print(f"✅ Login response includes profile_image field")
            print(f"   Profile image: {data['user']['profile_image']}")
            test_results["login_for_profile_image"] = True
        else:
            print(f"❌ Login response does not include profile_image field")
            test_results["login_for_profile_image"] = False
    else:
        print(f"❌ Login failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["login_for_profile_image"] = False
    
    return test_results["login_for_profile_image"]

# Test chat management APIs
def test_chat_management():
    print("\n=== Testing chat management APIs ===")
    
    # First, we need to login as admin
    if not tokens["admin"]:
        test_login_with_username()
    
    if not tokens["admin"]:
        print("❌ Cannot test chat management without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Test 1: Get user chats
    print("Test 1: Get user chats")
    response = requests.get(f"{BACKEND_URL}/user/chats", headers=headers)
    
    if response.status_code == 200:
        chats = response.json()
        print(f"✅ Get user chats successful. Chats count: {len(chats)}")
        get_chats_success = True
        
        # If there are chats, test getting messages for the first chat
        if chats:
            chat_id = chats[0]["id"]
            
            # Test 2: Get chat messages
            print("Test 2: Get chat messages")
            response = requests.get(f"{BACKEND_URL}/chats/{chat_id}/messages", headers=headers)
            
            if response.status_code == 200:
                messages = response.json()
                print(f"✅ Get chat messages successful. Messages count: {len(messages)}")
                get_messages_success = True
                
                # Test 3: Send a message
                print("Test 3: Send a message")
                message_payload = {
                    "chat_id": chat_id,
                    "sender_id": "",  # Will be filled from token
                    "sender_role": "",  # Will be filled from token
                    "message": f"Test message {random_string()}"
                }
                
                response = requests.post(f"{BACKEND_URL}/chats/{chat_id}/messages", json=message_payload, headers=headers)
                
                if response.status_code == 200:
                    print(f"✅ Send message successful")
                    send_message_success = True
                else:
                    print(f"❌ Send message failed. Status code: {response.status_code}")
                    print(f"Response: {response.text}")
                    send_message_success = False
            else:
                print(f"❌ Get chat messages failed. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                get_messages_success = False
                send_message_success = False
        else:
            print("ℹ️ No chats found to test messages")
            get_messages_success = True  # Skip this test
            send_message_success = True  # Skip this test
    else:
        print(f"❌ Get user chats failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        get_chats_success = False
        get_messages_success = False
        send_message_success = False
    
    # Overall success if all tests passed
    test_results["chat_management"] = get_chats_success and get_messages_success and send_message_success
    
    return test_results["chat_management"]

if __name__ == "__main__":
    # Add the new tests to the test_results dictionary
    test_results["login_for_profile_image"] = False
    test_results["chat_management"] = False
    
    print("\n=== Running regression tests for key APIs ===\n")
    
    # Test login with profile_image
    test_login_for_profile_image()
    
    # Test user profile viewing
    test_user_profile_viewing()
    
    # Test event creation APIs
    test_login_with_username()  # Login as clubly_founder for /api/events
    
    # Test event creation by clubly_founder
    print("\n=== Testing event creation by clubly_founder API ===")
    if tokens["admin"]:
        headers = {
            "Authorization": f"Bearer {tokens['admin']}"
        }
        
        # Generate a random event name
        event_name = f"Founder Event {random_string()}"
        
        # Get tomorrow's date
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        payload = {
            "name": event_name,
            "date": tomorrow,
            "start_time": "21:00",
            "location": "Founder Club, Milano",
            "organization": "Night Events Milano",
            "end_time": "05:00",
            "lineup": ["DJ Founder", "DJ VIP"],
            "guests": ["Special Guest"],
            "total_tables": 15,
            "tables_available": 15,
            "max_party_size": 10
        }
        
        response = requests.post(f"{BACKEND_URL}/events", json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Event creation by clubly_founder API successful. Event ID: {data.get('event_id')}")
            test_results["event_creation_by_clubly_founder"] = True
        else:
            print(f"❌ Event creation by clubly_founder API failed. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            test_results["event_creation_by_clubly_founder"] = False
    else:
        print("❌ Cannot test event creation by clubly_founder without admin token")
        test_results["event_creation_by_clubly_founder"] = False
    
    # Test event creation by promoter
    test_event_creation_by_promoter()
    
    # Test chat management
    test_chat_management()
    
    # Print summary
    print("\n=== Regression Test Results Summary ===")
    regression_tests = [
        "login_for_profile_image",
        "user_profile_viewing",
        "event_creation_by_clubly_founder",
        "event_creation_by_promoter",
        "chat_management"
    ]
    for test_name in regression_tests:
        status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Calculate success rate for regression tests
    success_count = sum(1 for test_name in regression_tests if test_results.get(test_name, False))
    total_count = len(regression_tests)
    success_rate = (success_count / total_count) * 100
    
    print(f"\nRegression tests success rate: {success_rate:.2f}% ({success_count}/{total_count} tests passed)")
