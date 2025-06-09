import requests
import json
import random
import string
from datetime import datetime, timedelta

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://86371f8e-929c-484d-b4db-cf725ee6a471.preview.emergentagent.com/api"

# Test results
test_results = {
    "create_capo_promoter_without_organization": False,
    "create_capo_promoter_with_organization": False,
    "login_regression": False,
    "booking_regression": False,
    "chat_regression": False,
    "chat_send_message": False
}

# Store tokens for different user roles
tokens = {
    "admin": None,
    "capo_promoter": None,
    "promoter": None,
    "cliente": None
}

# Helper function to generate a random string
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Helper function to create a fake base64 image
def create_fake_base64_image():
    # This is a tiny 1x1 transparent PNG image
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

# Test login with admin (clubly_founder)
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
        return True
    else:
        print(f"❌ Login failed with admin. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

# Test login with capo_promoter
def test_login_capo_promoter():
    print("\n=== Testing login with capo_promoter ===")
    
    payload = {
        "login": "capo_milano",
        "password": "Password1"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["capo_promoter"] = data.get("token")
        print(f"✅ Login successful with capo_promoter. User role: {data['user']['ruolo']}")
        return True
    else:
        print(f"❌ Login failed with capo_promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

# Test login with promoter
def test_login_promoter():
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

# Test creating a capo promoter without organization
def test_create_capo_promoter_without_organization():
    print("\n=== Testing creation of capo promoter without organization ===")
    
    # First, we need to login as admin (clubly_founder)
    if not tokens["admin"]:
        if not test_login_admin():
            print("❌ Cannot test create capo promoter without admin token")
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Generate random user data
    email = f"capo_no_org_{random_string()}@test.com"
    
    payload = {
        "nome": "Capo Test",
        "email": email,
        "password": "Password1",
        "ruolo": "capo_promoter"
        # No organization field
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Capo promoter created successfully without organization. User ID: {data.get('user_id')}")
        
        # Verify the organization is "Da assegnare" (To be assigned)
        if data.get('organization') == "Da assegnare":
            print(f"✅ Organization correctly set to 'Da assegnare'")
            
            # Try to login with the new capo promoter
            login_payload = {
                "login": email,
                "password": "Password1"
            }
            
            login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"✅ Login successful with new capo promoter without organization")
                
                # Verify the organization field is null or empty in the user data
                if not login_data['user'].get('organization'):
                    print(f"✅ Organization field is correctly empty in user data")
                    test_results["create_capo_promoter_without_organization"] = True
                else:
                    print(f"❌ Organization field is not empty: {login_data['user'].get('organization')}")
            else:
                print(f"❌ Login failed with new capo promoter. Status code: {login_response.status_code}")
                print(f"Response: {login_response.text}")
        else:
            print(f"❌ Organization not correctly set to 'Da assegnare': {data.get('organization')}")
    else:
        print(f"❌ Create capo promoter without organization failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["create_capo_promoter_without_organization"]

# Test creating a capo promoter with organization
def test_create_capo_promoter_with_organization():
    print("\n=== Testing creation of capo promoter with organization ===")
    
    # First, we need to login as admin (clubly_founder)
    if not tokens["admin"]:
        if not test_login_admin():
            print("❌ Cannot test create capo promoter without admin token")
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Get available organizations
    response = requests.get(f"{BACKEND_URL}/organizations", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not get organizations. Status code: {response.status_code}")
        return False
    
    organizations = response.json()
    
    if not organizations:
        print("❌ No organizations found")
        return False
    
    # Use the first organization
    organization_name = organizations[0]["name"]
    
    # Generate random user data
    email = f"capo_with_org_{random_string()}@test.com"
    
    payload = {
        "nome": "Capo Test Org",
        "email": email,
        "password": "Password1",
        "ruolo": "capo_promoter",
        "organization": organization_name
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Capo promoter created successfully with organization. User ID: {data.get('user_id')}")
        
        # Verify the organization is set correctly
        if data.get('organization') == organization_name:
            print(f"✅ Organization correctly set to '{organization_name}'")
            
            # Try to login with the new capo promoter
            login_payload = {
                "login": email,
                "password": "Password1"
            }
            
            login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"✅ Login successful with new capo promoter with organization")
                
                # Verify the organization field is set correctly in the user data
                if login_data['user'].get('organization') == organization_name:
                    print(f"✅ Organization field is correctly set to '{organization_name}' in user data")
                    test_results["create_capo_promoter_with_organization"] = True
                else:
                    print(f"❌ Organization field is not set correctly: {login_data['user'].get('organization')}")
            else:
                print(f"❌ Login failed with new capo promoter. Status code: {login_response.status_code}")
                print(f"Response: {login_response.text}")
        else:
            print(f"❌ Organization not correctly set: {data.get('organization')}")
    else:
        print(f"❌ Create capo promoter with organization failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["create_capo_promoter_with_organization"]

# Test login regression
def test_login_regression():
    print("\n=== Testing login regression ===")
    
    # Test login with different roles
    admin_login = test_login_admin()
    capo_login = test_login_capo_promoter()
    promoter_login = test_login_promoter()
    
    # Test login with wrong credentials
    print("\n=== Testing login with wrong credentials ===")
    
    payload = {
        "login": "admin",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 401:
        print(f"✅ Login correctly failed with wrong password. Status code: {response.status_code}")
        wrong_password_test = True
    else:
        print(f"❌ Login with wrong password returned unexpected status code: {response.status_code}")
        print(f"Response: {response.text}")
        wrong_password_test = False
    
    # Test login with non-existent user
    print("\n=== Testing login with non-existent user ===")
    
    payload = {
        "login": f"nonexistent_{random_string()}",
        "password": "anypassword"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 401:
        print(f"✅ Login correctly failed with non-existent user. Status code: {response.status_code}")
        nonexistent_user_test = True
    else:
        print(f"❌ Login with non-existent user returned unexpected status code: {response.status_code}")
        print(f"Response: {response.text}")
        nonexistent_user_test = False
    
    # Overall login regression test passes if all sub-tests pass
    test_results["login_regression"] = admin_login and capo_login and promoter_login and wrong_password_test and nonexistent_user_test
    
    return test_results["login_regression"]

# Test booking regression
def test_booking_regression():
    print("\n=== Testing booking regression ===")
    
    # First, we need to create a client account
    # Generate random user data
    username = f"client_{random_string()}"
    email = f"{username}@test.com"
    
    register_payload = {
        "nome": "Test Client",
        "cognome": "User",
        "email": email,
        "username": username,
        "password": "TestPassword123",
        "data_nascita": "1990-01-01",
        "citta": "Test City",
        "ruolo": "cliente",
        "profile_image": create_fake_base64_image()
    }
    
    register_response = requests.post(f"{BACKEND_URL}/auth/register", json=register_payload)
    
    if register_response.status_code != 200:
        print(f"❌ Could not create client account. Status code: {register_response.status_code}")
        print(f"Response: {register_response.text}")
        return False
    
    client_data = register_response.json()
    tokens["cliente"] = client_data.get("token")
    
    print(f"✅ Client account created successfully. Username: {username}")
    
    # Get available events
    response = requests.get(f"{BACKEND_URL}/events")
    
    if response.status_code != 200:
        print(f"❌ Could not get events. Status code: {response.status_code}")
        return False
    
    events = response.json()
    
    if not events:
        print("❌ No events found")
        return False
    
    # Use the first event for booking
    event_id = events[0]["id"]
    
    # Test 1: Booking with automatic promoter assignment (selected_promoter_id = null)
    print("\n=== Test 1: Booking with automatic promoter assignment ===")
    
    headers = {
        "Authorization": f"Bearer {tokens['cliente']}"
    }
    
    booking_payload = {
        "event_id": event_id,
        "booking_type": "lista",
        "party_size": 4
        # No selected_promoter_id - should be assigned automatically
    }
    
    response = requests.post(f"{BACKEND_URL}/bookings", json=booking_payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Booking with automatic promoter assignment successful. Booking ID: {data.get('booking_id')}")
        print(f"   Assigned promoter: {data.get('promoter_name')}")
        auto_assign_test = True
    else:
        print(f"❌ Booking with automatic promoter assignment failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        auto_assign_test = False
    
    # Test 2: Booking with specific promoter selection
    print("\n=== Test 2: Booking with specific promoter selection ===")
    
    # Get organization of the event
    event_org = events[0].get("organization")
    
    if not event_org:
        print("❌ Event has no organization")
        specific_promoter_test = False
    else:
        # Get promoters for this organization
        response = requests.get(f"{BACKEND_URL}/organizations/{event_org}/promoters", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Could not get promoters for organization. Status code: {response.status_code}")
            specific_promoter_test = False
        else:
            promoters = response.json()
            
            if not promoters:
                print("❌ No promoters found for this organization")
                specific_promoter_test = False
            else:
                # Use the first promoter
                promoter_id = promoters[0]["id"]
                
                booking_payload = {
                    "event_id": event_id,
                    "booking_type": "lista",
                    "party_size": 3,
                    "selected_promoter_id": promoter_id
                }
                
                response = requests.post(f"{BACKEND_URL}/bookings", json=booking_payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Booking with specific promoter selection successful. Booking ID: {data.get('booking_id')}")
                    print(f"   Selected promoter: {data.get('promoter_name')}")
                    specific_promoter_test = True
                else:
                    print(f"❌ Booking with specific promoter selection failed. Status code: {response.status_code}")
                    print(f"Response: {response.text}")
                    specific_promoter_test = False
    
    # Overall booking regression test passes if both sub-tests pass
    test_results["booking_regression"] = auto_assign_test and specific_promoter_test
    
    return test_results["booking_regression"]

# Test chat regression
def test_chat_regression():
    print("\n=== Testing chat regression ===")
    
    # We need a client token
    if not tokens["cliente"]:
        print("❌ Cannot test chat regression without client token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['cliente']}"
    }
    
    # Test 1: Get user chats
    print("\n=== Test 1: Get user chats ===")
    
    response = requests.get(f"{BACKEND_URL}/user/chats", headers=headers)
    
    if response.status_code == 200:
        chats = response.json()
        print(f"✅ Get user chats successful. Chats count: {len(chats)}")
        get_chats_success = True
        
        if chats:
            # Use the first chat for testing
            chat_id = chats[0]["id"]
            
            # Test 2: Get chat messages
            print("\n=== Test 2: Get chat messages ===")
            
            response = requests.get(f"{BACKEND_URL}/chats/{chat_id}/messages", headers=headers)
            
            if response.status_code == 200:
                messages = response.json()
                print(f"✅ Get chat messages successful. Messages count: {len(messages)}")
                get_messages_success = True
            else:
                print(f"❌ Get chat messages failed. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                get_messages_success = False
        else:
            print("ℹ️ No chats found to test messages")
            get_messages_success = True  # Skip this test
    else:
        print(f"❌ Get user chats failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        get_chats_success = False
        get_messages_success = False
    
    # Overall chat regression test passes if both sub-tests pass
    test_results["chat_regression"] = get_chats_success and get_messages_success
    
    return test_results["chat_regression"]

# Test chat send message
def test_chat_send_message():
    print("\n=== Testing chat send message ===")
    
    # We need a client token
    if not tokens["cliente"]:
        print("❌ Cannot test chat send message without client token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['cliente']}"
    }
    
    # Get user chats
    response = requests.get(f"{BACKEND_URL}/user/chats", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not get user chats. Status code: {response.status_code}")
        return False
    
    chats = response.json()
    
    if not chats:
        print("❌ No chats found")
        return False
    
    # Use the first chat for testing
    chat_id = chats[0]["id"]
    
    # Send a message
    message_payload = {
        "chat_id": chat_id,
        "sender_id": "",  # Will be filled from token
        "sender_role": "",  # Will be filled from token
        "message": f"Test message {random_string()}"
    }
    
    response = requests.post(f"{BACKEND_URL}/chats/{chat_id}/messages", json=message_payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Send message successful. Message ID: {data.get('message_id')}")
        
        # Verify the message was added by getting the chat messages
        response = requests.get(f"{BACKEND_URL}/chats/{chat_id}/messages", headers=headers)
        
        if response.status_code == 200:
            messages = response.json()
            
            # Check if the last message contains our test message
            if messages and any(message_payload["message"] in msg.get("message", "") for msg in messages):
                print(f"✅ Message verification successful. Message found in chat history.")
                test_results["chat_send_message"] = True
            else:
                print(f"❌ Message verification failed. Message not found in chat history.")
        else:
            print(f"❌ Could not verify message. Status code: {response.status_code}")
    else:
        print(f"❌ Send message failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["chat_send_message"]

# Run all tests
def run_all_tests():
    print("\n=== Running all tests for Clubly capo promoter and regression ===\n")
    
    # Test capo promoter creation
    test_create_capo_promoter_without_organization()
    test_create_capo_promoter_with_organization()
    
    # Test regression
    test_login_regression()
    test_booking_regression()
    test_chat_regression()
    test_chat_send_message()
    
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