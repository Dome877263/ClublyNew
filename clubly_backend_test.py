import requests
import json
import base64
import os
import time
import random
import string
from datetime import datetime, timedelta

# Backend URL from the review request
BACKEND_URL = "https://86371f8e-929c-484d-b4db-cf725ee6a471.preview.emergentagent.com/api"

# Test results
test_results = {
    # Login tests
    "login_admin": False,
    "login_capo_promoter": False,
    "login_promoter": False,
    "login_needs_password_change": False,
    
    # Dashboard tests
    "dashboard_clubly_founder": False,
    "dashboard_capo_promoter": False,
    "dashboard_promoter": False,
    
    # Event tests
    "event_creation": False,
    "event_modification": False,
    "event_date_validation": False,
    "event_poster_update": False,
    "event_deletion": False,
    
    # Organization tests
    "organization_management": False,
    "organization_capo_promoter_assignment": False,
    "organization_available_capo_promoters": False,
    
    # Booking tests
    "booking_with_auto_assignment": False,
    "booking_with_specific_promoter": False,
    
    # Notification tests
    "notification_count": False,
    
    # Temporary credentials tests
    "temporary_credentials_creation": False,
    "password_change": False,
    
    # Chat tests
    "chat_system": False
}

# Store tokens for different user roles
tokens = {
    "admin": None,
    "capo_promoter": None,
    "promoter": None,
    "temp_user": None
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
        print(f"   needs_password_change flag: {data['user'].get('needs_password_change', False)}")
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
        print(f"   needs_password_change flag: {data['user'].get('needs_password_change', False)}")
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
        print(f"   needs_password_change flag: {data['user'].get('needs_password_change', False)}")
        test_results["login_promoter"] = True
    else:
        print(f"❌ Login failed with promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["login_promoter"]

# Test login with needs_password_change flag
def test_login_needs_password_change():
    print("\n=== Testing login with needs_password_change flag ===")
    
    # First, create a temporary user with needs_password_change=True
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test needs_password_change without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Create temporary credentials
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
    
    # Login with temporary credentials
    login_payload = {
        "login": temp_email,
        "password": temp_password
    }
    
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
    
    if login_response.status_code == 200:
        data = login_response.json()
        tokens["temp_user"] = data.get("token")
        
        # Check if needs_password_change flag is present and true
        if data["user"].get("needs_password_change") == True:
            print(f"✅ Login response includes needs_password_change=True")
            
            # Now test changing the password
            change_password_payload = {
                "current_password": temp_password,
                "new_password": "NewPassword123"
            }
            
            change_headers = {
                "Authorization": f"Bearer {tokens['temp_user']}"
            }
            
            change_response = requests.post(f"{BACKEND_URL}/auth/change-password", json=change_password_payload, headers=change_headers)
            
            if change_response.status_code == 200:
                print(f"✅ Password change successful")
                
                # Login again to check if needs_password_change is now false
                login_payload = {
                    "login": temp_email,
                    "password": "NewPassword123"
                }
                
                login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    if data["user"].get("needs_password_change") == False:
                        print(f"✅ After password change, needs_password_change=False")
                        test_results["login_needs_password_change"] = True
                    else:
                        print(f"❌ After password change, needs_password_change is still True")
                else:
                    print(f"❌ Login after password change failed. Status code: {login_response.status_code}")
            else:
                print(f"❌ Password change failed. Status code: {change_response.status_code}")
                print(f"Response: {change_response.text}")
        else:
            print(f"❌ Login response does not include needs_password_change=True")
    else:
        print(f"❌ Login with temporary credentials failed. Status code: {login_response.status_code}")
        print(f"Response: {login_response.text}")
    
    return test_results["login_needs_password_change"]

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

# Test capo promoter dashboard API
def test_dashboard_capo_promoter():
    print("\n=== Testing capo promoter dashboard API ===")
    
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
        print(f"   Events: {len(data.get('events', []))}")
        print(f"   Members: {len(data.get('members', []))}")
        print(f"   Can edit events: {data.get('can_edit_events')}")
        print(f"   Can create promoters: {data.get('can_create_promoters')}")
        test_results["dashboard_capo_promoter"] = True
    else:
        print(f"❌ Capo promoter dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_capo_promoter"]

# Test promoter dashboard API
def test_dashboard_promoter():
    print("\n=== Testing promoter dashboard API ===")
    
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
        print(f"   Events: {len(data.get('events', []))}")
        print(f"   Members: {len(data.get('members', []))}")
        test_results["dashboard_promoter"] = True
    else:
        print(f"❌ Promoter dashboard API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["dashboard_promoter"]

# Test event creation
def test_event_creation():
    print("\n=== Testing event creation ===")
    
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test event creation without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
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
        "organization": "Night Events Milano",
        "end_time": "04:00",
        "lineup": ["DJ Test", "DJ Sample"],
        "guests": ["VIP Guest"],
        "total_tables": 10,
        "tables_available": 10,
        "max_party_size": 8,
        "event_poster": create_fake_base64_image()
    }
    
    response = requests.post(f"{BACKEND_URL}/events", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Event creation successful. Event ID: {data.get('event_id')}")
        
        # Store event ID for later tests
        global event_id
        event_id = data.get('event_id')
        
        test_results["event_creation"] = True
    else:
        print(f"❌ Event creation failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["event_creation"]

# Test event date validation
def test_event_date_validation():
    print("\n=== Testing event date validation (past dates) ===")
    
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test event date validation without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Generate a random event name
    event_name = f"Past Event {random_string()}"
    
    # Get yesterday's date
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    payload = {
        "name": event_name,
        "date": yesterday,
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
    
    response = requests.post(f"{BACKEND_URL}/events", json=payload, headers=headers)
    
    # Should fail with 400 Bad Request
    if response.status_code == 400:
        print(f"✅ Event creation with past date correctly rejected with 400 Bad Request")
        print(f"   Error message: {response.json().get('detail')}")
        test_results["event_date_validation"] = True
    else:
        print(f"❌ Event creation with past date not properly validated. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["event_date_validation"]

# Test event modification
def test_event_modification():
    print("\n=== Testing event modification ===")
    
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test event modification without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # First, get all events to find one to modify
    response = requests.get(f"{BACKEND_URL}/events", headers=headers)
    
    if response.status_code != 200 or not response.json():
        print(f"❌ Could not get events. Status code: {response.status_code}")
        return False
    
    events = response.json()
    
    # Use the first event or the one created in the previous test
    if 'event_id' in globals():
        event_id_to_modify = event_id
    else:
        event_id_to_modify = events[0]["id"]
    
    # Update event details
    updated_name = f"Updated Event {random_string()}"
    updated_lineup = ["DJ Updated", "DJ Modified"]
    
    payload = {
        "name": updated_name,
        "lineup": updated_lineup,
        "start_time": "23:00",
        "end_time": "05:00",
        "guests": ["Updated VIP Guest"],
        "event_poster": create_fake_base64_image()
    }
    
    response = requests.put(f"{BACKEND_URL}/events/{event_id_to_modify}/full-update", json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Event modification successful")
        
        # Verify the update by getting the event details
        response = requests.get(f"{BACKEND_URL}/events/{event_id_to_modify}", headers=headers)
        if response.status_code == 200:
            updated_event = response.json()
            
            name_updated = updated_event["name"] == updated_name
            lineup_updated = updated_event["lineup"] == updated_lineup
            
            print(f"   Name updated: {'Yes' if name_updated else 'No'}")
            print(f"   Lineup updated: {'Yes' if lineup_updated else 'No'}")
            
            test_results["event_modification"] = name_updated and lineup_updated
        else:
            print(f"❌ Could not verify event update. Status code: {response.status_code}")
    else:
        print(f"❌ Event modification failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["event_modification"]

# Test event poster update
def test_event_poster_update():
    print("\n=== Testing event poster update ===")
    
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test event poster update without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # First, get all events to find one to modify
    response = requests.get(f"{BACKEND_URL}/events", headers=headers)
    
    if response.status_code != 200 or not response.json():
        print(f"❌ Could not get events. Status code: {response.status_code}")
        return False
    
    events = response.json()
    
    # Use the first event or the one created in the previous test
    if 'event_id' in globals():
        event_id_to_modify = event_id
    else:
        event_id_to_modify = events[0]["id"]
    
    # Update event poster
    payload = {
        "event_poster": create_fake_base64_image()
    }
    
    response = requests.put(f"{BACKEND_URL}/events/{event_id_to_modify}/poster", json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Event poster update successful")
        
        # Verify the update by getting the event details
        response = requests.get(f"{BACKEND_URL}/events/{event_id_to_modify}", headers=headers)
        if response.status_code == 200:
            updated_event = response.json()
            
            poster_updated = updated_event.get("event_poster") is not None
            
            print(f"   Poster updated: {'Yes' if poster_updated else 'No'}")
            
            test_results["event_poster_update"] = poster_updated
        else:
            print(f"❌ Could not verify event poster update. Status code: {response.status_code}")
    else:
        print(f"❌ Event poster update failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["event_poster_update"]

# Test event deletion
def test_event_deletion():
    print("\n=== Testing event deletion ===")
    
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test event deletion without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # First, create an event to delete
    event_name = f"Event to Delete {random_string()}"
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    create_payload = {
        "name": event_name,
        "date": tomorrow,
        "start_time": "22:00",
        "location": "Delete Test Club, Milano",
        "organization": "Night Events Milano",
        "end_time": "04:00",
        "lineup": ["DJ Delete", "DJ Remove"],
        "guests": ["Delete VIP Guest"],
        "total_tables": 5,
        "tables_available": 5,
        "max_party_size": 6
    }
    
    create_response = requests.post(f"{BACKEND_URL}/events", json=create_payload, headers=headers)
    
    if create_response.status_code != 200:
        print(f"❌ Could not create event for deletion test. Status code: {create_response.status_code}")
        return False
    
    event_id_to_delete = create_response.json().get("event_id")
    
    # Now delete the event
    response = requests.delete(f"{BACKEND_URL}/events/{event_id_to_delete}", headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Event deletion successful")
        
        # Verify the deletion by trying to get the event details
        response = requests.get(f"{BACKEND_URL}/events/{event_id_to_delete}", headers=headers)
        if response.status_code == 404:
            print(f"✅ Event successfully deleted (404 Not Found)")
            test_results["event_deletion"] = True
        else:
            print(f"❌ Event not properly deleted. Status code: {response.status_code}")
    else:
        print(f"❌ Event deletion failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["event_deletion"]

# Test organization management
def test_organization_management():
    print("\n=== Testing organization management ===")
    
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test organization management without admin token")
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
        get_orgs_success = True
    else:
        print(f"❌ Get organizations failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        get_orgs_success = False
    
    # Test 2: Create a new organization
    print("Test 2: Create a new organization")
    org_name = f"Test Organization {random_string()}"
    
    create_payload = {
        "name": org_name,
        "location": "Test City"
    }
    
    response = requests.post(f"{BACKEND_URL}/organizations", json=create_payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Create organization successful. Organization ID: {data.get('organization_id')}")
        
        # Store organization ID for later tests
        global org_id
        org_id = data.get('organization_id')
        
        create_org_success = True
    else:
        print(f"❌ Create organization failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        create_org_success = False
    
    # Overall success if both tests passed
    test_results["organization_management"] = get_orgs_success and create_org_success
    
    return test_results["organization_management"]

# Test organization capo promoter assignment
def test_organization_capo_promoter_assignment():
    print("\n=== Testing organization capo promoter assignment ===")
    
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test organization capo promoter assignment without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # First, get available capo promoters
    response = requests.get(f"{BACKEND_URL}/organizations/available-capo-promoters", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Could not get available capo promoters. Status code: {response.status_code}")
        return False
    
    capo_promoters = response.json()
    
    if not capo_promoters:
        print("ℹ️ No available capo promoters found. Creating a temporary capo promoter...")
        
        # Create a temporary capo promoter
        temp_email = f"capo_{random_string()}@test.com"
        
        create_payload = {
            "nome": "Temporary Capo",
            "email": temp_email,
            "password": "TempPassword123",
            "ruolo": "capo_promoter",
            "organization": ""  # No organization yet
        }
        
        response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=create_payload, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Could not create temporary capo promoter. Status code: {response.status_code}")
            return False
        
        # Get available capo promoters again
        response = requests.get(f"{BACKEND_URL}/organizations/available-capo-promoters", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Could not get available capo promoters after creation. Status code: {response.status_code}")
            return False
        
        capo_promoters = response.json()
        
        if not capo_promoters:
            print("❌ Still no available capo promoters found after creation")
            return False
    
    # Use the first available capo promoter
    capo_promoter_id = capo_promoters[0]["id"]
    
    # Get an organization to assign the capo promoter to
    if 'org_id' in globals():
        org_id_to_update = org_id
    else:
        # Get all organizations
        response = requests.get(f"{BACKEND_URL}/organizations", headers=headers)
        
        if response.status_code != 200 or not response.json():
            print(f"❌ Could not get organizations. Status code: {response.status_code}")
            return False
        
        organizations = response.json()
        org_id_to_update = organizations[0]["id"]
    
    # Assign capo promoter to organization
    update_payload = {
        "capo_promoter_id": capo_promoter_id
    }
    
    response = requests.put(f"{BACKEND_URL}/organizations/{org_id_to_update}/assign-capo-promoter", json=update_payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Capo promoter assignment successful")
        test_results["organization_capo_promoter_assignment"] = True
    else:
        print(f"❌ Capo promoter assignment failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["organization_capo_promoter_assignment"]

# Test available capo promoters API
def test_organization_available_capo_promoters():
    print("\n=== Testing available capo promoters API ===")
    
    if not tokens["admin"]:
        test_login_admin()
    
    if not tokens["admin"]:
        print("❌ Cannot test available capo promoters API without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/organizations/available-capo-promoters", headers=headers)
    
    if response.status_code == 200:
        capo_promoters = response.json()
        print(f"✅ Available capo promoters API successful. Capo promoters count: {len(capo_promoters)}")
        test_results["organization_available_capo_promoters"] = True
    else:
        print(f"❌ Available capo promoters API failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["organization_available_capo_promoters"]

# Test booking with automatic promoter assignment
def test_booking_with_auto_assignment():
    print("\n=== Testing booking with automatic promoter assignment ===")
    
    # First, create a client account or use an existing one
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
        test_results["booking_with_auto_assignment"] = True
    else:
        print(f"❌ Booking with auto-assignment failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["booking_with_auto_assignment"]

# Test booking with specific promoter selection
def test_booking_with_specific_promoter():
    print("\n=== Testing booking with specific promoter selection ===")
    
    # First, create a client account or use an existing one
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
    
    # Get organization of the event
    event_organization = events[0]["organization"]
    
    # Get promoters for this organization
    response = requests.get(f"{BACKEND_URL}/organizations/{event_organization}/promoters", headers=client_headers)
    
    if response.status_code != 200 or not response.json():
        print(f"❌ Could not get promoters for organization. Status code: {response.status_code}")
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
        test_results["booking_with_specific_promoter"] = True
    else:
        print(f"❌ Booking with specific promoter failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["booking_with_specific_promoter"]

# Test notification count API
def test_notification_count():
    print("\n=== Testing notification count API ===")
    
    # Test with different user roles
    
    # 1. Test with admin
    if not tokens["admin"]:
        test_login_admin()
    
    if tokens["admin"]:
        admin_headers = {
            "Authorization": f"Bearer {tokens['admin']}"
        }
        
        response = requests.get(f"{BACKEND_URL}/user/notifications/count", headers=admin_headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Notification count API successful for admin")
            print(f"   Unread count: {data.get('unread_count')}")
            admin_success = True
        else:
            print(f"❌ Notification count API failed for admin. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            admin_success = False
    else:
        admin_success = False
    
    # 2. Test with capo_promoter
    if not tokens["capo_promoter"]:
        test_login_capo_promoter()
    
    if tokens["capo_promoter"]:
        capo_headers = {
            "Authorization": f"Bearer {tokens['capo_promoter']}"
        }
        
        response = requests.get(f"{BACKEND_URL}/user/notifications/count", headers=capo_headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Notification count API successful for capo_promoter")
            print(f"   Unread count: {data.get('unread_count')}")
            capo_success = True
        else:
            print(f"❌ Notification count API failed for capo_promoter. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            capo_success = False
    else:
        capo_success = False
    
    # Overall success if at least one test passed
    test_results["notification_count"] = admin_success or capo_success
    
    return test_results["notification_count"]

# Test temporary credentials creation
def test_temporary_credentials_creation():
    print("\n=== Testing temporary credentials creation ===")
    
    # Test with both admin and capo_promoter
    
    # 1. Test with admin (clubly_founder)
    if not tokens["admin"]:
        test_login_admin()
    
    if tokens["admin"]:
        admin_headers = {
            "Authorization": f"Bearer {tokens['admin']}"
        }
        
        # Create temporary promoter
        temp_email = f"temp_promoter_{random_string()}@test.com"
        
        admin_payload = {
            "nome": "Temp",
            "email": temp_email,
            "password": "TempPassword123",
            "ruolo": "promoter",
            "organization": "Night Events Milano"
        }
        
        response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=admin_payload, headers=admin_headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Temporary credentials creation successful for admin")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Organization: {data.get('organization')}")
            admin_success = True
        else:
            print(f"❌ Temporary credentials creation failed for admin. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            admin_success = False
    else:
        admin_success = False
    
    # 2. Test with capo_promoter
    if not tokens["capo_promoter"]:
        test_login_capo_promoter()
    
    if tokens["capo_promoter"]:
        capo_headers = {
            "Authorization": f"Bearer {tokens['capo_promoter']}"
        }
        
        # Get capo promoter's organization
        response = requests.get(f"{BACKEND_URL}/dashboard/capo-promoter", headers=capo_headers)
        if response.status_code != 200:
            print(f"❌ Could not get capo promoter dashboard. Status code: {response.status_code}")
            capo_success = False
        else:
            dashboard_data = response.json()
            organization = dashboard_data.get("organization")
            
            # Create temporary promoter for capo's organization
            temp_email = f"temp_promoter_{random_string()}@test.com"
            
            capo_payload = {
                "nome": "Temp",
                "email": temp_email,
                "password": "TempPassword123",
                "ruolo": "promoter",
                "organization": organization
            }
            
            response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=capo_payload, headers=capo_headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Temporary credentials creation successful for capo_promoter")
                print(f"   User ID: {data.get('user_id')}")
                print(f"   Email: {data.get('email')}")
                print(f"   Organization: {data.get('organization')}")
                capo_success = True
            else:
                print(f"❌ Temporary credentials creation failed for capo_promoter. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                capo_success = False
    else:
        capo_success = False
    
    # Overall success if both tests passed
    test_results["temporary_credentials_creation"] = admin_success and capo_success
    
    return test_results["temporary_credentials_creation"]

# Test password change
def test_password_change():
    print("\n=== Testing password change API ===")
    
    # Create a new user to test password change
    username = f"pwd_user_{random_string()}"
    email = f"{username}@test.com"
    initial_password = "InitialPassword123"
    
    register_payload = {
        "nome": "Password",
        "cognome": "Test",
        "email": email,
        "username": username,
        "password": initial_password,
        "data_nascita": "1990-01-01",
        "citta": "Test City",
        "ruolo": "cliente"
    }
    
    register_response = requests.post(f"{BACKEND_URL}/auth/register", json=register_payload)
    
    if register_response.status_code != 200:
        print(f"❌ Could not register user for password change test. Status code: {register_response.status_code}")
        return False
    
    user_token = register_response.json().get("token")
    
    headers = {
        "Authorization": f"Bearer {user_token}"
    }
    
    # Change password
    new_password = "NewPassword456"
    
    change_payload = {
        "current_password": initial_password,
        "new_password": new_password
    }
    
    response = requests.post(f"{BACKEND_URL}/user/change-password", json=change_payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Password change successful")
        
        # Try to login with new password
        login_payload = {
            "login": email,
            "password": new_password
        }
        
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
        
        if login_response.status_code == 200:
            print(f"✅ Login with new password successful")
            test_results["password_change"] = True
        else:
            print(f"❌ Login with new password failed. Status code: {login_response.status_code}")
            print(f"Response: {login_response.text}")
    else:
        print(f"❌ Password change failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["password_change"]

# Test chat system
def test_chat_system():
    print("\n=== Testing chat system ===")
    
    # First, create a booking to get a chat
    
    # Create a client account
    client_email = f"chat_client_{random_string()}@test.com"
    client_password = "ClientPassword123"
    
    register_payload = {
        "nome": "Chat",
        "cognome": "Client",
        "email": client_email,
        "username": f"chat_client_{random_string()}",
        "password": client_password,
        "data_nascita": "1990-01-01",
        "citta": "Test City",
        "ruolo": "cliente"
    }
    
    register_response = requests.post(f"{BACKEND_URL}/auth/register", json=register_payload)
    
    if register_response.status_code != 200:
        print(f"❌ Could not register client for chat test. Status code: {register_response.status_code}")
        return False
    
    client_token = register_response.json().get("token")
    
    client_headers = {
        "Authorization": f"Bearer {client_token}"
    }
    
    # Get an event to book
    response = requests.get(f"{BACKEND_URL}/events")
    
    if response.status_code != 200 or not response.json():
        print(f"❌ Could not get events for chat test. Status code: {response.status_code}")
        return False
    
    events = response.json()
    event_id_to_book = events[0]["id"]
    
    # Create booking to get a chat
    booking_payload = {
        "event_id": event_id_to_book,
        "booking_type": "lista",
        "party_size": 2,
        "selected_promoter_id": None  # Auto-assign
    }
    
    booking_response = requests.post(f"{BACKEND_URL}/bookings", json=booking_payload, headers=client_headers)
    
    if booking_response.status_code != 200:
        print(f"❌ Could not create booking for chat test. Status code: {booking_response.status_code}")
        return False
    
    booking_data = booking_response.json()
    chat_id = booking_data.get("chat_id")
    
    # Test 1: Get user chats
    print("Test 1: Get user chats")
    response = requests.get(f"{BACKEND_URL}/user/chats", headers=client_headers)
    
    if response.status_code == 200:
        chats = response.json()
        print(f"✅ Get user chats successful. Chats count: {len(chats)}")
        get_chats_success = len(chats) > 0
    else:
        print(f"❌ Get user chats failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        get_chats_success = False
    
    # Test 2: Get chat messages
    print("Test 2: Get chat messages")
    response = requests.get(f"{BACKEND_URL}/chats/{chat_id}/messages", headers=client_headers)
    
    if response.status_code == 200:
        messages = response.json()
        print(f"✅ Get chat messages successful. Messages count: {len(messages)}")
        get_messages_success = True
    else:
        print(f"❌ Get chat messages failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        get_messages_success = False
    
    # Test 3: Send a message
    print("Test 3: Send a message")
    message_payload = {
        "chat_id": chat_id,
        "sender_id": "",  # Will be filled from token
        "sender_role": "",  # Will be filled from token
        "message": f"Test message {random_string()}"
    }
    
    response = requests.post(f"{BACKEND_URL}/chats/{chat_id}/messages", json=message_payload, headers=client_headers)
    
    if response.status_code == 200:
        print(f"✅ Send message successful")
        send_message_success = True
    else:
        print(f"❌ Send message failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        send_message_success = False
    
    # Overall success if all tests passed
    test_results["chat_system"] = get_chats_success and get_messages_success and send_message_success
    
    return test_results["chat_system"]

# Run all tests
def run_all_tests():
    print("\n=== Running all backend API tests ===\n")
    
    # Login tests
    test_login_admin()
    test_login_capo_promoter()
    test_login_promoter()
    test_login_needs_password_change()
    
    # Dashboard tests
    test_dashboard_clubly_founder()
    test_dashboard_capo_promoter()
    test_dashboard_promoter()
    
    # Event tests
    test_event_creation()
    test_event_date_validation()
    test_event_modification()
    test_event_poster_update()
    test_event_deletion()
    
    # Organization tests
    test_organization_management()
    test_organization_available_capo_promoters()
    test_organization_capo_promoter_assignment()
    
    # Booking tests
    test_booking_with_auto_assignment()
    test_booking_with_specific_promoter()
    
    # Notification tests
    test_notification_count()
    
    # Temporary credentials and password tests
    test_temporary_credentials_creation()
    test_password_change()
    
    # Chat tests
    test_chat_system()
    
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
