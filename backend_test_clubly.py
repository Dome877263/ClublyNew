import requests
import json
import base64
import os
import time
import random
import string
import jwt
from datetime import datetime, timedelta

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://86371f8e-929c-484d-b4db-cf725ee6a471.preview.emergentagent.com/api"

# Test results
test_results = {
    # Authentication tests
    "login_authentication": False,
    "login_error_handling": False,
    "login_needs_password_change": False,
    
    # Booking tests
    "booking_auto_promoter_assignment": False,
    "booking_specific_promoter": False,
    
    # Chat tests
    "chat_get_messages": False,
    "chat_send_message": False,
    
    # Dashboard tests
    "dashboard_clubly_founder": False,
    "dashboard_capo_promoter": False,
    "dashboard_promoter": False,
    
    # Organization tests
    "organization_promoters_api": False
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

# Test login with admin
def test_login_admin():
    print("\n=== Testing login with admin ===")
    
    payload = {
        "login": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["admin"] = data.get("token")
        print(f"✅ Login successful with admin. User role: {data['user']['ruolo']}")
        print(f"   Needs password change: {data['user'].get('needs_password_change', False)}")
        test_results["login_authentication"] = True
        return True
    else:
        print(f"❌ Login failed with admin. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

# Test login with capo promoter
def test_login_capo_promoter():
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
        print(f"   Organization: {data['user'].get('organization')}")
        return True
    else:
        print(f"❌ Login failed with capo promoter. Status code: {response.status_code}")
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
        print(f"   Organization: {data['user'].get('organization')}")
        return True
    else:
        print(f"❌ Login failed with promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

# Test login error handling
def test_login_error_handling():
    print("\n=== Testing login error handling ===")
    
    # Test with wrong password
    payload = {
        "login": "admin",
        "password": "wrong_password"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 401:
        print(f"✅ Login correctly rejected with wrong password. Status code: {response.status_code}")
        print(f"   Error message: {response.json().get('detail')}")
        wrong_password_test = True
    else:
        print(f"❌ Login with wrong password not properly handled. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        wrong_password_test = False
    
    # Test with non-existent user
    payload = {
        "login": "nonexistent_user",
        "password": "password123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 401:
        print(f"✅ Login correctly rejected with non-existent user. Status code: {response.status_code}")
        print(f"   Error message: {response.json().get('detail')}")
        nonexistent_user_test = True
    else:
        print(f"❌ Login with non-existent user not properly handled. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        nonexistent_user_test = False
    
    test_results["login_error_handling"] = wrong_password_test and nonexistent_user_test
    return test_results["login_error_handling"]

# Test login with needs_password_change flag
def test_login_needs_password_change():
    print("\n=== Testing login with needs_password_change flag ===")
    
    # First, create a temporary user that needs password change
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test needs_password_change without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Create temporary user
    temp_email = f"temp_user_{random_string()}@test.com"
    temp_password = "TempPassword123"
    
    create_payload = {
        "nome": "Temporary",
        "email": temp_email,
        "password": temp_password,
        "ruolo": "promoter",
        "organization": "Night Events Milano"
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=create_payload, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not create temporary user. Status code: {response.status_code}")
        return False
    
    # Login with temporary user
    login_payload = {
        "login": temp_email,
        "password": temp_password
    }
    
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
    
    if login_response.status_code == 200:
        data = login_response.json()
        temp_token = data.get("token")
        
        # Check if needs_password_change flag is present and true
        if data["user"].get("needs_password_change") == True:
            print(f"✅ Login response correctly includes needs_password_change=true")
            
            # Now change the password
            change_payload = {
                "current_password": temp_password,
                "new_password": "NewPassword456"
            }
            
            change_headers = {
                "Authorization": f"Bearer {temp_token}"
            }
            
            change_response = requests.post(f"{BACKEND_URL}/user/change-password", json=change_payload, headers=change_headers)
            
            if change_response.status_code == 200:
                print(f"✅ Password change successful")
                
                # Login again to check if flag is now false
                login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                    "login": temp_email,
                    "password": "NewPassword456"
                })
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    if data["user"].get("needs_password_change") == False:
                        print(f"✅ After password change, needs_password_change flag is correctly set to false")
                        test_results["login_needs_password_change"] = True
                    else:
                        print(f"❌ After password change, needs_password_change flag is still true")
                else:
                    print(f"❌ Login after password change failed. Status code: {login_response.status_code}")
            else:
                print(f"❌ Password change failed. Status code: {change_response.status_code}")
                print(f"Response: {change_response.text}")
        else:
            print(f"❌ Login response does not include needs_password_change=true")
    else:
        print(f"❌ Login with temporary user failed. Status code: {login_response.status_code}")
        print(f"Response: {login_response.text}")
    
    return test_results["login_needs_password_change"]

# Test booking with automatic promoter assignment
def test_booking_auto_promoter_assignment():
    print("\n=== Testing booking with automatic promoter assignment ===")
    
    # Create a client account
    client_email = f"client_{random_string()}@test.com"
    client_password = "ClientPassword123"
    
    register_payload = {
        "nome": "Test",
        "cognome": "Client",
        "email": client_email,
        "username": f"client_{random_string()}",
        "password": client_password,
        "data_nascita": "1990-01-01",
        "citta": "Test City",
        "ruolo": "cliente"
    }
    
    register_response = requests.post(f"{BACKEND_URL}/auth/register", json=register_payload)
    
    if register_response.status_code != 200:
        print(f"❌ Could not register client. Status code: {register_response.status_code}")
        return False
    
    client_token = register_response.json().get("token")
    tokens["client"] = client_token
    
    client_headers = {
        "Authorization": f"Bearer {client_token}"
    }
    
    # Get an event to book
    response = requests.get(f"{BACKEND_URL}/events")
    
    if response.status_code != 200 or not response.json():
        print(f"❌ Could not get events. Status code: {response.status_code}")
        return False
    
    events = response.json()
    event_id_to_book = events[0]["id"]
    
    # Create booking with automatic promoter assignment
    booking_payload = {
        "event_id": event_id_to_book,
        "booking_type": "lista",
        "party_size": 4,
        "selected_promoter_id": None  # Auto-assign
    }
    
    response = requests.post(f"{BACKEND_URL}/bookings", json=booking_payload, headers=client_headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Booking with auto-assignment successful")
        print(f"   Booking ID: {data.get('booking_id')}")
        print(f"   Chat ID: {data.get('chat_id')}")
        print(f"   Assigned promoter: {data.get('promoter_name')}")
        
        # Store chat ID for later tests
        global chat_id
        chat_id = data.get('chat_id')
        
        test_results["booking_auto_promoter_assignment"] = True
    else:
        print(f"❌ Booking with auto-assignment failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["booking_auto_promoter_assignment"]

# Test booking with specific promoter selection
def test_booking_specific_promoter():
    print("\n=== Testing booking with specific promoter selection ===")
    
    # Use the client token from previous test or create a new client
    if not tokens["client"]:
        # Create a client account
        client_email = f"client_{random_string()}@test.com"
        client_password = "ClientPassword123"
        
        register_payload = {
            "nome": "Test",
            "cognome": "Client",
            "email": client_email,
            "username": f"client_{random_string()}",
            "password": client_password,
            "data_nascita": "1990-01-01",
            "citta": "Test City",
            "ruolo": "cliente"
        }
        
        register_response = requests.post(f"{BACKEND_URL}/auth/register", json=register_payload)
        
        if register_response.status_code != 200:
            print(f"❌ Could not register client. Status code: {register_response.status_code}")
            return False
        
        client_token = register_response.json().get("token")
        tokens["client"] = client_token
    
    client_headers = {
        "Authorization": f"Bearer {tokens['client']}"
    }
    
    # Get an event to book
    response = requests.get(f"{BACKEND_URL}/events")
    
    if response.status_code != 200 or not response.json():
        print(f"❌ Could not get events. Status code: {response.status_code}")
        return False
    
    events = response.json()
    event_id_to_book = events[0]["id"]
    
    # Get organization of the event
    event_organization = events[0]["organization"]
    
    # Get promoters for this organization
    response = requests.get(f"{BACKEND_URL}/organizations/{event_organization}/promoters", headers=client_headers)
    
    if response.status_code != 200:
        print(f"❌ Could not get promoters for organization. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    promoters = response.json()
    
    if not promoters:
        print("❌ No promoters found for this organization")
        return False
    
    # Use the first promoter
    selected_promoter_id = promoters[0]["id"]
    
    # Create booking with specific promoter
    booking_payload = {
        "event_id": event_id_to_book,
        "booking_type": "lista",
        "party_size": 3,
        "selected_promoter_id": selected_promoter_id
    }
    
    response = requests.post(f"{BACKEND_URL}/bookings", json=booking_payload, headers=client_headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Booking with specific promoter successful")
        print(f"   Booking ID: {data.get('booking_id')}")
        print(f"   Chat ID: {data.get('chat_id')}")
        print(f"   Selected promoter: {data.get('promoter_name')}")
        test_results["booking_specific_promoter"] = True
    else:
        print(f"❌ Booking with specific promoter failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["booking_specific_promoter"]

# Test organization promoters API
def test_organization_promoters_api():
    print("\n=== Testing organization promoters API ===")
    
    # Use the client token from previous test or create a new client
    if not tokens["client"]:
        test_login_admin()
        client_headers = {
            "Authorization": f"Bearer {tokens['admin']}"
        }
    else:
        client_headers = {
            "Authorization": f"Bearer {tokens['client']}"
        }
    
    # Get all organizations
    response = requests.get(f"{BACKEND_URL}/organizations")
    
    if response.status_code != 200 or not response.json():
        print(f"❌ Could not get organizations. Status code: {response.status_code}")
        return False
    
    organizations = response.json()
    
    # Use the first organization
    organization_name = organizations[0]["name"]
    
    # Get promoters for this organization
    response = requests.get(f"{BACKEND_URL}/organizations/{organization_name}/promoters", headers=client_headers)
    
    if response.status_code == 200:
        promoters = response.json()
        print(f"✅ Organization promoters API successful")
        print(f"   Organization: {organization_name}")
        print(f"   Promoters count: {len(promoters)}")
        
        # Check if promoters have the required fields
        if promoters:
            required_fields = ["id", "nome", "cognome", "username", "ruolo", "biografia"]
            has_required_fields = all(field in promoters[0] for field in required_fields)
            
            if has_required_fields:
                print(f"✅ Promoters data includes all required fields")
                test_results["organization_promoters_api"] = True
            else:
                print(f"❌ Promoters data missing some required fields")
                print(f"   Available fields: {list(promoters[0].keys())}")
        else:
            print(f"ℹ️ No promoters found for this organization")
            # Still mark as success if API works but no promoters exist
            test_results["organization_promoters_api"] = True
    else:
        print(f"❌ Organization promoters API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["organization_promoters_api"]

# Test chat get messages
def test_chat_get_messages():
    print("\n=== Testing chat get messages ===")
    
    # Use the client token and chat ID from previous test
    if not tokens["client"] or not 'chat_id' in globals():
        print("❌ Cannot test chat messages without client token and chat ID")
        return False
    
    client_headers = {
        "Authorization": f"Bearer {tokens['client']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/chats/{chat_id}/messages", headers=client_headers)
    
    if response.status_code == 200:
        messages = response.json()
        print(f"✅ Get chat messages successful")
        print(f"   Messages count: {len(messages)}")
        
        # Check if there's at least one message (the automatic booking message)
        if messages:
            print(f"✅ Chat has initial automatic message")
            test_results["chat_get_messages"] = True
        else:
            print(f"❌ Chat has no initial message")
    else:
        print(f"❌ Get chat messages failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["chat_get_messages"]

# Test chat send message
def test_chat_send_message():
    print("\n=== Testing chat send message ===")
    
    # Use the client token and chat ID from previous test
    if not tokens["client"] or not 'chat_id' in globals():
        print("❌ Cannot test sending chat message without client token and chat ID")
        return False
    
    client_headers = {
        "Authorization": f"Bearer {tokens['client']}"
    }
    
    # Send a message
    message_text = f"Test message {random_string()}"
    message_payload = {
        "chat_id": chat_id,
        "sender_id": "",  # Will be filled from token
        "sender_role": "",  # Will be filled from token
        "message": message_text
    }
    
    response = requests.post(f"{BACKEND_URL}/chats/{chat_id}/messages", json=message_payload, headers=client_headers)
    
    if response.status_code == 200:
        print(f"✅ Send message successful")
        
        # Verify the message was sent by getting messages
        response = requests.get(f"{BACKEND_URL}/chats/{chat_id}/messages", headers=client_headers)
        
        if response.status_code == 200:
            messages = response.json()
            
            # Check if our message is in the list
            message_found = any(message["message"] == message_text for message in messages)
            
            if message_found:
                print(f"✅ Message found in chat history")
                test_results["chat_send_message"] = True
            else:
                print(f"❌ Message not found in chat history")
        else:
            print(f"❌ Could not verify message was sent. Status code: {response.status_code}")
    else:
        print(f"❌ Send message failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["chat_send_message"]

# Test clubly founder dashboard
def test_dashboard_clubly_founder():
    print("\n=== Testing clubly founder dashboard ===")
    
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
        print(f"   Organizations count: {len(data.get('organizations', []))}")
        print(f"   Events count: {len(data.get('events', []))}")
        print(f"   Capo promoters count: {len(data.get('users', {}).get('capo_promoter', []))}")
        print(f"   Promoters count: {len(data.get('users', {}).get('promoter', []))}")
        test_results["dashboard_clubly_founder"] = True
    else:
        print(f"❌ Clubly founder dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_clubly_founder"]

# Test capo promoter dashboard
def test_dashboard_capo_promoter():
    print("\n=== Testing capo promoter dashboard ===")
    
    if not tokens["capo_promoter"]:
        test_login_capo_promoter()
    
    if not tokens["capo_promoter"]:
        print("❌ Cannot test capo promoter dashboard without capo_promoter token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/dashboard/capo-promoter", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Capo promoter dashboard API successful")
        print(f"   Organization: {data.get('organization')}")
        print(f"   Events count: {len(data.get('events', []))}")
        print(f"   Members count: {len(data.get('members', []))}")
        print(f"   Can edit events: {data.get('can_edit_events')}")
        print(f"   Can create promoters: {data.get('can_create_promoters')}")
        test_results["dashboard_capo_promoter"] = True
    else:
        print(f"❌ Capo promoter dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_capo_promoter"]

# Test promoter dashboard
def test_dashboard_promoter():
    print("\n=== Testing promoter dashboard ===")
    
    if not tokens["promoter"]:
        test_login_promoter()
    
    if not tokens["promoter"]:
        print("❌ Cannot test promoter dashboard without promoter token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['promoter']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/dashboard/promoter", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Promoter dashboard API successful")
        print(f"   Organization: {data.get('organization')}")
        print(f"   Events count: {len(data.get('events', []))}")
        print(f"   Members count: {len(data.get('members', []))}")
        test_results["dashboard_promoter"] = True
    else:
        print(f"❌ Promoter dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_promoter"]

# Run all tests
def run_all_tests():
    print("\n=== Running all backend API tests for Clubly ===\n")
    
    # Authentication tests
    test_login_admin()
    test_login_capo_promoter()
    test_login_promoter()
    test_login_error_handling()
    test_login_needs_password_change()
    
    # Organization tests
    test_organization_promoters_api()
    
    # Booking tests
    test_booking_auto_promoter_assignment()
    test_booking_specific_promoter()
    
    # Chat tests
    test_chat_get_messages()
    test_chat_send_message()
    
    # Dashboard tests
    test_dashboard_clubly_founder()
    test_dashboard_capo_promoter()
    test_dashboard_promoter()
    
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
