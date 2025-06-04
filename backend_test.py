import requests
import json
import base64
import os
import time
import random
import string

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://fa498a36-0d1e-4a17-8617-8d653e8d39bb.preview.emergentagent.com/api"

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
    "complete_user_setup": False
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
