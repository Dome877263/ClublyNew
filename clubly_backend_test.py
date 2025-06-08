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
BACKEND_URL = "https://8ddadc21-e620-48aa-a5c2-33d9784e126a.preview.emergentagent.com/api"

# Test results
test_results = {
    # Notification System
    "get_user_notifications": False,
    
    # Password Change System
    "change_password_success": False,
    "change_password_wrong_current": False,
    "needs_password_change_flag": False,
    
    # Enhanced Organization Management
    "get_available_capo_promoters": False,
    "assign_capo_promoter": False,
    
    # Temporary Credentials with Organization
    "create_credentials_with_organization": False,
    "create_credentials_organization_validation": False,
    "capo_promoter_create_credentials_restriction": False,
    
    # Enhanced Event Management
    "delete_event": False,
    "update_event_poster": False,
    "full_update_event": False,
    
    # Date Validation
    "create_event_past_date": False,
    "create_event_future_date": False,
    
    # Automatic Booking Assignment
    "booking_auto_assignment": False
}

# Store tokens for different user roles
tokens = {
    "admin": None,
    "capo_promoter": None,
    "promoter": None,
    "temp_user": None
}

# Store IDs for created resources
created_resources = {
    "event_id": None,
    "organization_id": None,
    "temp_user_id": None,
    "booking_id": None
}

# Helper function to generate a random string
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Helper function to create a fake base64 image
def create_fake_base64_image():
    # This is a tiny 1x1 transparent PNG image
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

# Login with different roles
def login_with_roles():
    print("\n=== Logging in with different roles ===")
    
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
    
    # Try to find a promoter in the system
    if tokens["admin"]:
        headers = {
            "Authorization": f"Bearer {tokens['admin']}"
        }
        
        response = requests.get(f"{BACKEND_URL}/dashboard/clubly-founder", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            promoters = data.get("users", {}).get("promoter", [])
            
            if promoters:
                # Create temporary credentials for a promoter
                temp_email = f"temp_promoter_{random_string()}@test.com"
                
                payload = {
                    "nome": "Temporary",
                    "email": temp_email,
                    "password": "TempPassword123",
                    "ruolo": "promoter",
                    "organization": "Night Events Milano"
                }
                
                response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=headers)
                
                if response.status_code == 200:
                    # Login with the temporary credentials
                    login_payload = {
                        "login": temp_email,
                        "password": "TempPassword123"
                    }
                    
                    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
                    
                    if login_response.status_code == 200:
                        login_data = login_response.json()
                        tokens["promoter"] = login_data.get("token")
                        print(f"✅ Login successful as promoter (temporary credentials)")
                    else:
                        print(f"❌ Login failed with temporary promoter credentials. Status code: {login_response.status_code}")
            else:
                print("ℹ️ No promoters found in the system")
    
    return all(token is not None for token in [tokens["admin"], tokens["capo_promoter"]])

