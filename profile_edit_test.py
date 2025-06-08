import requests
import json
import random
import string
import jwt

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://5e33d9d6-d926-4f31-98aa-cda829ab2ec0.preview.emergentagent.com/api"

# Test results
test_results = {
    "profile_edit_valid_data": False,
    "profile_edit_username_uniqueness": False,
    "profile_edit_data_returned": False,
    "profile_edit_auth_required": False,
    "user_search_basic": False,
    "user_search_with_filters": False,
    "user_search_empty": False
}

# Store tokens for different user roles
tokens = {
    "admin": None,
    "capo_promoter": None,
    "new_user1": None,
    "new_user2": None
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

# Register two new users for testing
def register_test_users():
    print("\n=== Registering test users for profile edit tests ===")
    
    # Create first test user
    username1 = f"test_user_{random_string()}"
    email1 = f"{username1}@test.com"
    
    payload1 = {
        "nome": "Test",
        "cognome": "User1",
        "email": email1,
        "username": username1,
        "password": "TestPassword123",
        "data_nascita": "1990-01-01",
        "citta": "Test City",
        "ruolo": "cliente",
        "biografia": "Test user biography",
        "profile_image": create_fake_base64_image()
    }
    
    response1 = requests.post(f"{BACKEND_URL}/auth/register", json=payload1)
    
    if response1.status_code == 200:
        data1 = response1.json()
        tokens["new_user1"] = data1.get("token")
        print(f"✅ Registration successful for first test user: {username1}")
    else:
        print(f"❌ Registration failed for first test user. Status code: {response1.status_code}")
        print(f"Response: {response1.text}")
        return False
    
    # Create second test user
    username2 = f"test_user_{random_string()}"
    email2 = f"{username2}@test.com"
    
    payload2 = {
        "nome": "Test",
        "cognome": "User2",
        "email": email2,
        "username": username2,
        "password": "TestPassword123",
        "data_nascita": "1992-02-02",
        "citta": "Another City",
        "ruolo": "cliente",
        "biografia": "Another test user biography",
        "profile_image": create_fake_base64_image()
    }
    
    response2 = requests.post(f"{BACKEND_URL}/auth/register", json=payload2)
    
    if response2.status_code == 200:
        data2 = response2.json()
        tokens["new_user2"] = data2.get("token")
        print(f"✅ Registration successful for second test user: {username2}")
        return True
    else:
        print(f"❌ Registration failed for second test user. Status code: {response2.status_code}")
        print(f"Response: {response2.text}")
        return False

# Test profile edit with valid data
def test_profile_edit_valid_data():
    print("\n=== Testing profile edit with valid data ===")
    
    if not tokens["new_user1"]:
        print("❌ Cannot test profile edit without user token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['new_user1']}"
    }
    
    # Get user ID from token
    token_data = jwt.decode(tokens["new_user1"], options={"verify_signature": False})
    user_id = token_data.get("id")
    
    # Get current user data
    response = requests.get(f"{BACKEND_URL}/user/profile", headers=headers)
    if response.status_code != 200:
        print(f"❌ Could not get current user profile. Status code: {response.status_code}")
        return False
    
    current_user = response.json()
    
    # Update profile with new data
    new_nome = f"Updated{random_string(4)}"
    new_username = f"updated_user_{random_string(4)}"
    new_biografia = f"This is an updated biography for testing purposes {random_string(8)}"
    new_citta = "Updated City"
    
    payload = {
        "nome": new_nome,
        "username": new_username,
        "biografia": new_biografia,
        "citta": new_citta
    }
    
    response = requests.put(f"{BACKEND_URL}/user/profile/edit", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Profile edit successful")
        
        # Verify the updated data
        updated_user = data.get("user", {})
        
        nome_updated = updated_user.get("nome") == new_nome
        username_updated = updated_user.get("username") == new_username
        biografia_updated = updated_user.get("biografia") == new_biografia
        citta_updated = updated_user.get("citta") == new_citta
        
        print(f"   Nome updated: {'Yes' if nome_updated else 'No'}")
        print(f"   Username updated: {'Yes' if username_updated else 'No'}")
        print(f"   Biografia updated: {'Yes' if biografia_updated else 'No'}")
        print(f"   Città updated: {'Yes' if citta_updated else 'No'}")
        
        test_results["profile_edit_valid_data"] = nome_updated and username_updated and biografia_updated and citta_updated
    else:
        print(f"❌ Profile edit failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["profile_edit_valid_data"]

# Test profile edit username uniqueness
def test_profile_edit_username_uniqueness():
    print("\n=== Testing profile edit username uniqueness ===")
    
    if not tokens["new_user1"] or not tokens["new_user2"]:
        print("❌ Cannot test username uniqueness without both user tokens")
        return False
    
    # Get user2's username
    headers2 = {
        "Authorization": f"Bearer {tokens['new_user2']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/user/profile", headers=headers2)
    if response.status_code != 200:
        print(f"❌ Could not get user2 profile. Status code: {response.status_code}")
        return False
    
    user2 = response.json()
    user2_username = user2.get("username")
    
    # Try to update user1's username to user2's username
    headers1 = {
        "Authorization": f"Bearer {tokens['new_user1']}"
    }
    
    response = requests.get(f"{BACKEND_URL}/user/profile", headers=headers1)
    if response.status_code != 200:
        print(f"❌ Could not get user1 profile. Status code: {response.status_code}")
        return False
    
    user1 = response.json()
    
    payload = {
        "nome": user1.get("nome"),
        "username": user2_username,  # Try to use user2's username
        "biografia": user1.get("biografia"),
        "citta": user1.get("citta")
    }
    
    response = requests.put(f"{BACKEND_URL}/user/profile/edit", json=payload, headers=headers1)
    
    # This should fail with a 400 Bad Request
    if response.status_code == 400:
        print(f"✅ Username uniqueness correctly enforced (400 Bad Request)")
        test_results["profile_edit_username_uniqueness"] = True
    else:
        print(f"❌ Username uniqueness test failed. Expected 400, got: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["profile_edit_username_uniqueness"]

# Test profile edit data returned
def test_profile_edit_data_returned():
    print("\n=== Testing profile edit data returned ===")
    
    if not tokens["new_user1"]:
        print("❌ Cannot test profile edit data returned without user token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['new_user1']}"
    }
    
    # Get current user data
    response = requests.get(f"{BACKEND_URL}/user/profile", headers=headers)
    if response.status_code != 200:
        print(f"❌ Could not get current user profile. Status code: {response.status_code}")
        return False
    
    current_user = response.json()
    
    # Update profile with new data
    new_nome = f"Updated{random_string(4)}"
    new_username = f"updated_user_{random_string(4)}"
    new_biografia = f"This is another updated biography {random_string(8)}"
    new_citta = "Another Updated City"
    
    payload = {
        "nome": new_nome,
        "username": new_username,
        "biografia": new_biografia,
        "citta": new_citta
    }
    
    response = requests.put(f"{BACKEND_URL}/user/profile/edit", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if the response contains the user object with all fields
        if "user" in data:
            user = data["user"]
            required_fields = ["id", "nome", "cognome", "email", "username", "ruolo", "citta", "biografia"]
            
            all_fields_present = all(field in user for field in required_fields)
            
            if all_fields_present:
                print(f"✅ Profile edit response contains all required user data")
                test_results["profile_edit_data_returned"] = True
            else:
                print(f"❌ Profile edit response missing some required fields")
                print(f"   Missing fields: {[field for field in required_fields if field not in user]}")
        else:
            print(f"❌ Profile edit response does not contain user object")
    else:
        print(f"❌ Profile edit failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["profile_edit_data_returned"]

# Test profile edit authentication required
def test_profile_edit_auth_required():
    print("\n=== Testing profile edit authentication required ===")
    
    # Try to update profile without authentication
    payload = {
        "nome": "Unauthorized User",
        "username": "unauthorized_user",
        "biografia": "This should fail",
        "citta": "Unauthorized City"
    }
    
    response = requests.put(f"{BACKEND_URL}/user/profile/edit", json=payload)
    
    # This should fail with a 401 Unauthorized or 403 Forbidden
    if response.status_code in [401, 403]:
        print(f"✅ Authentication requirement correctly enforced (Status code: {response.status_code})")
        test_results["profile_edit_auth_required"] = True
    else:
        print(f"❌ Authentication requirement test failed. Expected 401 or 403, got: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["profile_edit_auth_required"]

# Test user search basic functionality
def test_user_search_basic():
    print("\n=== Testing user search basic functionality ===")
    
    if not tokens["admin"]:
        test_login_with_username()
    
    if not tokens["admin"]:
        print("❌ Cannot test user search without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Search for "admin" user
    payload = {
        "search_term": "admin"
    }
    
    response = requests.post(f"{BACKEND_URL}/users/search", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ User search basic functionality successful. Results: {len(data)}")
            
            # Check if the results contain the admin user
            admin_found = any(user.get("username") == "admin" for user in data)
            
            if admin_found:
                print(f"   Admin user found in search results")
                test_results["user_search_basic"] = True
            else:
                print(f"❌ Admin user not found in search results")
        else:
            print(f"❌ User search returned no results or invalid data")
    else:
        print(f"❌ User search failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["user_search_basic"]

# Test user search with filters
def test_user_search_with_filters():
    print("\n=== Testing user search with filters ===")
    
    if not tokens["admin"]:
        print("❌ Cannot test user search with filters without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Test with role filter
    print("Test with role filter: promoter")
    payload = {
        "role_filter": "promoter"
    }
    
    response = requests.post(f"{BACKEND_URL}/users/search", json=payload, headers=headers)
    
    role_filter_success = False
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, list):
            print(f"✅ User search with role filter successful. Results: {len(data)}")
            
            # Check if all results have the correct role
            all_correct_role = all(user.get("ruolo") == "promoter" for user in data)
            
            if all_correct_role:
                print(f"   All users have the correct role: promoter")
                role_filter_success = True
            else:
                print(f"❌ Some users have incorrect roles")
        else:
            print(f"❌ User search returned invalid data")
    else:
        print(f"❌ User search with role filter failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test with combined filters
    print("\nTest with combined filters: role and search term")
    payload = {
        "search_term": "capo",
        "role_filter": "capo_promoter"
    }
    
    response = requests.post(f"{BACKEND_URL}/users/search", json=payload, headers=headers)
    
    combined_filter_success = False
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, list):
            print(f"✅ User search with combined filters successful. Results: {len(data)}")
            
            # Check if results contain capo_promoter with "capo" in the name/username
            valid_results = all(
                user.get("ruolo") == "capo_promoter" and 
                ("capo" in user.get("nome", "").lower() or 
                 "capo" in user.get("cognome", "").lower() or 
                 "capo" in user.get("username", "").lower())
                for user in data
            )
            
            if valid_results:
                print(f"   All users match the combined filters")
                combined_filter_success = True
            else:
                print(f"❌ Some users don't match the combined filters")
        else:
            print(f"❌ User search returned invalid data")
    else:
        print(f"❌ User search with combined filters failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    test_results["user_search_with_filters"] = role_filter_success and combined_filter_success
    return test_results["user_search_with_filters"]

# Test empty search returns all users
def test_user_search_empty():
    print("\n=== Testing empty search returns all users ===")
    
    if not tokens["admin"]:
        print("❌ Cannot test empty search without admin token")
        return False
    
    headers = {
        "Authorization": f"Bearer {tokens['admin']}"
    }
    
    # Empty search payload
    payload = {}
    
    response = requests.post(f"{BACKEND_URL}/users/search", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ Empty search successful. Results: {len(data)}")
            
            # Check if the results contain different user roles
            roles = set(user.get("ruolo") for user in data)
            
            if len(roles) > 1:
                print(f"   Search returned users with different roles: {roles}")
                test_results["user_search_empty"] = True
            else:
                print(f"❌ Search returned users with only one role: {roles}")
        else:
            print(f"❌ Empty search returned no results or invalid data")
    else:
        print(f"❌ Empty search failed. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return test_results["user_search_empty"]

# Run all tests
def run_all_tests():
    print("\n=== Running all profile edit and user search API tests ===\n")
    
    # Login tests
    test_login_with_username()
    test_login_with_capo_promoter()
    
    # Register test users
    register_test_users()
    
    # Profile edit tests
    test_profile_edit_valid_data()
    test_profile_edit_username_uniqueness()
    test_profile_edit_data_returned()
    test_profile_edit_auth_required()
    
    # User search tests
    test_user_search_basic()
    test_user_search_with_filters()
    test_user_search_empty()
    
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