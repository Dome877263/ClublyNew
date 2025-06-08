import requests
import json
import base64
import os
import time
import random
import string
from datetime import datetime, timedelta

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://e8284f37-9eee-4296-9b38-bf14bc6ff4ca.preview.emergentagent.com/api"

# Test results
test_results = {
    # Event poster update test
    "capo_promoter_event_poster_update": False,
    "clubly_founder_event_poster_update": False,
    
    # Automatic PR assignment test
    "booking_automatic_pr_assignment": False,
    "booking_specific_pr_selection": False,
    
    # Notifications test
    "notifications_count": False,
    
    # Organization management test
    "get_available_organizations": False,
    "get_available_capo_promoters": False,
    
    # Event date validation test
    "event_past_date_validation": False,
    
    # Login with needs_password_change test
    "login_needs_password_change": False,
    
    # Error handling test
    "login_incorrect_credentials": False
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
        return True
    else:
        print(f"❌ Login failed with username. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

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
        return True
    else:
        print(f"❌ Login failed with capo promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

# Test login with promoter
def test_login_with_promoter():
    print("\n=== Testing login with promoter ===")
    
    payload = {
        "login": "marco_promoter",
        "password": "Password1@"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["promoter"] = data.get("token")
        print(f"✅ Login successful with promoter. User role: {data['user']['ruolo']}")
        return True
    else:
        print(f"❌ Login failed with promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

# Test 1: Event poster update by capo promoter
def test_capo_promoter_event_poster_update():
    print("\n=== Testing event poster update by capo promoter ===")
    
    # First, we need to login as capo_promoter
    if not tokens["capo_promoter"]:
        if not test_login_with_capo_promoter():
            print("❌ Cannot test event poster update without capo_promoter token")
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
        
        # Get tomorrow's date
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        payload = {
            "name": f"Test Event for Poster {random_string()}",
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
        
        if response.status_code != 200:
            print(f"❌ Could not create test event. Status code: {response.status_code}")
            return False
        
        # Try to get events again
        response = requests.get(f"{BACKEND_URL}/organizations/{organization}/events", headers=headers)
        if response.status_code != 200 or not response.json():
            print("❌ Could not create or find any events for testing")
            return False
        
        events = response.json()
    
    # Use the first event for testing
    event_id = events[0]["id"]
    
    # Update event poster
    poster_payload = {
        "event_poster": create_fake_base64_image()
    }
    
    response = requests.put(f"{BACKEND_URL}/events/{event_id}/poster", json=poster_payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Event poster update by capo promoter successful")
        
        # Verify the update by getting the event details
        response = requests.get(f"{BACKEND_URL}/events/{event_id}", headers=headers)
        if response.status_code == 200:
            updated_event = response.json()
            
            if "event_poster" in updated_event and updated_event["event_poster"]:
                print(f"✅ Event poster field updated successfully")
                test_results["capo_promoter_event_poster_update"] = True
            else:
                print(f"❌ Event poster field not updated")
        else:
            print(f"❌ Could not verify event update. Status code: {response.status_code}")
    else:
        print(f"❌ Event poster update by capo promoter failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["capo_promoter_event_poster_update"]

# Test 2: Event poster update by clubly founder
def test_clubly_founder_event_poster_update():
    print("\n=== Testing event poster update by clubly founder ===")
    
    # First, we need to login as admin (clubly_founder)
    if not tokens["admin"]:
        if not test_login_with_username():
            print("❌ Cannot test event poster update without admin token")
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Get all events
    response = requests.get(f"{BACKEND_URL}/events", headers=headers)
    if response.status_code != 200:
        print(f"❌ Could not get events. Status code: {response.status_code}")
        return False
    
    events = response.json()
    
    if not events:
        print("❌ No events found for testing")
        return False
    
    # Use the first event for testing
    event_id = events[0]["id"]
    
    # Update event poster
    poster_payload = {
        "event_poster": create_fake_base64_image()
    }
    
    response = requests.put(f"{BACKEND_URL}/events/{event_id}/poster", json=poster_payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Event poster update by clubly founder successful")
        
        # Verify the update by getting the event details
        response = requests.get(f"{BACKEND_URL}/events/{event_id}", headers=headers)
        if response.status_code == 200:
            updated_event = response.json()
            
            if "event_poster" in updated_event and updated_event["event_poster"]:
                print(f"✅ Event poster field updated successfully")
                test_results["clubly_founder_event_poster_update"] = True
            else:
                print(f"❌ Event poster field not updated")
        else:
            print(f"❌ Could not verify event update. Status code: {response.status_code}")
    else:
        print(f"❌ Event poster update by clubly founder failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["clubly_founder_event_poster_update"]

# Test 3: Automatic PR assignment for bookings
def test_booking_automatic_pr_assignment():
    print("\n=== Testing automatic PR assignment for bookings ===")
    
    # First, we need to login as a regular user (we'll use admin for simplicity)
    if not tokens["admin"]:
        if not test_login_with_username():
            print("❌ Cannot test booking without admin token")
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Get all events
    response = requests.get(f"{BACKEND_URL}/events", headers=headers)
    if response.status_code != 200:
        print(f"❌ Could not get events. Status code: {response.status_code}")
        return False
    
    events = response.json()
    
    if not events:
        print("❌ No events found for testing")
        return False
    
    # Use the first event for testing
    event_id = events[0]["id"]
    
    # Create a booking with automatic PR assignment (selected_promoter_id = None)
    booking_payload = {
        "event_id": event_id,
        "booking_type": "lista",
        "party_size": 4,
        "selected_promoter_id": None  # This should trigger automatic assignment
    }
    
    response = requests.post(f"{BACKEND_URL}/bookings", json=booking_payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Booking with automatic PR assignment successful")
        
        if "promoter_name" in data:
            print(f"✅ Promoter automatically assigned: {data['promoter_name']}")
            test_results["booking_automatic_pr_assignment"] = True
        else:
            print(f"❌ No promoter name in response")
    else:
        print(f"❌ Booking with automatic PR assignment failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["booking_automatic_pr_assignment"]

# Test 4: Specific PR selection for bookings
def test_booking_specific_pr_selection():
    print("\n=== Testing specific PR selection for bookings ===")
    
    # First, we need to login as a regular user (we'll use admin for simplicity)
    if not tokens["admin"]:
        if not test_login_with_username():
            print("❌ Cannot test booking without admin token")
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Get all events
    response = requests.get(f"{BACKEND_URL}/events", headers=headers)
    if response.status_code != 200:
        print(f"❌ Could not get events. Status code: {response.status_code}")
        return False
    
    events = response.json()
    
    if not events:
        print("❌ No events found for testing")
        return False
    
    # Use the first event for testing
    event_id = events[0]["id"]
    organization = events[0].get("organization")
    
    if not organization:
        print("❌ Event has no organization")
        return False
    
    # Get promoters for this organization
    response = requests.get(f"{BACKEND_URL}/organizations/{organization}/promoters", headers=headers)
    if response.status_code != 200:
        print(f"❌ Could not get organization promoters. Status code: {response.status_code}")
        return False
    
    promoters = response.json()
    
    if not promoters:
        print("❌ No promoters found for this organization")
        return False
    
    # Use the first promoter for testing
    promoter_id = promoters[0]["id"]
    
    # Create a booking with specific PR selection
    booking_payload = {
        "event_id": event_id,
        "booking_type": "lista",
        "party_size": 4,
        "selected_promoter_id": promoter_id  # Specific promoter selection
    }
    
    response = requests.post(f"{BACKEND_URL}/bookings", json=booking_payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Booking with specific PR selection successful")
        
        if "promoter_name" in data:
            print(f"✅ Selected promoter assigned: {data['promoter_name']}")
            test_results["booking_specific_pr_selection"] = True
        else:
            print(f"❌ No promoter name in response")
    else:
        print(f"❌ Booking with specific PR selection failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["booking_specific_pr_selection"]

# Test 5: Notifications count API
def test_notifications_count():
    print("\n=== Testing notifications count API ===")
    
    # Test with different user roles
    
    # 1. Test with clubly founder
    if not tokens["admin"]:
        if not test_login_with_username():
            print("❌ Cannot test notifications without admin token")
            return False
    
    admin_headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/user/notifications", headers=admin_headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Notifications count for clubly founder successful: {data.get('notification_count', 'N/A')}")
        admin_success = True
    else:
        print(f"❌ Notifications count for clubly founder failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        admin_success = False
    
    # 2. Test with capo promoter
    if not tokens["capo_promoter"]:
        if not test_login_with_capo_promoter():
            print("❌ Cannot test notifications without capo_promoter token")
            return False
    
    capo_headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/user/notifications", headers=capo_headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Notifications count for capo promoter successful: {data.get('notification_count', 'N/A')}")
        capo_success = True
    else:
        print(f"❌ Notifications count for capo promoter failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        capo_success = False
    
    # Overall success if at least one test passed
    test_results["notifications_count"] = admin_success or capo_success
    
    return test_results["notifications_count"]

# Test 6: Get available organizations API
def test_get_available_organizations():
    print("\n=== Testing get available organizations API ===")
    
    # This is a public API, no token needed
    response = requests.get(f"{BACKEND_URL}/organizations")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Get available organizations successful. Organizations count: {len(data)}")
        
        if len(data) > 0:
            print(f"   First organization: {data[0].get('name')}")
            test_results["get_available_organizations"] = True
        else:
            print(f"   No organizations found")
            test_results["get_available_organizations"] = False
    else:
        print(f"❌ Get available organizations failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["get_available_organizations"]

# Test 7: Get available capo promoters API
def test_get_available_capo_promoters():
    print("\n=== Testing get available capo promoters API ===")
    
    # First, we need to login as admin (clubly_founder)
    if not tokens["admin"]:
        if not test_login_with_username():
            print("❌ Cannot test get available capo promoters without admin token")
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/organizations/available-capo-promoters", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Get available capo promoters successful. Capo promoters count: {len(data)}")
        test_results["get_available_capo_promoters"] = True
    else:
        print(f"❌ Get available capo promoters failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["get_available_capo_promoters"]

# Test 8: Event past date validation
def test_event_past_date_validation():
    print("\n=== Testing event past date validation ===")
    
    # First, we need to login as admin (clubly_founder)
    if not tokens["admin"]:
        if not test_login_with_username():
            print("❌ Cannot test event past date validation without admin token")
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Try to create an event with a past date
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    payload = {
        "name": f"Past Event {random_string()}",
        "date": yesterday,
        "start_time": "21:00",
        "location": "Past Club, Milano",
        "organization": "Night Events Milano",
        "end_time": "05:00",
        "lineup": ["DJ Past", "DJ History"],
        "guests": ["Past Guest"],
        "total_tables": 15,
        "tables_available": 15,
        "max_party_size": 10
    }
    
    response = requests.post(f"{BACKEND_URL}/events", json=payload, headers=headers)
    
    # The request should fail with a 400 Bad Request
    if response.status_code == 400:
        print(f"✅ Event past date validation successful - correctly rejected past date")
        test_results["event_past_date_validation"] = True
    else:
        print(f"❌ Event past date validation failed. Expected 400, got: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["event_past_date_validation"]

# Test 9: Login with needs_password_change flag
def test_login_needs_password_change():
    print("\n=== Testing login with needs_password_change flag ===")
    
    # First, we need to create a temporary user that needs password change
    if not tokens["admin"]:
        if not test_login_with_username():
            print("❌ Cannot create temporary user without admin token")
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Create temporary user
    temp_email = f"temp_user_{random_string()}@test.com"
    temp_password = "TempPassword123"
    
    payload = {
        "nome": "Temporary",
        "email": temp_email,
        "password": temp_password,
        "ruolo": "promoter",
        "organization": "Night Events Milano"
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not create temporary user. Status code: {response.status_code}")
        return False
    
    # Now login with the temporary credentials
    login_payload = {
        "login": temp_email,
        "password": temp_password
    }
    
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        
        # Check if needs_password_change flag is present and true
        if "needs_password_change" in login_data["user"] and login_data["user"]["needs_password_change"]:
            print(f"✅ Login with needs_password_change flag successful")
            
            # Now test changing the password
            temp_token = login_data.get("token")
            temp_headers = {
                "Authorization": f"Bearer {temp_token}"
            }
            
            change_password_payload = {
                "current_password": temp_password,
                "new_password": "NewPassword123"
            }
            
            change_response = requests.post(f"{BACKEND_URL}/user/change-password", json=change_password_payload, headers=temp_headers)
            
            if change_response.status_code == 200:
                print(f"✅ Password change successful")
                
                # Login again to verify needs_password_change is now false
                login_payload = {
                    "login": temp_email,
                    "password": "NewPassword123"
                }
                
                login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    
                    if "needs_password_change" in login_data["user"] and not login_data["user"]["needs_password_change"]:
                        print(f"✅ needs_password_change flag correctly set to false after password change")
                        test_results["login_needs_password_change"] = True
                    else:
                        print(f"❌ needs_password_change flag not set to false after password change")
                else:
                    print(f"❌ Login after password change failed. Status code: {login_response.status_code}")
            else:
                print(f"❌ Password change failed. Status code: {change_response.status_code}")
                print(f"Response: {change_response.text}")
        else:
            print(f"❌ needs_password_change flag not present or not true")
    else:
        print(f"❌ Login with temporary credentials failed. Status code: {login_response.status_code}")
        print(f"Response: {login_response.text}")
    
    return test_results["login_needs_password_change"]

# Test 10: Login with incorrect credentials
def test_login_incorrect_credentials():
    print("\n=== Testing login with incorrect credentials ===")
    
    # Test with incorrect password
    payload = {
        "login": "admin",
        "password": "wrong_password"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    # The request should fail with a 401 Unauthorized
    if response.status_code == 401:
        print(f"✅ Login with incorrect password correctly rejected with 401")
        password_test = True
    else:
        print(f"❌ Login with incorrect password test failed. Expected 401, got: {response.status_code}")
        print(f"Response: {response.text}")
        password_test = False
    
    # Test with non-existent user
    payload = {
        "login": f"nonexistent_user_{random_string()}",
        "password": "any_password"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    # The request should fail with a 401 Unauthorized
    if response.status_code == 401:
        print(f"✅ Login with non-existent user correctly rejected with 401")
        user_test = True
    else:
        print(f"❌ Login with non-existent user test failed. Expected 401, got: {response.status_code}")
        print(f"Response: {response.text}")
        user_test = False
    
    test_results["login_incorrect_credentials"] = password_test and user_test
    
    return test_results["login_incorrect_credentials"]

# Run all tests
def run_all_tests():
    print("\n=== Running all backend API tests for new features ===\n")
    
    # Event poster update tests
    test_capo_promoter_event_poster_update()
    test_clubly_founder_event_poster_update()
    
    # Booking PR assignment tests
    test_booking_automatic_pr_assignment()
    test_booking_specific_pr_selection()
    
    # Notifications test
    test_notifications_count()
    
    # Organization management tests
    test_get_available_organizations()
    test_get_available_capo_promoters()
    
    # Event date validation test
    test_event_past_date_validation()
    
    # Login with needs_password_change test
    test_login_needs_password_change()
    
    # Error handling test
    test_login_incorrect_credentials()
    
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
