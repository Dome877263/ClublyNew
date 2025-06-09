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
    # Organization Management Enhanced
    "create_organization_without_capo": False,
    "get_available_organizations": False,
    "assign_capo_promoter_to_organization": False,
    "get_available_capo_promoters": False,
    
    # Credential Creation with Organization
    "create_credentials_with_organization": False,
    "capo_promoter_create_credentials_own_org": False,
    "clubly_founder_create_credentials_any_org": False,
    
    # Password Change System
    "change_password_correct": False,
    "change_password_incorrect": False,
    "password_change_needs_flag": False,
    
    # Event Management for Clubly Founder
    "delete_event_clubly_founder": False,
    "full_update_event_clubly_founder": False,
    "update_event_poster": False,
    "validate_past_dates": False,
    
    # Notification System
    "get_notification_count": False,
    "notification_different_roles": False
}

# Store tokens for different user roles
tokens = {
    "admin": None,
    "capo_promoter": None,
    "promoter": None,
    "new_user": None,
    "temp_user": None
}

# Store IDs for created resources
created_resources = {
    "organization_id": None,
    "event_id": None,
    "temp_user_id": None
}

# Helper function to generate a random string
def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Helper function to create a fake base64 image
def create_fake_base64_image():
    # This is a tiny 1x1 transparent PNG image
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

