import requests
import json
import random
import string
from datetime import datetime, timedelta

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://cf2530ec-d455-4e05-aef3-ef00e108bc21.preview.emergentagent.com/api"

# Test results
test_results = {
    # Organization Promoters API
    "get_organization_promoters": False,
    
    # Booking with Promoter Selection API
    "booking_with_selected_promoter": False,
    "booking_with_auto_assignment": False,
    
    # Regression tests
    "login_regression": False,
    "dashboard_regression": False,
    "profile_viewing_regression": False,
    "events_regression": False
}

# Store tokens for different user roles
tokens = {
    "admin": None,
    "capo_promoter": None,
    "promoter": None,
    "client": None
}

# Helper function to generate a random string
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Helper function to create a fake base64 image
def create_fake_base64_image():
    # This is a tiny 1x1 transparent PNG image
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

# Test login with different roles
def test_login():
    print("\n=== Testing login for different roles ===")
    
    # Login as admin (clubly_founder)
    admin_payload = {
        "login": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=admin_payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["admin"] = data.get("token")
        print(f"✅ Login successful as admin (clubly_founder)")
    else:
        print(f"❌ Login failed as admin. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # Login as capo_promoter
    capo_payload = {
        "login": "capo_milano",
        "password": "Password1"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=capo_payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["capo_promoter"] = data.get("token")
        print(f"✅ Login successful as capo_promoter")
    else:
        print(f"❌ Login failed as capo_promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # Register a new client for booking tests
    client_username = f"client_{random_string()}"
    client_email = f"{client_username}@test.com"
    
    client_payload = {
        "nome": "Test",
        "cognome": "Client",
        "email": client_email,
        "username": client_username,
        "password": "TestPassword123",
        "data_nascita": "1990-01-01",
        "citta": "Test City",
        "ruolo": "cliente",
        "profile_image": create_fake_base64_image(),
        "biografia": "Test client for booking API tests"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=client_payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["client"] = data.get("token")
        print(f"✅ Registration successful for test client: {client_username}")
    else:
        print(f"❌ Registration failed for test client. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    test_results["login_regression"] = True
    return True

# Test Organization Promoters API
def test_organization_promoters_api():
    print("\n=== Testing Organization Promoters API ===")
    
    if not tokens["client"]:
        print("❌ Cannot test organization promoters API without client token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['client']}"
    }
    
    # First, get all organizations to find one with promoters
    response = requests.get(f"{BACKEND_URL}/organizations", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not get organizations list. Status code: {response.status_code}")
        return False
    
    organizations = response.json()
    
    if not organizations:
        print("❌ No organizations found")
        return False
    
    # Try each organization until we find one with promoters
    for org in organizations:
        org_name = org["name"]
        print(f"Testing organization: {org_name}")
        
        response = requests.get(f"{BACKEND_URL}/organizations/{org_name}/promoters", headers=headers)
        
        if response.status_code == 200:
            promoters = response.json()
            
            if promoters:
                print(f"✅ Organization Promoters API successful. Found {len(promoters)} promoters for {org_name}")
                
                # Check if all required fields are present in the response
                required_fields = ["id", "nome", "cognome", "username", "profile_image", "ruolo", "biografia"]
                all_fields_present = all(field in promoters[0] for field in required_fields)
                
                if all_fields_present:
                    print(f"✅ All required fields are present in the response")
                    
                    # Print sample promoter data
                    sample_promoter = promoters[0]
                    print(f"   Sample promoter: {sample_promoter['nome']} {sample_promoter['cognome']} (@{sample_promoter['username']})")
                    print(f"   Role: {sample_promoter['ruolo']}")
                    print(f"   Biography: {sample_promoter['biografia']}")
                    
                    test_results["get_organization_promoters"] = True
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in promoters[0]]
                    print(f"❌ Missing required fields in response: {missing_fields}")
            else:
                print(f"ℹ️ No promoters found for {org_name}, trying another organization")
        else:
            print(f"❌ Organization Promoters API failed for {org_name}. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    print("❌ Could not find an organization with promoters")
    return False

# Test Booking with Selected Promoter API
def test_booking_with_selected_promoter():
    print("\n=== Testing Booking with Selected Promoter API ===")
    
    if not tokens["client"]:
        print("❌ Cannot test booking API without client token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['client']}"
    }
    
    # First, get all events to find one for booking
    response = requests.get(f"{BACKEND_URL}/events", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not get events list. Status code: {response.status_code}")
        return False
    
    events = response.json()
    
    if not events:
        print("❌ No events found")
        return False
    
    # Use the first event for testing
    event = events[0]
    event_id = event["id"]
    organization_name = event["organization"]
    
    print(f"Using event: {event['name']} (ID: {event_id})")
    print(f"Organization: {organization_name}")
    
    # Get promoters for this organization
    response = requests.get(f"{BACKEND_URL}/organizations/{organization_name}/promoters", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not get promoters for organization. Status code: {response.status_code}")
        return False
    
    promoters = response.json()
    
    if not promoters:
        print(f"❌ No promoters found for organization {organization_name}")
        return False
    
    # Use the first promoter for testing
    selected_promoter = promoters[0]
    selected_promoter_id = selected_promoter["id"]
    
    print(f"Selected promoter: {selected_promoter['nome']} {selected_promoter['cognome']} (@{selected_promoter['username']})")
    
    # Create booking with selected promoter
    booking_payload = {
        "event_id": event_id,
        "booking_type": "lista",
        "party_size": 4,
        "selected_promoter_id": selected_promoter_id
    }
    
    response = requests.post(f"{BACKEND_URL}/bookings", json=booking_payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Booking with selected promoter successful. Booking ID: {data.get('booking_id')}")
        
        # Check if the response includes the promoter name
        if "promoter_name" in data:
            print(f"✅ Response includes promoter name: {data['promoter_name']}")
            test_results["booking_with_selected_promoter"] = True
        else:
            print(f"❌ Response does not include promoter name")
    else:
        print(f"❌ Booking with selected promoter failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["booking_with_selected_promoter"]

# Test Booking with Auto Assignment API
def test_booking_with_auto_assignment():
    print("\n=== Testing Booking with Auto Assignment API ===")
    
    if not tokens["client"]:
        print("❌ Cannot test booking API without client token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['client']}"
    }
    
    # First, get all events to find one for booking
    response = requests.get(f"{BACKEND_URL}/events", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not get events list. Status code: {response.status_code}")
        return False
    
    events = response.json()
    
    if not events:
        print("❌ No events found")
        return False
    
    # Use the first event for testing
    event = events[0]
    event_id = event["id"]
    
    print(f"Using event: {event['name']} (ID: {event_id})")
    
    # Create booking with auto assignment (no selected_promoter_id)
    booking_payload = {
        "event_id": event_id,
        "booking_type": "lista",
        "party_size": 3
        # No selected_promoter_id - should be auto-assigned
    }
    
    response = requests.post(f"{BACKEND_URL}/bookings", json=booking_payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Booking with auto assignment successful. Booking ID: {data.get('booking_id')}")
        
        # Check if the response includes the promoter name
        if "promoter_name" in data:
            print(f"✅ Response includes auto-assigned promoter name: {data['promoter_name']}")
            test_results["booking_with_auto_assignment"] = True
        else:
            print(f"❌ Response does not include promoter name")
    else:
        print(f"❌ Booking with auto assignment failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["booking_with_auto_assignment"]

# Test Dashboard APIs (regression test)
def test_dashboard_apis():
    print("\n=== Testing Dashboard APIs (Regression) ===")
    
    # Test clubly_founder dashboard
    if tokens["admin"]:
        headers = {
            "Authorization": f"Bearer {tokens['admin']}"
        }
        
        response = requests.get(f"{BACKEND_URL}/dashboard/clubly-founder", headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Clubly founder dashboard API successful")
            founder_dashboard_ok = True
        else:
            print(f"❌ Clubly founder dashboard API failed. Status code: {response.status_code}")
            founder_dashboard_ok = False
    else:
        print("❌ Cannot test clubly founder dashboard without admin token")
        founder_dashboard_ok = False
    
    # Test capo_promoter dashboard
    if tokens["capo_promoter"]:
        headers = {
            "Authorization": f"Bearer {tokens['capo_promoter']}"
        }
        
        response = requests.get(f"{BACKEND_URL}/dashboard/capo-promoter", headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Capo promoter dashboard API successful")
            capo_dashboard_ok = True
        else:
            print(f"❌ Capo promoter dashboard API failed. Status code: {response.status_code}")
            capo_dashboard_ok = False
    else:
        print("❌ Cannot test capo promoter dashboard without capo_promoter token")
        capo_dashboard_ok = False
    
    test_results["dashboard_regression"] = founder_dashboard_ok and capo_dashboard_ok
    return test_results["dashboard_regression"]

# Test Profile Viewing API (regression test)
def test_profile_viewing_api():
    print("\n=== Testing Profile Viewing API (Regression) ===")
    
    if not tokens["client"]:
        print("❌ Cannot test profile viewing API without client token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['client']}"
    }
    
    # Get a user ID to view (we'll use the admin's ID)
    import jwt
    admin_token_data = jwt.decode(tokens["admin"], options={"verify_signature": False})
    user_id = admin_token_data.get("id")
    
    if not user_id:
        print("❌ Could not extract user ID from admin token")
        return False
    
    response = requests.get(f"{BACKEND_URL}/users/{user_id}/profile", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Profile viewing API successful. Username: {data.get('username')}")
        
        # Check if all required fields are present
        required_fields = ["id", "nome", "cognome", "username", "profile_image", "citta", "biografia", "ruolo"]
        all_fields_present = all(field in data for field in required_fields)
        
        if all_fields_present:
            print(f"✅ All required fields are present in the profile response")
            test_results["profile_viewing_regression"] = True
        else:
            missing_fields = [field for field in required_fields if field not in data]
            print(f"❌ Missing required fields in profile response: {missing_fields}")
    else:
        print(f"❌ Profile viewing API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["profile_viewing_regression"]

# Test Events API (regression test)
def test_events_api():
    print("\n=== Testing Events API (Regression) ===")
    
    if not tokens["client"]:
        print("❌ Cannot test events API without client token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['client']}"
    }
    
    # Get all events
    response = requests.get(f"{BACKEND_URL}/events", headers=headers)
    
    if response.status_code == 200:
        events = response.json()
        print(f"✅ Events API successful. Found {len(events)} events")
        
        if events:
            # Get details for the first event
            event_id = events[0]["id"]
            response = requests.get(f"{BACKEND_URL}/events/{event_id}", headers=headers)
            
            if response.status_code == 200:
                event_details = response.json()
                print(f"✅ Event details API successful. Event: {event_details.get('name')}")
                test_results["events_regression"] = True
            else:
                print(f"❌ Event details API failed. Status code: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print("ℹ️ No events found to test details API")
            test_results["events_regression"] = True  # Still mark as success if the main API works
    else:
        print(f"❌ Events API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["events_regression"]

# Run all tests
def run_all_tests():
    print("\n=== Running all Clubly API tests ===\n")
    
    # Login first
    if not test_login():
        print("❌ Login failed, cannot proceed with other tests")
        return
    
    # Test new APIs
    test_organization_promoters_api()
    test_booking_with_selected_promoter()
    test_booking_with_auto_assignment()
    
    # Regression tests
    test_dashboard_apis()
    test_profile_viewing_api()
    test_events_api()
    
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

if __name__ == "__main__":
    run_all_tests()