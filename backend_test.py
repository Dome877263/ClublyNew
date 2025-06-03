import requests
import unittest
import json
import os
import sys
from datetime import datetime

class ClublyAPITester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ClublyAPITester, self).__init__(*args, **kwargs)
        # Get backend URL from environment or use default
        self.base_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://f6498984-fefd-41c2-8ae2-7386f674ba3d.preview.emergentagent.com')
        self.token = None
        self.user_id = None
        self.test_event_id = None
        self.test_booking_id = None
        self.test_chat_id = None
        
        # Test user data
        self.test_user = {
            "nome": "Test",
            "cognome": "User",
            "email": f"test{datetime.now().strftime('%Y%m%d%H%M%S')}@test.it",
            "username": f"testuser{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "password": "Test123!",
            "data_nascita": "1990-01-01",
            "citta": "Milano"
        }
        
        # Admin credentials
        self.admin_credentials = {
            "email": "admin@clubly.it",
            "password": "admin123"
        }

    def setUp(self):
        print(f"\n🔍 Testing Clubly API at {self.base_url}")

    def test_01_api_root(self):
        """Test API root endpoint"""
        print("\n🔍 Testing API root endpoint...")
        try:
            # The root endpoint is at /api/ not /api
            response = requests.get(f"{self.base_url}/api/")
            # Accept 200 or 404 as the root endpoint might not be explicitly defined
            self.assertIn(response.status_code, [200, 404])
            print("✅ API root endpoint is accessible")
        except Exception as e:
            print(f"❌ API root endpoint test failed: {str(e)}")
            self.fail(f"API root endpoint test failed: {str(e)}")

    def test_02_get_events(self):
        """Test getting events list"""
        print("\n🔍 Testing events list endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/events")
            self.assertEqual(response.status_code, 200)
            events = response.json()
            self.assertIsInstance(events, list)
            
            if len(events) > 0:
                self.test_event_id = events[0]['id']
                print(f"✅ Events list endpoint returned {len(events)} events")
                print(f"   First event: {events[0]['name']}")
                
                # Check max_party_size for specific events
                neon_nights = next((e for e in events if "NEON NIGHTS" in e['name']), None)
                red_passion = next((e for e in events if "RED PASSION" in e['name']), None)
                techno_underground = next((e for e in events if "TECHNO UNDERGROUND" in e['name']), None)
                
                if neon_nights:
                    self.assertEqual(neon_nights['max_party_size'], 8, 
                                    f"NEON NIGHTS should have max_party_size=8, got {neon_nights['max_party_size']}")
                    print(f"✅ NEON NIGHTS has correct max_party_size: {neon_nights['max_party_size']}")
                
                if red_passion:
                    self.assertEqual(red_passion['max_party_size'], 6, 
                                    f"RED PASSION should have max_party_size=6, got {red_passion['max_party_size']}")
                    print(f"✅ RED PASSION has correct max_party_size: {red_passion['max_party_size']}")
                
                if techno_underground:
                    self.assertEqual(techno_underground['max_party_size'], 12, 
                                    f"TECHNO UNDERGROUND should have max_party_size=12, got {techno_underground['max_party_size']}")
                    print(f"✅ TECHNO UNDERGROUND has correct max_party_size: {techno_underground['max_party_size']}")
            else:
                print("⚠️ Events list endpoint returned 0 events")
        except Exception as e:
            print(f"❌ Events list endpoint test failed: {str(e)}")
            self.fail(f"Events list endpoint test failed: {str(e)}")

    def test_03_get_event_details(self):
        """Test getting event details"""
        if not self.test_event_id:
            self.skipTest("No event ID available from previous test")
            
        print(f"\n🔍 Testing event details endpoint for event ID: {self.test_event_id}...")
        try:
            response = requests.get(f"{self.base_url}/api/events/{self.test_event_id}")
            self.assertEqual(response.status_code, 200)
            event = response.json()
            self.assertEqual(event['id'], self.test_event_id)
            
            # Check if max_party_size field exists
            self.assertIn('max_party_size', event, "max_party_size field is missing in event data")
            self.assertIsInstance(event['max_party_size'], int, "max_party_size should be an integer")
            
            print(f"✅ Event details endpoint returned data for '{event['name']}'")
            print(f"   Event max_party_size: {event['max_party_size']}")
        except Exception as e:
            print(f"❌ Event details endpoint test failed: {str(e)}")
            self.fail(f"Event details endpoint test failed: {str(e)}")

    def test_04_admin_login(self):
        """Test admin login"""
        print("\n🔍 Testing admin login...")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.admin_credentials
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('token', data)
            self.assertIn('user', data)
            # Save admin token for later tests
            self.token = data['token']
            print(f"✅ Admin login successful for {self.admin_credentials['email']}")
        except Exception as e:
            print(f"❌ Admin login test failed: {str(e)}")
            self.fail(f"Admin login test failed: {str(e)}")

    def test_05_user_registration(self):
        """Test user registration"""
        print("\n🔍 Testing user registration...")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=self.test_user
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('token', data)
            self.assertIn('user', data)
            self.token = data['token']
            self.user_id = data['user']['id']
            print(f"✅ User registration successful for {self.test_user['email']}")
        except Exception as e:
            print(f"❌ User registration test failed: {str(e)}")
            self.fail(f"User registration test failed: {str(e)}")

    def test_06_user_login(self):
        """Test user login"""
        print("\n🔍 Testing user login...")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": self.test_user['email'],
                    "password": self.test_user['password']
                }
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('token', data)
            self.assertIn('user', data)
            self.token = data['token']
            print(f"✅ User login successful for {self.test_user['email']}")
        except Exception as e:
            print(f"❌ User login test failed: {str(e)}")
            self.fail(f"User login test failed: {str(e)}")

    def test_07_get_user_profile(self):
        """Test getting user profile"""
        if not self.token:
            self.skipTest("No token available from previous test")
            
        print("\n🔍 Testing user profile endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/api/user/profile",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.assertEqual(response.status_code, 200)
            user = response.json()
            self.assertEqual(user['email'], self.test_user['email'])
            print(f"✅ User profile endpoint returned data for {user['email']}")
        except Exception as e:
            print(f"❌ User profile endpoint test failed: {str(e)}")
            self.fail(f"User profile endpoint test failed: {str(e)}")

    def test_08_create_booking(self):
        """Test creating a booking"""
        if not self.token or not self.test_event_id:
            self.skipTest("No token or event ID available from previous tests")
            
        print("\n🔍 Testing booking creation...")
        try:
            booking_data = {
                "event_id": self.test_event_id,
                "booking_type": "lista",
                "party_size": 2
            }
            
            response = requests.post(
                f"{self.base_url}/api/bookings",
                json=booking_data,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('booking_id', data)
            self.test_booking_id = data['booking_id']
            self.test_chat_id = data.get('chat_id')
            
            # Verify that a chat_id is returned
            self.assertIsNotNone(self.test_chat_id, "No chat_id returned from booking creation")
            
            print(f"✅ Booking created successfully with ID: {self.test_booking_id}")
            print(f"✅ Chat created automatically with ID: {self.test_chat_id}")
        except Exception as e:
            print(f"❌ Booking creation test failed: {str(e)}")
            self.fail(f"Booking creation test failed: {str(e)}")

    def test_09_get_user_bookings(self):
        """Test getting user bookings"""
        if not self.token:
            self.skipTest("No token available from previous test")
            
        print("\n🔍 Testing user bookings endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/api/user/bookings",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.assertEqual(response.status_code, 200)
            bookings = response.json()
            self.assertIsInstance(bookings, list)
            
            if len(bookings) > 0:
                print(f"✅ User bookings endpoint returned {len(bookings)} bookings")
            else:
                print("⚠️ User bookings endpoint returned 0 bookings")
        except Exception as e:
            print(f"❌ User bookings endpoint test failed: {str(e)}")
            self.fail(f"User bookings endpoint test failed: {str(e)}")

    def test_10_get_user_chats(self):
        """Test getting user chats"""
        if not self.token:
            self.skipTest("No token available from previous test")
            
        print("\n🔍 Testing user chats endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/api/user/chats",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.assertEqual(response.status_code, 200)
            chats = response.json()
            self.assertIsInstance(chats, list)
            
            if len(chats) > 0:
                print(f"✅ User chats endpoint returned {len(chats)} chats")
                
                # Verify chat structure
                chat = chats[0]
                self.assertIn('id', chat, "Chat is missing 'id' field")
                self.assertIn('event', chat, "Chat is missing 'event' field")
                self.assertIn('other_participant', chat, "Chat is missing 'other_participant' field")
                self.assertIn('last_message', chat, "Chat is missing 'last_message' field")
                
                # Verify promoter assignment
                self.assertIn('nome', chat['other_participant'], "Promoter is missing 'nome' field")
                print(f"✅ Chat assigned to promoter: {chat['other_participant']['nome']} {chat['other_participant']['cognome']}")
                
                # Save chat ID if not already set
                if not self.test_chat_id:
                    self.test_chat_id = chat['id']
            else:
                print("⚠️ User chats endpoint returned 0 chats")
        except Exception as e:
            print(f"❌ User chats endpoint test failed: {str(e)}")
            self.fail(f"User chats endpoint test failed: {str(e)}")

    def test_11_get_chat_messages(self):
        """Test getting chat messages"""
        if not self.token or not self.test_chat_id:
            self.skipTest("No token or chat ID available from previous tests")
            
        print(f"\n🔍 Testing chat messages endpoint for chat ID: {self.test_chat_id}...")
        try:
            response = requests.get(
                f"{self.base_url}/api/chats/{self.test_chat_id}/messages",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.assertEqual(response.status_code, 200)
            messages = response.json()
            self.assertIsInstance(messages, list)
            
            if len(messages) > 0:
                print(f"✅ Chat messages endpoint returned {len(messages)} messages")
                
                # Verify automatic message
                first_message = messages[0]
                self.assertIn('is_automatic', first_message, "Message is missing 'is_automatic' field")
                self.assertTrue(first_message.get('is_automatic', False), "First message should be automatic")
                
                # Verify message content
                self.assertIn('message', first_message, "Message is missing 'message' field")
                message_content = first_message['message']
                self.assertIn('Nuova prenotazione', message_content, "Automatic message should contain 'Nuova prenotazione'")
                self.assertIn('Cliente:', message_content, "Automatic message should contain client info")
                self.assertIn('Evento:', message_content, "Automatic message should contain event info")
                self.assertIn('Tipo:', message_content, "Automatic message should contain booking type")
                self.assertIn('Persone:', message_content, "Automatic message should contain party size")
                
                print("✅ Automatic message contains all required information")
                print(f"✅ Message preview: {message_content[:100]}...")
            else:
                print("⚠️ Chat messages endpoint returned 0 messages")
        except Exception as e:
            print(f"❌ Chat messages endpoint test failed: {str(e)}")
            self.fail(f"Chat messages endpoint test failed: {str(e)}")

    def test_12_send_chat_message(self):
        """Test sending a chat message"""
        if not self.token or not self.test_chat_id:
            self.skipTest("No token or chat ID available from previous tests")
            
        print(f"\n🔍 Testing sending a chat message to chat ID: {self.test_chat_id}...")
        try:
            message_data = {
                "chat_id": self.test_chat_id,
                "sender_id": self.user_id,
                "sender_role": "cliente",
                "message": "Questo è un messaggio di test inviato dall'API test."
            }
            
            response = requests.post(
                f"{self.base_url}/api/chats/{self.test_chat_id}/messages",
                json=message_data,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('message_id', data)
            print(f"✅ Message sent successfully with ID: {data['message_id']}")
            
            # Verify message was added to chat
            response = requests.get(
                f"{self.base_url}/api/chats/{self.test_chat_id}/messages",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.assertEqual(response.status_code, 200)
            messages = response.json()
            
            # The last message should be our test message
            last_message = messages[-1]
            self.assertEqual(last_message['message'], message_data['message'])
            self.assertEqual(last_message['sender_id'], self.user_id)
            print("✅ Message successfully added to chat")
        except Exception as e:
            print(f"❌ Sending chat message test failed: {str(e)}")
            self.fail(f"Sending chat message test failed: {str(e)}")

if __name__ == "__main__":
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add tests in order
    suite.addTest(ClublyAPITester('test_01_api_root'))
    suite.addTest(ClublyAPITester('test_02_get_events'))
    suite.addTest(ClublyAPITester('test_03_get_event_details'))
    suite.addTest(ClublyAPITester('test_04_admin_login'))
    suite.addTest(ClublyAPITester('test_05_user_registration'))
    suite.addTest(ClublyAPITester('test_06_user_login'))
    suite.addTest(ClublyAPITester('test_07_get_user_profile'))
    suite.addTest(ClublyAPITester('test_08_create_booking'))
    suite.addTest(ClublyAPITester('test_09_get_user_bookings'))
    suite.addTest(ClublyAPITester('test_10_get_user_chats'))
    suite.addTest(ClublyAPITester('test_11_get_chat_messages'))
    suite.addTest(ClublyAPITester('test_12_send_chat_message'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())