# Login as admin (clubly founder)
def login_as_admin():
    print("\n=== Logging in as admin (clubly founder) ===")
    
    payload = {
        "login": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["admin"] = data.get("token")
        print(f"✅ Login successful as admin. User role: {data['user']['ruolo']}")
        return True
    else:
        print(f"❌ Login failed as admin. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

# Login as capo promoter
def login_as_capo_promoter():
    print("\n=== Logging in as capo promoter ===")
    
    payload = {
        "login": "capo_milano",
        "password": "Password1"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens["capo_promoter"] = data.get("token")
        print(f"✅ Login successful as capo promoter. User role: {data['user']['ruolo']}")
        return True
    else:
        print(f"❌ Login failed as capo promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

# 1. Organization Management Enhanced Tests

# Test creating organization without capo promoter field
def test_create_organization_without_capo():
    print("\n=== Testing organization creation without capo promoter ===")
    
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Generate a random organization name
    org_name = f"Test Org {random_string()}"
    
    payload = {
        "name": org_name,
        "location": "Test Location"
        # No capo_promoter_username field
    }
    
    response = requests.post(f"{BACKEND_URL}/organizations", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        created_resources["organization_id"] = data.get("organization_id")
        print(f"✅ Organization created successfully without capo promoter. ID: {created_resources['organization_id']}")
        test_results["create_organization_without_capo"] = True
    else:
        print(f"❌ Organization creation failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["create_organization_without_capo"]

# Test API for getting available organizations
def test_get_available_organizations():
    print("\n=== Testing API for getting available organizations ===")
    
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/organizations", headers=headers)
    
    if response.status_code == 200:
        organizations = response.json()
        print(f"✅ Successfully retrieved {len(organizations)} organizations")
        
        # Check if our created organization is in the list
        if created_resources["organization_id"]:
            found = any(org["id"] == created_resources["organization_id"] for org in organizations)
            if found:
                print(f"✅ Found our created organization in the list")
            else:
                print(f"⚠️ Could not find our created organization in the list")
        
        test_results["get_available_organizations"] = True
    else:
        print(f"❌ Failed to get organizations. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["get_available_organizations"]

# Test API for getting available capo promoters
def test_get_available_capo_promoters():
    print("\n=== Testing API for getting available capo promoters ===")
    
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/organizations/available-capo-promoters", headers=headers)
    
    if response.status_code == 200:
        capo_promoters = response.json()
        print(f"✅ Successfully retrieved {len(capo_promoters)} available capo promoters")
        test_results["get_available_capo_promoters"] = True
        
        # Store a capo promoter ID if available for later tests
        if capo_promoters:
            return capo_promoters[0]["id"]
    else:
        print(f"❌ Failed to get available capo promoters. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["get_available_capo_promoters"]

# Test API for assigning capo promoter to organization
def test_assign_capo_promoter_to_organization(capo_promoter_id=None):
    print("\n=== Testing API for assigning capo promoter to organization ===")
    
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    if not created_resources["organization_id"]:
        print("❌ No organization ID available for testing")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # If no capo promoter ID provided, try to get one
    if not capo_promoter_id:
        capo_promoter_id = test_get_available_capo_promoters()
        if not isinstance(capo_promoter_id, str):
            print("❌ Could not get a capo promoter ID for testing")
            return False
    
    payload = {
        "capo_promoter_id": capo_promoter_id
    }
    
    response = requests.put(
        f"{BACKEND_URL}/organizations/{created_resources['organization_id']}/assign-capo-promoter", 
        json=payload, 
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ Successfully assigned capo promoter to organization")
        test_results["assign_capo_promoter_to_organization"] = True
    else:
        print(f"❌ Failed to assign capo promoter. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["assign_capo_promoter_to_organization"]

# 2. Credential Creation with Organization Tests

# Test creating credentials with organization selection
def test_create_credentials_with_organization():
    print("\n=== Testing credential creation with organization selection ===")
    
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Generate random user data
    temp_email = f"temp_user_{random_string()}@test.com"
    
    # Get an organization name
    response = requests.get(f"{BACKEND_URL}/organizations", headers=headers)
    if response.status_code != 200 or not response.json():
        print("❌ Could not get organizations for testing")
        return False
    
    organization_name = response.json()[0]["name"]
    
    payload = {
        "nome": "Temporary",
        "email": temp_email,
        "password": "TempPassword1",
        "ruolo": "promoter",
        "organization": organization_name  # Required field
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        created_resources["temp_user_id"] = data.get("user_id")
        print(f"✅ Successfully created credentials with organization selection. User ID: {created_resources['temp_user_id']}")
        print(f"   Organization: {data.get('organization')}")
        test_results["create_credentials_with_organization"] = True
    else:
        print(f"❌ Failed to create credentials. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["create_credentials_with_organization"]

# Test that capo promoter can only create for their organization
def test_capo_promoter_create_credentials_own_org():
    print("\n=== Testing capo promoter can only create credentials for own organization ===")
    
    if not tokens["capo_promoter"]:
        if not login_as_capo_promoter():
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    # Get capo promoter's organization
    response = requests.get(f"{BACKEND_URL}/dashboard/capo-promoter", headers=headers)
    if response.status_code != 200:
        print(f"❌ Could not get capo promoter dashboard. Status code: {response.status_code}")
        return False
    
    capo_org = response.json().get("organization")
    if not capo_org:
        print("❌ Capo promoter has no organization")
        return False
    
    print(f"   Capo promoter's organization: {capo_org}")
    
    # Test 1: Create for own organization (should succeed)
    temp_email = f"temp_user_{random_string()}@test.com"
    
    payload = {
        "nome": "Temporary",
        "email": temp_email,
        "password": "TempPassword1",
        "ruolo": "promoter",
        "organization": capo_org
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=headers)
    
    own_org_success = False
    if response.status_code == 200:
        print(f"✅ Capo promoter successfully created credentials for own organization")
        own_org_success = True
    else:
        print(f"❌ Capo promoter failed to create credentials for own organization. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 2: Try to create for different organization (should fail)
    # Get a different organization
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    admin_headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/organizations", headers=admin_headers)
    if response.status_code != 200 or not response.json():
        print("❌ Could not get organizations for testing")
        return False
    
    # Find an organization different from capo's organization
    different_org = None
    for org in response.json():
        if org["name"] != capo_org:
            different_org = org["name"]
            break
    
    if not different_org:
        print("⚠️ Could not find a different organization for testing")
        # Create a new one
        org_name = f"Test Org {random_string()}"
        payload = {
            "name": org_name,
            "location": "Test Location"
        }
        response = requests.post(f"{BACKEND_URL}/organizations", json=payload, headers=admin_headers)
        if response.status_code == 200:
            different_org = org_name
        else:
            print("❌ Could not create a different organization for testing")
            return False
    
    print(f"   Different organization: {different_org}")
    
    # Switch back to capo promoter token
    headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    temp_email = f"temp_user_{random_string()}@test.com"
    
    payload = {
        "nome": "Temporary",
        "email": temp_email,
        "password": "TempPassword1",
        "ruolo": "promoter",
        "organization": different_org
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=headers)
    
    different_org_fails = False
    if response.status_code == 403:
        print(f"✅ Capo promoter correctly denied creating credentials for different organization (403 Forbidden)")
        different_org_fails = True
    else:
        print(f"❌ Capo promoter was able to create credentials for different organization. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    test_results["capo_promoter_create_credentials_own_org"] = own_org_success and different_org_fails
    
    return test_results["capo_promoter_create_credentials_own_org"]

# Test that clubly founder can create for any organization
def test_clubly_founder_create_credentials_any_org():
    print("\n=== Testing clubly founder can create credentials for any organization ===")
    
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Get all organizations
    response = requests.get(f"{BACKEND_URL}/organizations", headers=headers)
    if response.status_code != 200 or not response.json():
        print("❌ Could not get organizations for testing")
        return False
    
    organizations = response.json()
    
    # Test creating credentials for each organization
    success_count = 0
    for i, org in enumerate(organizations[:2]):  # Test with first 2 organizations
        temp_email = f"temp_user_{random_string()}@test.com"
        
        payload = {
            "nome": f"Temporary {i+1}",
            "email": temp_email,
            "password": "TempPassword1",
            "ruolo": "promoter",
            "organization": org["name"]
        }
        
        response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Clubly founder successfully created credentials for organization: {org['name']}")
            success_count += 1
        else:
            print(f"❌ Clubly founder failed to create credentials for organization: {org['name']}. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    test_results["clubly_founder_create_credentials_any_org"] = success_count > 0
    
    return test_results["clubly_founder_create_credentials_any_org"]

# 3. Password Change System Tests

# Create a temporary user with needs_password_change flag
def create_temp_user_for_password_change():
    print("\n=== Creating temporary user for password change tests ===")
    
    if not tokens["admin"]:
        if not login_as_admin():
            return None, None
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Get an organization name
    response = requests.get(f"{BACKEND_URL}/organizations", headers=headers)
    if response.status_code != 200 or not response.json():
        print("❌ Could not get organizations for testing")
        return None, None
    
    organization_name = response.json()[0]["name"]
    
    # Generate random user data
    temp_email = f"temp_pwd_{random_string()}@test.com"
    temp_password = "TempPassword1"
    
    payload = {
        "nome": "Password Test",
        "email": temp_email,
        "password": temp_password,
        "ruolo": "promoter",
        "organization": organization_name
    }
    
    response = requests.post(f"{BACKEND_URL}/users/temporary-credentials", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        user_id = data.get("user_id")
        print(f"✅ Created temporary user for password change tests. User ID: {user_id}")
        
        # Login with the temporary credentials
        login_payload = {
            "login": temp_email,
            "password": temp_password
        }
        
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            temp_token = login_data.get("token")
            
            # Verify needs_password_change flag is set
            if login_data["user"].get("needs_password_change"):
                print(f"✅ User has needs_password_change flag set to true")
                return temp_token, temp_password
            else:
                print(f"❌ User does not have needs_password_change flag set")
        else:
            print(f"❌ Could not login with temporary credentials. Status code: {login_response.status_code}")
    else:
        print(f"❌ Failed to create temporary user. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return None, None

# Test changing password with correct current password
def test_change_password_correct():
    print("\n=== Testing password change with correct current password ===")
    
    # Create a temporary user for testing
    temp_token, current_password = create_temp_user_for_password_change()
    
    if not temp_token or not current_password:
        print("❌ Could not create temporary user for testing")
        return False
    
    headers = {
        "Authorization": f"Bearer {temp_token}"
    }
    
    new_password = f"NewPassword{random_string(4)}!"
    
    payload = {
        "current_password": current_password,
        "new_password": new_password
    }
    
    response = requests.post(f"{BACKEND_URL}/user/change-password", json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Password changed successfully")
        test_results["change_password_correct"] = True
        
        # Try to login with the new password
        # Extract user info from token
        token_data = jwt.decode(temp_token, options={"verify_signature": False})
        email = token_data.get("email")
        
        if email:
            login_payload = {
                "login": email,
                "password": new_password
            }
            
            login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
            
            if login_response.status_code == 200:
                print(f"✅ Successfully logged in with new password")
                
                # Check if needs_password_change is now false
                login_data = login_response.json()
                if not login_data["user"].get("needs_password_change"):
                    print(f"✅ needs_password_change flag is now set to false")
                    test_results["password_change_needs_flag"] = True
                else:
                    print(f"❌ needs_password_change flag is still true after password change")
            else:
                print(f"❌ Could not login with new password. Status code: {login_response.status_code}")
                print(f"Response: {login_response.text}")
        else:
            print(f"❌ Could not extract email from token")
    else:
        print(f"❌ Password change failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["change_password_correct"]

# Test changing password with incorrect current password
def test_change_password_incorrect():
    print("\n=== Testing password change with incorrect current password ===")
    
    # Create a temporary user for testing
    temp_token, current_password = create_temp_user_for_password_change()
    
    if not temp_token or not current_password:
        print("❌ Could not create temporary user for testing")
        return False
    
    headers = {
        "Authorization": f"Bearer {temp_token}"
    }
    
    new_password = f"NewPassword{random_string(4)}!"
    
    payload = {
        "current_password": "WrongPassword123!",  # Incorrect password
        "new_password": new_password
    }
    
    response = requests.post(f"{BACKEND_URL}/user/change-password", json=payload, headers=headers)
    
    if response.status_code == 400:
        print(f"✅ Password change correctly rejected with incorrect current password (400 Bad Request)")
        test_results["change_password_incorrect"] = True
    else:
        print(f"❌ Unexpected response for incorrect password. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["change_password_incorrect"]

# 4. Event Management for Clubly Founder Tests

# Create an event for testing
def create_test_event():
    print("\n=== Creating test event for event management tests ===")
    
    if not tokens["admin"]:
        if not login_as_admin():
            return None
    
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
        "guests": ["Special Guest"],
        "total_tables": 10,
        "tables_available": 10,
        "max_party_size": 8,
        "image": create_fake_base64_image()
    }
    
    response = requests.post(f"{BACKEND_URL}/events", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        event_id = data.get("event_id")
        print(f"✅ Created test event for management tests. Event ID: {event_id}")
        return event_id
    else:
        print(f"❌ Failed to create test event. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

# Test full event update for clubly founder
def test_full_update_event_clubly_founder():
    print("\n=== Testing full event update for clubly founder ===")
    
    # Create a test event
    event_id = create_test_event()
    
    if not event_id:
        print("❌ Could not create test event")
        return False
    
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Update all fields
    updated_name = f"Updated Event {random_string(4)}"
    updated_lineup = ["DJ Updated", "DJ New"]
    updated_start_time = "23:30"
    updated_end_time = "05:30"
    updated_guests = ["VIP Guest", "Special Guest"]
    updated_poster = create_fake_base64_image()
    
    payload = {
        "name": updated_name,
        "lineup": updated_lineup,
        "start_time": updated_start_time,
        "end_time": updated_end_time,
        "guests": updated_guests,
        "event_poster": updated_poster
    }
    
    response = requests.put(f"{BACKEND_URL}/events/{event_id}/full-update", json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Full event update successful")
        
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
            
            test_results["full_update_event_clubly_founder"] = name_updated and lineup_updated and start_time_updated
            
            # Store event ID for later tests
            created_resources["event_id"] = event_id
        else:
            print(f"❌ Could not verify event update. Status code: {response.status_code}")
    else:
        print(f"❌ Full event update failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["full_update_event_clubly_founder"]

# Test update event poster
def test_update_event_poster():
    print("\n=== Testing event poster update ===")
    
    # Use the event created in the previous test or create a new one
    event_id = created_resources.get("event_id")
    if not event_id:
        event_id = create_test_event()
    
    if not event_id:
        print("❌ Could not get or create test event")
        return False
    
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Update poster
    poster_data = {
        "event_poster": create_fake_base64_image()
    }
    
    response = requests.put(f"{BACKEND_URL}/events/{event_id}/poster", json=poster_data, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Event poster update successful")
        test_results["update_event_poster"] = True
        
        # Verify the update by getting the event details
        response = requests.get(f"{BACKEND_URL}/events/{event_id}", headers=headers)
        if response.status_code == 200:
            updated_event = response.json()
            
            if "event_poster" in updated_event and updated_event["event_poster"]:
                print(f"✅ Event poster field is present and not empty")
            else:
                print(f"❌ Event poster field is missing or empty")
                test_results["update_event_poster"] = False
        else:
            print(f"❌ Could not verify event poster update. Status code: {response.status_code}")
    else:
        print(f"❌ Event poster update failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["update_event_poster"]

# Test validation for past dates
def test_validate_past_dates():
    print("\n=== Testing validation for past dates ===")
    
    if not tokens["admin"]:
        if not login_as_admin():
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
        "organization": "Night Events Milano"
    }
    
    response = requests.post(f"{BACKEND_URL}/events", json=payload, headers=headers)
    
    if response.status_code == 400:
        print(f"✅ Past date validation works correctly (400 Bad Request)")
        test_results["validate_past_dates"] = True
    else:
        print(f"❌ Past date validation failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["validate_past_dates"]

# Test event deletion for clubly founder
def test_delete_event_clubly_founder():
    print("\n=== Testing event deletion for clubly founder ===")
    
    # Create a test event
    event_id = create_test_event()
    
    if not event_id:
        print("❌ Could not create test event")
        return False
    
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    response = requests.delete(f"{BACKEND_URL}/events/{event_id}", headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Event deletion successful")
        
        # Verify the deletion by trying to get the event details
        response = requests.get(f"{BACKEND_URL}/events/{event_id}", headers=headers)
        if response.status_code == 404:
            print(f"✅ Event was correctly deleted (404 Not Found)")
            test_results["delete_event_clubly_founder"] = True
        else:
            print(f"❌ Event still exists after deletion. Status code: {response.status_code}")
    else:
        print(f"❌ Event deletion failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["delete_event_clubly_founder"]

# 5. Notification System Tests

# Test API for getting notification count
def test_get_notification_count():
    print("\n=== Testing API for getting notification count ===")
    
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/user/notifications/count", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully retrieved notification count: {data.get('unread_count')}")
        test_results["get_notification_count"] = True
    else:
        print(f"❌ Failed to get notification count. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["get_notification_count"]

# Test notification functionality for different roles
def test_notification_different_roles():
    print("\n=== Testing notification functionality for different roles ===")
    
    # Test for clubly founder
    if not tokens["admin"]:
        if not login_as_admin():
            return False
    
    admin_headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    admin_response = requests.get(f"{BACKEND_URL}/user/notifications/count", headers=admin_headers)
    
    admin_success = False
    if admin_response.status_code == 200:
        print(f"✅ Successfully retrieved notification count for clubly founder")
        admin_success = True
    else:
        print(f"❌ Failed to get notification count for clubly founder. Status code: {admin_response.status_code}")
    
    # Test for capo promoter
    if not tokens["capo_promoter"]:
        if not login_as_capo_promoter():
            return False
    
    capo_headers = {
        "Authorization": f"Bearer {tokens['capo_promoter']}"
    }
    
    capo_response = requests.get(f"{BACKEND_URL}/user/notifications/count", headers=capo_headers)
    
    capo_success = False
    if capo_response.status_code == 200:
        print(f"✅ Successfully retrieved notification count for capo promoter")
        capo_success = True
    else:
        print(f"❌ Failed to get notification count for capo promoter. Status code: {capo_response.status_code}")
    
    test_results["notification_different_roles"] = admin_success and capo_success
    
    return test_results["notification_different_roles"]

# Run all tests
def run_all_tests():
    print("\n=== Running all enhanced Clubly API tests ===\n")
    
    # Login first
    login_as_admin()
    login_as_capo_promoter()
    
    # 1. Organization Management Enhanced Tests
    test_create_organization_without_capo()
    test_get_available_organizations()
    capo_promoter_id = test_get_available_capo_promoters()
    if isinstance(capo_promoter_id, str):
        test_assign_capo_promoter_to_organization(capo_promoter_id)
    else:
        test_assign_capo_promoter_to_organization()
    
    # 2. Credential Creation with Organization Tests
    test_create_credentials_with_organization()
    test_capo_promoter_create_credentials_own_org()
    test_clubly_founder_create_credentials_any_org()
    
    # 3. Password Change System Tests
    test_change_password_correct()
    test_change_password_incorrect()
    
    # 4. Event Management for Clubly Founder Tests
    test_full_update_event_clubly_founder()
    test_update_event_poster()
    test_validate_past_dates()
    test_delete_event_clubly_founder()
    
    # 5. Notification System Tests
    test_get_notification_count()
    test_notification_different_roles()
    
    # Print summary
    print("\n=== Test Results Summary ===")
    
    # Group tests by category
    categories = {
        "Organization Management": [
            "create_organization_without_capo",
            "get_available_organizations",
            "assign_capo_promoter_to_organization",
            "get_available_capo_promoters"
        ],
        "Credential Creation": [
            "create_credentials_with_organization",
            "capo_promoter_create_credentials_own_org",
            "clubly_founder_create_credentials_any_org"
        ],
        "Password Change System": [
            "change_password_correct",
            "change_password_incorrect",
            "password_change_needs_flag"
        ],
        "Event Management": [
            "delete_event_clubly_founder",
            "full_update_event_clubly_founder",
            "update_event_poster",
            "validate_past_dates"
        ],
        "Notification System": [
            "get_notification_count",
            "notification_different_roles"
        ]
    }
    
    # Print results by category
    for category, tests in categories.items():
        print(f"\n{category}:")
        for test_name in tests:
            status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
            print(f"{status} - {test_name}")
    
    # Calculate overall success rate
    success_count = sum(1 for result in test_results.values() if result)
    total_count = len(test_results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\nOverall success rate: {success_rate:.2f}% ({success_count}/{total_count} tests passed)")

if __name__ == "__main__":
    run_all_tests()
