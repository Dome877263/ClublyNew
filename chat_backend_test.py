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
    "login_admin": False,
    "login_capo_promoter": False,
    "login_promoter": False,
    "get_user_chats": False,
    "get_chat_messages": False,
    "send_chat_message": False,
    "get_notifications": False,
    "dashboard_clubly_founder": False,
    "dashboard_capo_promoter": False,
    "dashboard_promoter": False
}

# Store tokens for different user roles
tokens = {
    "admin": None,
    "capo_promoter": None,
    "promoter": None,
    "client": None
}

# Store chat IDs for testing
chat_ids = []

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
        test_results["login_admin"] = True
    else:
        print(f"❌ Login failed with admin. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["login_admin"]

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
        test_results["login_capo_promoter"] = True
    else:
        print(f"❌ Login failed with capo_promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["login_capo_promoter"]

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
        test_results["login_promoter"] = True
    else:
        print(f"❌ Login failed with promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["login_promoter"]

# Test creating a client account
def create_client_account():
    print("\n=== Creating a client account for testing ===")
    
    # Generate random user data
    username = f"test_client_{random_string()}"
    email = f"{username}@test.com"
    
    payload = {
        "nome": "Test",
        "cognome": "Client",
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
        tokens["client"] = data.get("token")
        print(f"✅ Client registration successful. Username: {username}")
        return True
    else:
        print(f"❌ Client registration failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

# Test creating a booking to generate a chat
def create_booking_for_chat():
    print("\n=== Creating a booking to generate a chat ===")
    
    if not tokens["client"]:
        print("❌ Cannot create booking without client token")
        return None
    
    headers = {
        "Authorization": f"Bearer {tokens['client']}"
    }
    
    # Get an event to book
    response = requests.get(f"{BACKEND_URL}/events")
    
    if response.status_code != 200 or not response.json():
        print(f"❌ Could not get events. Status code: {response.status_code}")
        return None
    
    events = response.json()
    event_id_to_book = events[0]["id"]
    
    # Create booking with automatic promoter assignment
    booking_payload = {
        "event_id": event_id_to_book,
        "booking_type": "lista",
        "party_size": 4,
        "selected_promoter_id": None  # Auto-assign
    }
    
    response = requests.post(f"{BACKEND_URL}/bookings", json=booking_payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        chat_id = data.get("chat_id")
        print(f"✅ Booking created successfully. Chat ID: {chat_id}")
        return chat_id
    else:
        print(f"❌ Booking creation failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

# Test getting user chats
def test_get_user_chats():
    print("\n=== Testing GET /api/user/chats ===")
    
    # Test with different user roles
    for role in ["client", "promoter", "capo_promoter", "admin"]:
        if not tokens[role]:
            continue
        
        headers = {
            "Authorization": f"Bearer {tokens[role]}"
        }
        
        response = requests.get(f"{BACKEND_URL}/user/chats", headers=headers)
        
        if response.status_code == 200:
            chats = response.json()
            print(f"✅ Get user chats successful for {role}. Chats count: {len(chats)}")
            
            # Store chat IDs for later tests
            if chats:
                for chat in chats:
                    if chat["id"] not in chat_ids:
                        chat_ids.append(chat["id"])
                
                # Print details of the first chat
                first_chat = chats[0]
                print(f"   First chat details:")
                print(f"   - Chat ID: {first_chat.get('id')}")
                print(f"   - Event: {first_chat.get('event', {}).get('name')}")
                print(f"   - Other participant: {first_chat.get('other_participant', {}).get('username')}")
                
                if "last_message" in first_chat and first_chat["last_message"]:
                    print(f"   - Last message: {first_chat['last_message'].get('message')[:50]}...")
            
            test_results["get_user_chats"] = True
        else:
            print(f"❌ Get user chats failed for {role}. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    return test_results["get_user_chats"]

# Test getting chat messages
def test_get_chat_messages():
    print("\n=== Testing GET /api/chats/{chat_id}/messages ===")
    
    if not chat_ids:
        print("❌ No chat IDs available for testing")
        return False
    
    # Test with different user roles
    success = False
    for role in ["client", "promoter", "capo_promoter", "admin"]:
        if not tokens[role]:
            continue
        
        headers = {
            "Authorization": f"Bearer {tokens[role]}"
        }
        
        # Try each chat ID until one works
        for chat_id in chat_ids:
            response = requests.get(f"{BACKEND_URL}/chats/{chat_id}/messages", headers=headers)
            
            if response.status_code == 200:
                messages = response.json()
                print(f"✅ Get chat messages successful for {role} with chat ID {chat_id}. Messages count: {len(messages)}")
                
                # Print details of the first message if available
                if messages:
                    first_message = messages[0]
                    print(f"   First message details:")
                    print(f"   - Message ID: {first_message.get('id')}")
                    print(f"   - Sender role: {first_message.get('sender_role')}")
                    print(f"   - Message: {first_message.get('message')[:50]}...")
                    print(f"   - Timestamp: {first_message.get('timestamp')}")
                
                success = True
                break
        
        if success:
            break
    
    test_results["get_chat_messages"] = success
    return success

# Test sending a chat message
def test_send_chat_message():
    print("\n=== Testing POST /api/chats/{chat_id}/messages ===")
    
    if not chat_ids:
        print("❌ No chat IDs available for testing")
        return False
    
    # Test with different user roles
    success = False
    for role in ["client", "promoter", "capo_promoter"]:
        if not tokens[role]:
            continue
        
        headers = {
            "Authorization": f"Bearer {tokens[role]}"
        }
        
        # Try each chat ID until one works
        for chat_id in chat_ids:
            message_payload = {
                "chat_id": chat_id,
                "sender_id": "",  # Will be filled from token
                "sender_role": "",  # Will be filled from token
                "message": f"Test message from {role} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            response = requests.post(f"{BACKEND_URL}/chats/{chat_id}/messages", json=message_payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Send message successful for {role} with chat ID {chat_id}")
                print(f"   Message ID: {data.get('message_id')}")
                
                success = True
                break
        
        if success:
            break
    
    test_results["send_chat_message"] = success
    return success

# Test getting notifications
def test_get_notifications():
    print("\n=== Testing GET /api/user/notifications ===")
    
    # Test with different user roles
    for role in ["client", "promoter", "capo_promoter", "admin"]:
        if not tokens[role]:
            continue
        
        headers = {
            "Authorization": f"Bearer {tokens[role]}"
        }
        
        response = requests.get(f"{BACKEND_URL}/user/notifications", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get notifications successful for {role}")
            print(f"   Notification count: {data.get('notification_count')}")
            
            test_results["get_notifications"] = True
            return True
        else:
            print(f"❌ Get notifications failed for {role}. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    return False

# Test clubly founder dashboard
def test_dashboard_clubly_founder():
    print("\n=== Testing clubly founder dashboard API ===")
    
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
        print(f"   Clients count: {data.get('users', {}).get('cliente', 0)}")
        
        test_results["dashboard_clubly_founder"] = True
    else:
        print(f"❌ Clubly founder dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_clubly_founder"]

# Test capo promoter dashboard
def test_dashboard_capo_promoter():
    print("\n=== Testing capo promoter dashboard API ===")
    
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
        print(f"   Chats count: {len(data.get('chats', []))}")
        print(f"   Can edit events: {data.get('can_edit_events')}")
        print(f"   Can create promoters: {data.get('can_create_promoters')}")
        
        test_results["dashboard_capo_promoter"] = True
    else:
        print(f"❌ Capo promoter dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_capo_promoter"]

# Test promoter dashboard
def test_dashboard_promoter():
    print("\n=== Testing promoter dashboard API ===")
    
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
        print(f"   Chats count: {len(data.get('chats', []))}")
        
        test_results["dashboard_promoter"] = True
    else:
        print(f"❌ Promoter dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_promoter"]

# Run all tests
def run_all_tests():
    print("\n=== Running all backend API tests for Clubly chat system ===\n")
    
    # Login tests
    test_login_admin()
    test_login_capo_promoter()
    test_login_promoter()
    
    # Create a client account for testing
    create_client_account()
    
    # Create a booking to generate a chat
    new_chat_id = create_booking_for_chat()
    if new_chat_id:
        chat_ids.append(new_chat_id)
    
    # Chat tests
    test_get_user_chats()
    test_get_chat_messages()
    test_send_chat_message()
    
    # Notification tests
    test_get_notifications()
    
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