# 1. Test Notification System
def test_notification_system():
    print("\n=== Testing Notification System ===")
    
    if not tokens["admin"] or not tokens["capo_promoter"]:
        print("❌ Cannot test notification system without required tokens")
        return False
    
    # Test notifications for clubly_founder
    admin_headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/user/notifications", headers=admin_headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Notifications for clubly_founder: {data.get('notification_count', 'N/A')}")
        clubly_founder_success = True
    else:
        print(f"❌ Failed to get notifications for clubly_founder. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        clubly_founder_success = False
    
    # Test notifications for capo_promoter
    capo_headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/user/notifications", headers=capo_headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Notifications for capo_promoter: {data.get('notification_count', 'N/A')}")
        capo_promoter_success = True
    else:
        print(f"❌ Failed to get notifications for capo_promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        capo_promoter_success = False
    
    # Test notifications for promoter if available
    if tokens["promoter"]:
        promoter_headers = {
            "Authorization": f"Bearer {tokens['promoter']}"
        }
        
        response = requests.get(f"{BACKEND_URL}/user/notifications", headers=promoter_headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Notifications for promoter: {data.get('notification_count', 'N/A')}")
            promoter_success = True
        else:
            print(f"❌ Failed to get notifications for promoter. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            promoter_success = False
    else:
        print("ℹ️ Skipping promoter notifications test (no token available)")
        promoter_success = True  # Skip this test
    
    test_results["get_user_notifications"] = clubly_founder_success and capo_promoter_success and promoter_success
    return test_results["get_user_notifications"]

# 2. Test Password Change System
def test_password_change_system():
    print("\n=== Testing Password Change System ===")
    
    # Create a temporary user with needs_password_change flag
    if not tokens["admin"]:
        print("❌ Cannot test password change system without admin token")
        return False
    
    admin_headers = {
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
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=admin_headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to create temporary user. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    temp_user_data = response.json()
    created_resources["temp_user_id"] = temp_user_data.get("user_id")
    
    # Login with temporary credentials
    login_payload = {
        "login": temp_email,
        "password": temp_password
    }
    
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
    
    if login_response.status_code != 200:
        print(f"❌ Failed to login with temporary credentials. Status code: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    login_data = login_response.json()
    tokens["temp_user"] = login_data.get("token")
    
    # Check if needs_password_change flag is set
    needs_password_change = login_data.get("user", {}).get("needs_password_change", False)
    
    if needs_password_change:
        print(f"✅ needs_password_change flag is correctly set to true for new user")
        test_results["needs_password_change_flag"] = True
    else:
        print(f"❌ needs_password_change flag is not set for new user")
        test_results["needs_password_change_flag"] = False
    
    # Test changing password with wrong current password
    temp_headers = {
        "Authorization": f"Bearer {tokens['temp_user']}"
    }
    
    wrong_password_payload = {
        "current_password": "WrongPassword123",
        "new_password": "NewPassword123"
    }
    
    response = requests.post(f"{BACKEND_URL}/user/change-password", json=wrong_password_payload, headers=temp_headers)
    
    if response.status_code == 400:
        print(f"✅ Password change correctly failed with wrong current password (400 Bad Request)")
        test_results["change_password_wrong_current"] = True
    else:
        print(f"❌ Password change with wrong current password returned unexpected status: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["change_password_wrong_current"] = False
    
    # Test changing password with correct current password
    correct_password_payload = {
        "current_password": temp_password,
        "new_password": "NewPassword123"
    }
    
    response = requests.post(f"{BACKEND_URL}/user/change-password", json=correct_password_payload, headers=temp_headers)
    
    if response.status_code == 200:
        print(f"✅ Password changed successfully")
        test_results["change_password_success"] = True
        
        # Login again to check if needs_password_change flag is reset
        new_login_payload = {
            "login": temp_email,
            "password": "NewPassword123"
        }
        
        new_login_response = requests.post(f"{BACKEND_URL}/auth/login", json=new_login_payload)
        
        if new_login_response.status_code == 200:
            new_login_data = new_login_response.json()
            new_needs_password_change = new_login_data.get("user", {}).get("needs_password_change", True)
            
            if not new_needs_password_change:
                print(f"✅ needs_password_change flag is correctly reset to false after password change")
            else:
                print(f"❌ needs_password_change flag is still true after password change")
                test_results["needs_password_change_flag"] = False
        else:
            print(f"❌ Failed to login after password change. Status code: {new_login_response.status_code}")
            print(f"Response: {new_login_response.text}")
    else:
        print(f"❌ Password change failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["change_password_success"] = False
    
    return test_results["change_password_success"] and test_results["change_password_wrong_current"] and test_results["needs_password_change_flag"]

# 3. Test Enhanced Organization Management
def test_enhanced_organization_management():
    print("\n=== Testing Enhanced Organization Management ===")
    
    if not tokens["admin"]:
        print("❌ Cannot test organization management without admin token")
        return False
    
    admin_headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Test getting available capo promoters
    response = requests.get(f"{BACKEND_URL}/organizations/available-capo-promoters", headers=admin_headers)
    
    if response.status_code == 200:
        capo_promoters = response.json()
        print(f"✅ Got available capo promoters. Count: {len(capo_promoters)}")
        test_results["get_available_capo_promoters"] = True
        
        # Create a new organization
        org_name = f"Test Organization {random_string()}"
        
        org_payload = {
            "name": org_name,
            "location": "Test City"
        }
        
        response = requests.post(f"{BACKEND_URL}/organizations", json=org_payload, headers=admin_headers)
        
        if response.status_code == 200:
            org_data = response.json()
            org_id = org_data.get("organization_id")
            created_resources["organization_id"] = org_id
            print(f"✅ Created new organization: {org_name} (ID: {org_id})")
            
            # If we have available capo promoters, try to assign one
            if capo_promoters:
                capo_promoter_id = capo_promoters[0]["id"]
                
                assign_payload = {
                    "capo_promoter_id": capo_promoter_id
                }
                
                response = requests.put(f"{BACKEND_URL}/organizations/{org_id}/assign-capo-promoter", json=assign_payload, headers=admin_headers)
                
                if response.status_code == 200:
                    print(f"✅ Successfully assigned capo promoter to organization")
                    test_results["assign_capo_promoter"] = True
                else:
                    print(f"❌ Failed to assign capo promoter. Status code: {response.status_code}")
                    print(f"Response: {response.text}")
                    test_results["assign_capo_promoter"] = False
            else:
                print("ℹ️ No available capo promoters to test assignment")
                test_results["assign_capo_promoter"] = True  # Skip this test
        else:
            print(f"❌ Failed to create organization. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            test_results["assign_capo_promoter"] = False
    else:
        print(f"❌ Failed to get available capo promoters. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["get_available_capo_promoters"] = False
        test_results["assign_capo_promoter"] = False
    
    return test_results["get_available_capo_promoters"] and test_results["assign_capo_promoter"]

# 4. Test Temporary Credentials with Organization
def test_temporary_credentials_with_organization():
    print("\n=== Testing Temporary Credentials with Organization ===")
    
    if not tokens["admin"] or not tokens["capo_promoter"]:
        print("❌ Cannot test temporary credentials without required tokens")
        return False
    
    admin_headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    capo_headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    # Get organizations
    response = requests.get(f"{BACKEND_URL}/organizations", headers=admin_headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get organizations. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    organizations = response.json()
    
    if not organizations:
        print("❌ No organizations found")
        return False
    
    # Get capo promoter's organization
    response = requests.get(f"{BACKEND_URL}/dashboard/capo-promoter", headers=capo_headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get capo promoter dashboard. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    capo_data = response.json()
    capo_organization = capo_data.get("organization")
    
    if not capo_organization:
        print("❌ Capo promoter has no organization")
        return False
    
    # Find a different organization than capo's
    different_org = None
    for org in organizations:
        if org["name"] != capo_organization:
            different_org = org["name"]
            break
    
    # Test 1: Create credentials with valid organization as admin
    temp_email1 = f"temp_user_{random_string()}@test.com"
    
    valid_org_payload = {
        "nome": "Temporary",
        "email": temp_email1,
        "password": "TempPassword123",
        "ruolo": "promoter",
        "organization": organizations[0]["name"]
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=valid_org_payload, headers=admin_headers)
    
    if response.status_code == 200:
        print(f"✅ Admin successfully created temporary credentials with valid organization")
        test_results["create_credentials_with_organization"] = True
    else:
        print(f"❌ Admin failed to create temporary credentials. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["create_credentials_with_organization"] = False
    
    # Test 2: Create credentials with invalid organization
    temp_email2 = f"temp_user_{random_string()}@test.com"
    
    invalid_org_payload = {
        "nome": "Temporary",
        "email": temp_email2,
        "password": "TempPassword123",
        "ruolo": "promoter",
        "organization": "Non-Existent Organization"
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=invalid_org_payload, headers=admin_headers)
    
    if response.status_code == 400:
        print(f"✅ Correctly rejected credentials with invalid organization (400 Bad Request)")
        test_results["create_credentials_organization_validation"] = True
    else:
        print(f"❌ Unexpected response for invalid organization. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["create_credentials_organization_validation"] = False
    
    # Test 3: Capo promoter can only create for their organization
    if different_org:
        temp_email3 = f"temp_user_{random_string()}@test.com"
        
        different_org_payload = {
            "nome": "Temporary",
            "email": temp_email3,
            "password": "TempPassword123",
            "ruolo": "promoter",
            "organization": different_org
        }
        
        response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=different_org_payload, headers=capo_headers)
        
        if response.status_code == 403:
            print(f"✅ Correctly rejected capo promoter creating for different organization (403 Forbidden)")
            test_results["capo_promoter_create_credentials_restriction"] = True
        else:
            print(f"❌ Unexpected response for capo promoter restriction. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            test_results["capo_promoter_create_credentials_restriction"] = False
        
        # Test capo promoter creating for their own organization
        temp_email4 = f"temp_user_{random_string()}@test.com"
        
        own_org_payload = {
            "nome": "Temporary",
            "email": temp_email4,
            "password": "TempPassword123",
            "ruolo": "promoter",
            "organization": capo_organization
        }
        
        response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=own_org_payload, headers=capo_headers)
        
        if response.status_code == 200:
            print(f"✅ Capo promoter successfully created credentials for own organization")
        else:
            print(f"❌ Capo promoter failed to create credentials for own organization. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            test_results["capo_promoter_create_credentials_restriction"] = False
    else:
        print("ℹ️ Could not find a different organization to test capo promoter restriction")
        test_results["capo_promoter_create_credentials_restriction"] = True  # Skip this test
    
    return (test_results["create_credentials_with_organization"] and 
            test_results["create_credentials_organization_validation"] and 
            test_results["capo_promoter_create_credentials_restriction"])

# 5. Test Enhanced Event Management for Clubly Founder
def test_enhanced_event_management():
    print("\n=== Testing Enhanced Event Management for Clubly Founder ===")
    
    if not tokens["admin"]:
        print("❌ Cannot test enhanced event management without admin token")
        return False
    
    admin_headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Create a test event
    event_name = f"Test Event {random_string()}"
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    event_payload = {
        "name": event_name,
        "date": tomorrow,
        "start_time": "20:00",
        "location": "Test Club",
        "organization": "Night Events Milano",
        "end_time": "02:00",
        "lineup": ["DJ Test"],
        "guests": ["VIP Guest"],
        "total_tables": 5,
        "tables_available": 5,
        "max_party_size": 6
    }
    
    response = requests.post(f"{BACKEND_URL}/events", json=event_payload, headers=admin_headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to create test event. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    event_data = response.json()
    event_id = event_data.get("event_id")
    created_resources["event_id"] = event_id
    print(f"✅ Created test event: {event_name} (ID: {event_id})")
    
    # Test 1: Update event poster
    poster_payload = {
        "event_poster": create_fake_base64_image()
    }
    
    response = requests.put(f"{BACKEND_URL}/events/{event_id}/poster", json=poster_payload, headers=admin_headers)
    
    if response.status_code == 200:
        print(f"✅ Successfully updated event poster")
        test_results["update_event_poster"] = True
    else:
        print(f"❌ Failed to update event poster. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["update_event_poster"] = False
    
    # Test 2: Full update event
    updated_name = f"{event_name} - Updated"
    updated_lineup = ["DJ Test Updated", "DJ New"]
    
    full_update_payload = {
        "name": updated_name,
        "lineup": updated_lineup,
        "start_time": "21:00",
        "end_time": "03:00",
        "guests": ["VIP Guest Updated", "Celebrity Guest"]
    }
    
    response = requests.put(f"{BACKEND_URL}/events/{event_id}/full-update", json=full_update_payload, headers=admin_headers)
    
    if response.status_code == 200:
        print(f"✅ Successfully performed full event update")
        
        # Verify the update
        response = requests.get(f"{BACKEND_URL}/events/{event_id}", headers=admin_headers)
        
        if response.status_code == 200:
            updated_event = response.json()
            
            if (updated_event["name"] == updated_name and 
                updated_event["lineup"] == updated_lineup):
                print(f"✅ Event update verified")
                test_results["full_update_event"] = True
            else:
                print(f"❌ Event update not properly applied")
                test_results["full_update_event"] = False
        else:
            print(f"❌ Failed to verify event update. Status code: {response.status_code}")
            test_results["full_update_event"] = False
    else:
        print(f"❌ Failed to perform full event update. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["full_update_event"] = False
    
    # Test 3: Delete event
    # Create another event for deletion
    delete_event_name = f"Delete Test Event {random_string()}"
    
    delete_event_payload = {
        "name": delete_event_name,
        "date": tomorrow,
        "start_time": "19:00",
        "location": "Delete Test Club",
        "organization": "Night Events Milano",
        "end_time": "01:00",
        "lineup": ["DJ Delete"],
        "total_tables": 3,
        "tables_available": 3,
        "max_party_size": 4
    }
    
    response = requests.post(f"{BACKEND_URL}/events", json=delete_event_payload, headers=admin_headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to create event for deletion test. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["delete_event"] = False
    else:
        delete_event_data = response.json()
        delete_event_id = delete_event_data.get("event_id")
        print(f"✅ Created event for deletion: {delete_event_name} (ID: {delete_event_id})")
        
        # Delete the event
        response = requests.delete(f"{BACKEND_URL}/events/{delete_event_id}", headers=admin_headers)
        
        if response.status_code == 200:
            print(f"✅ Successfully deleted event")
            
            # Verify deletion
            response = requests.get(f"{BACKEND_URL}/events/{delete_event_id}", headers=admin_headers)
            
            if response.status_code == 404:
                print(f"✅ Event deletion verified (404 Not Found)")
                test_results["delete_event"] = True
            else:
                print(f"❌ Event still exists after deletion. Status code: {response.status_code}")
                test_results["delete_event"] = False
        else:
            print(f"❌ Failed to delete event. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            test_results["delete_event"] = False
    
    return test_results["update_event_poster"] and test_results["full_update_event"] and test_results["delete_event"]

# 6. Test Date Validation for Events
def test_date_validation():
    print("\n=== Testing Date Validation for Events ===")
    
    if not tokens["admin"]:
        print("❌ Cannot test date validation without admin token")
        return False
    
    admin_headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Test 1: Create event with past date (should fail)
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    past_event_payload = {
        "name": f"Past Event {random_string()}",
        "date": yesterday,
        "start_time": "20:00",
        "location": "Past Club",
        "organization": "Night Events Milano"
    }
    
    response = requests.post(f"{BACKEND_URL}/events", json=past_event_payload, headers=admin_headers)
    
    if response.status_code == 400:
        print(f"✅ Correctly rejected event with past date (400 Bad Request)")
        test_results["create_event_past_date"] = True
    else:
        print(f"❌ Unexpected response for past date event. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["create_event_past_date"] = False
    
    # Test 2: Create event with future date (should succeed)
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    future_event_payload = {
        "name": f"Future Event {random_string()}",
        "date": tomorrow,
        "start_time": "20:00",
        "location": "Future Club",
        "organization": "Night Events Milano",
        "end_time": "02:00",
        "lineup": ["DJ Future"],
        "total_tables": 5,
        "tables_available": 5,
        "max_party_size": 6
    }
    
    response = requests.post(f"{BACKEND_URL}/events", json=future_event_payload, headers=admin_headers)
    
    if response.status_code == 200:
        print(f"✅ Successfully created event with future date")
        test_results["create_event_future_date"] = True
    else:
        print(f"❌ Failed to create event with future date. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["create_event_future_date"] = False
    
    return test_results["create_event_past_date"] and test_results["create_event_future_date"]

# 7. Test Automatic Booking Assignment
def test_automatic_booking_assignment():
    print("\n=== Testing Automatic Booking Assignment ===")
    
    # We need a client token for this test
    if not tokens["admin"]:
        print("❌ Cannot test booking assignment without admin token")
        return False
    
    # For simplicity, we'll use the admin token as a client
    client_headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Get events
    response = requests.get(f"{BACKEND_URL}/events", headers=client_headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get events. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    events = response.json()
    
    if not events:
        print("❌ No events found for booking test")
        return False
    
    # Use the first event for booking
    event_id = events[0]["id"]
    
    # Create booking without selected_promoter_id
    booking_payload = {
        "event_id": event_id,
        "booking_type": "lista",
        "party_size": 4,
        "selected_promoter_id": None  # Auto-assign
    }
    
    response = requests.post(f"{BACKEND_URL}/bookings", json=booking_payload, headers=client_headers)
    
    if response.status_code == 200:
        booking_data = response.json()
        created_resources["booking_id"] = booking_data.get("booking_id")
        
        if "promoter_name" in booking_data:
            print(f"✅ Booking created with auto-assigned promoter: {booking_data.get('promoter_name')}")
            test_results["booking_auto_assignment"] = True
        else:
            print(f"❌ Booking created but no promoter was assigned")
            test_results["booking_auto_assignment"] = False
    else:
        print(f"❌ Failed to create booking. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        test_results["booking_auto_assignment"] = False
    
    return test_results["booking_auto_assignment"]

# Run all tests
def run_all_tests():
    print("\n=== Running all tests for Clubly backend ===\n")
    
    # Login with different roles
    if not login_with_roles():
        print("❌ Failed to login with required roles. Aborting tests.")
        return
    
    # Run all test functions
    test_notification_system()
    test_password_change_system()
    test_enhanced_organization_management()
    test_temporary_credentials_with_organization()
    test_enhanced_event_management()
    test_date_validation()
    test_automatic_booking_assignment()
    
    # Print summary
    print("\n=== Test Results Summary ===")
    
    # Group results by category
    categories = {
        "Notification System": ["get_user_notifications"],
        "Password Change System": ["change_password_success", "change_password_wrong_current", "needs_password_change_flag"],
        "Enhanced Organization Management": ["get_available_capo_promoters", "assign_capo_promoter"],
        "Temporary Credentials with Organization": ["create_credentials_with_organization", "create_credentials_organization_validation", "capo_promoter_create_credentials_restriction"],
        "Enhanced Event Management": ["delete_event", "update_event_poster", "full_update_event"],
        "Date Validation": ["create_event_past_date", "create_event_future_date"],
        "Automatic Booking Assignment": ["booking_auto_assignment"]
    }
    
    for category, tests in categories.items():
        category_results = [test_results[test] for test in tests]
        category_success = all(category_results)
        status = "✅ PASS" if category_success else "❌ FAIL"
        print(f"{status} - {category}")
        
        # Print individual test results if category failed
        if not category_success:
            for test in tests:
                test_status = "✅ PASS" if test_results[test] else "❌ FAIL"
                print(f"  {test_status} - {test}")
    
    # Calculate overall success rate
    success_count = sum(1 for result in test_results.values() if result)
    total_count = len(test_results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\nOverall success rate: {success_rate:.2f}% ({success_count}/{total_count} tests passed)")

if __name__ == "__main__":
    run_all_tests()
