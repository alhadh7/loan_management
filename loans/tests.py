######   ignore this  ######



# import unittest
# import json
# import requests
# from datetime import datetime, timedelta

# # Base URL for the API
# BASE_URL = "http://localhost:8000"

# class LoanManagementAPITests(unittest.TestCase):
#     def setUp(self):
#         # Setup test data
#         self.admin_credentials = {
#             "username": "admin_user",
#             "password": "admin_password",
#             "email": "admin@example.com",
#             "first_name": "Admin",
#             "last_name": "User"
#         }
        
#         self.user_credentials = {
#             "username": "test_user",
#             "password": "test_password",
#             "email": "test@example.com",
#             "first_name": "Test",
#             "last_name": "User"
#         }
        
#         self.loan_data = {
#             "amount": 50000,
#             "tenure": 12,
#             "interest_rate": 10.5
#         }
        
#         # Register test users
#         self.register_test_users()
        
#         # Login and get tokens
#         self.admin_token = self.login_user(self.admin_credentials["username"], self.admin_credentials["password"])
#         self.user_token = self.login_user(self.user_credentials["username"], self.user_credentials["password"])
        
#         # Create a test loan
#         self.test_loan_id = self.create_test_loan()
    
#     def register_test_users(self):
#         """Register admin and regular test users if they don't exist"""
#         # Register admin
#         try:
#             response = requests.post(f"{BASE_URL}/auth/admin-register/", json=self.admin_credentials)
#             print(f"Admin registration: {response.status_code}, {response.json()}")
#         except Exception as e:
#             print(f"Admin registration error: {e}")
        
#         # Register regular user
#         try:
#             response = requests.post(f"{BASE_URL}/auth/register/", json=self.user_credentials)
#             print(f"User registration: {response.status_code}, {response.json()}")
            
#             # Simulate email verification (in a real test, you'd need to extract the token from the email)
#             # This is a placeholder - in reality, you'd need to handle verification properly
#             if response.status_code == 201:
#                 # Directly set user as active in the database for testing purposes
#                 # In a real scenario, you would need to extract the verification link
#                 pass
#         except Exception as e:
#             print(f"User registration error: {e}")
    
#     def login_user(self, username, password):
#         """Log in a user and return their access token"""
#         login_data = {
#             "username": username,
#             "password": password
#         }
        
#         response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
#         if response.status_code == 200:
#             return response.json()["data"]["access"]
#         return None
    
#     def create_test_loan(self):
#         """Create a test loan and return its ID"""
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         response = requests.post(f"{BASE_URL}/api/loans/", json=self.loan_data, headers=headers)
        
#         if response.status_code == 201:
#             return response.json()["data"]["loan_id"]
#         return None
    
#     def tearDown(self):
#         """Clean up after tests"""
#         # If we created a loan, delete it
#         if hasattr(self, 'test_loan_id') and self.test_loan_id:
#             headers = {"Authorization": f"Bearer {self.admin_token}"}
#             requests.delete(f"{BASE_URL}/api/loans-delete/", json={"loan_id": self.test_loan_id}, headers=headers)
    
#     # Authentication Tests
#     def test_register_user_success(self):
#         """Test successful user registration"""
#         test_user = {
#             "username": f"test_user_{datetime.now().timestamp()}",
#             "password": "test_password",
#             "email": f"test_{datetime.now().timestamp()}@example.com",
#             "first_name": "Test",
#             "last_name": "User"
#         }
        
#         response = requests.post(f"{BASE_URL}/auth/register/", json=test_user)
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.json()["status"], "success")
    
#     def test_register_user_duplicate(self):
#         """Test registration with duplicate username"""
#         response = requests.post(f"{BASE_URL}/auth/register/", json=self.user_credentials)
#         self.assertNotEqual(response.status_code, 201)
#         self.assertEqual(response.json()["status"], "error")
    
#     def test_login_success(self):
#         """Test successful login"""
#         login_data = {
#             "username": self.user_credentials["username"],
#             "password": self.user_credentials["password"]
#         }
        
#         response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()["status"], "success")
#         self.assertIn("access", response.json()["data"])
    
#     def test_login_invalid_credentials(self):
#         """Test login with invalid credentials"""
#         login_data = {
#             "username": self.user_credentials["username"],
#             "password": "wrong_password"
#         }
        
#         response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
#         self.assertEqual(response.status_code, 401)
#         self.assertEqual(response.json()["status"], "error")
    
#     # Loan Creation Tests
#     def test_create_loan_success(self):
#         """Test successful loan creation"""
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         response = requests.post(f"{BASE_URL}/api/loans/", json=self.loan_data, headers=headers)
        
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.json()["status"], "success")
#         self.assertIn("loan_id", response.json()["data"])
        
#         # Clean up - delete the created loan
#         if "loan_id" in response.json()["data"]:
#             loan_id = response.json()["data"]["loan_id"]
#             admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
#             requests.delete(f"{BASE_URL}/api/loans-delete/", json={"loan_id": loan_id}, headers=admin_headers)
    
#     def test_create_loan_invalid_amount(self):
#         """Test loan creation with invalid amount"""
#         invalid_data = self.loan_data.copy()
#         invalid_data["amount"] = 500  # Below minimum
        
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         response = requests.post(f"{BASE_URL}/api/loans/", json=invalid_data, headers=headers)
        
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()["status"], "error")
    
#     def test_create_loan_invalid_tenure(self):
#         """Test loan creation with invalid tenure"""
#         invalid_data = self.loan_data.copy()
#         invalid_data["tenure"] = 30  # Above maximum
        
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         response = requests.post(f"{BASE_URL}/api/loans/", json=invalid_data, headers=headers)
        
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()["status"], "error")
    
#     def test_create_loan_unauthorized(self):
#         """Test loan creation without authentication"""
#         response = requests.post(f"{BASE_URL}/api/loans/", json=self.loan_data)
#         self.assertEqual(response.status_code, 401)
    
#     # Loan List Tests
#     def test_get_loans_as_user(self):
#         """Test getting loans as a regular user"""
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         response = requests.get(f"{BASE_URL}/api/loans/", headers=headers)
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()["status"], "success")
#         self.assertIn("loans", response.json()["data"])
    
#     def test_get_loans_as_admin(self):
#         """Test getting all loans as an admin"""
#         headers = {"Authorization": f"Bearer {self.admin_token}"}
#         response = requests.get(f"{BASE_URL}/api/loans/", headers=headers)
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()["status"], "success")
#         self.assertIn("loans", response.json()["data"])
    
#     def test_get_loans_with_filter(self):
#         """Test getting loans with status filter"""
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         response = requests.get(f"{BASE_URL}/api/loans/?status=active", headers=headers)
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()["status"], "success")
    
#     # Loan Detail Tests
#     def test_get_loan_detail_success(self):
#         """Test getting loan details"""
#         if not self.test_loan_id:
#             self.skipTest("No test loan available")
        
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         response = requests.post(
#             f"{BASE_URL}/api/loans/detail/", 
#             json={"loan_id": self.test_loan_id}, 
#             headers=headers
#         )
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()["status"], "success")
#         self.assertEqual(response.json()["data"]["loan_id"], self.test_loan_id)
    
#     def test_get_loan_detail_not_found(self):
#         """Test getting details for a non-existent loan"""
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         response = requests.post(
#             f"{BASE_URL}/api/loans/detail/", 
#             json={"loan_id": "LOAN999"}, 
#             headers=headers
#         )
        
#         self.assertEqual(response.status_code, 404)
    
#     def test_get_loan_detail_unauthorized(self):
#         """Test getting loan details for another user's loan"""
#         if not self.test_loan_id:
#             self.skipTest("No test loan available")
        
#         # Create another user and try to access the loan
#         other_user = {
#             "username": f"other_user_{datetime.now().timestamp()}",
#             "password": "test_password",
#             "email": f"other_{datetime.now().timestamp()}@example.com",
#             "first_name": "Other",
#             "last_name": "User"
#         }
        
#         # Register and login
#         requests.post(f"{BASE_URL}/auth/register/", json=other_user)
#         other_token = self.login_user(other_user["username"], other_user["password"])
        
#         if other_token:
#             headers = {"Authorization": f"Bearer {other_token}"}
#             response = requests.post(
#                 f"{BASE_URL}/api/loans/detail/", 
#                 json={"loan_id": self.test_loan_id}, 
#                 headers=headers
#             )
            
#             self.assertEqual(response.status_code, 403)
    
#     # Loan Installment Payment Tests
#     def test_pay_installment_success(self):
#         """Test successful installment payment"""
#         if not self.test_loan_id:
#             self.skipTest("No test loan available")
        
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         payment_data = {
#             "loan_id": self.test_loan_id,
#             "installment_no": 1
#         }
        
#         response = requests.post(f"{BASE_URL}/api/loans/pay/", json=payment_data, headers=headers)
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()["status"], "success")
    
#     def test_pay_installment_already_paid(self):
#         """Test paying an already paid installment"""
#         if not self.test_loan_id:
#             self.skipTest("No test loan available")
        
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         payment_data = {
#             "loan_id": self.test_loan_id,
#             "installment_no": 1
#         }
        
#         # First payment
#         requests.post(f"{BASE_URL}/api/loans/pay/", json=payment_data, headers=headers)
        
#         # Second payment attempt for the same installment
#         response = requests.post(f"{BASE_URL}/api/loans/pay/", json=payment_data, headers=headers)
        
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()["status"], "error")
    
#     def test_pay_installment_invalid_number(self):
#         """Test paying a non-existent installment"""
#         if not self.test_loan_id:
#             self.skipTest("No test loan available")
        
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         payment_data = {
#             "loan_id": self.test_loan_id,
#             "installment_no": 999  # Invalid installment number
#         }
        
#         response = requests.post(f"{BASE_URL}/api/loans/pay/", json=payment_data, headers=headers)
        
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(response.json()["status"], "error")
    
#     # Foreclosure Tests
#     def test_foreclose_loan_success(self):
#         """Test successful loan foreclosure"""
#         if not self.test_loan_id:
#             self.skipTest("No test loan available")
        
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         response = requests.post(
#             f"{BASE_URL}/api/loans/foreclose/", 
#             json={"loan_id": self.test_loan_id}, 
#             headers=headers
#         )
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()["status"], "success")
#         self.assertEqual(response.json()["data"]["status"], "FORECLOSED")
    
#     def test_foreclose_non_active_loan(self):
#         """Test foreclosing a non-active loan"""
#         if not self.test_loan_id:
#             self.skipTest("No test loan available")
        
#         # First foreclose the loan
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         requests.post(
#             f"{BASE_URL}/api/loans/foreclose/", 
#             json={"loan_id": self.test_loan_id}, 
#             headers=headers
#         )
        
#         # Try to foreclose again
#         response = requests.post(
#             f"{BASE_URL}/api/loans/foreclose/", 
#             json={"loan_id": self.test_loan_id}, 
#             headers=headers
#         )
        
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()["status"], "error")
    
#     # Loan Deletion Tests
#     def test_delete_loan_as_admin(self):
#         """Test deleting a loan as an admin"""
#         # Create a loan to delete
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         create_response = requests.post(f"{BASE_URL}/api/loans/", json=self.loan_data, headers=headers)
        
#         if create_response.status_code != 201:
#             self.skipTest("Failed to create test loan for deletion")
        
#         loan_id = create_response.json()["data"]["loan_id"]
        
#         # Delete the loan as admin
#         admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
#         response = requests.delete(f"{BASE_URL}/api/loans-delete/", json={"loan_id": loan_id}, headers=admin_headers)
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()["status"], "success")
    
#     def test_delete_loan_as_user(self):
#         """Test deleting a loan as a regular user (should fail)"""
#         if not self.test_loan_id:
#             self.skipTest("No test loan available")
        
#         # Try to delete as regular user
#         headers = {"Authorization": f"Bearer {self.user_token}"}
#         response = requests.delete(
#             f"{BASE_URL}/api/loans-delete/", 
#             json={"loan_id": self.test_loan_id}, 
#             headers=headers
#         )
        
#         self.assertEqual(response.status_code, 403)  # Should be forbidden
    
#     def test_delete_nonexistent_loan(self):
#         """Test deleting a non-existent loan"""
#         headers = {"Authorization": f"Bearer {self.admin_token}"}
#         response = requests.delete(
#             f"{BASE_URL}/api/loans-delete/", 
#             json={"loan_id": "LOAN999"}, 
#             headers=headers
#         )
        
#         self.assertEqual(response.status_code, 404)

#     # Error handling tests
#     def test_missing_loan_id(self):
#         """Test endpoints with missing loan_id parameter"""
#         headers = {"Authorization": f"Bearer {self.user_token}"}
        
#         # Test loan detail with missing loan_id
#         response = requests.post(f"{BASE_URL}/api/loans/detail/", json={}, headers=headers)
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()["status"], "error")
        
#         # Test loan foreclosure with missing loan_id
#         response = requests.post(f"{BASE_URL}/api/loans/foreclose/", json={}, headers=headers)
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()["status"], "error")
        
#         # Test loan deletion with missing loan_id
#         admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
#         response = requests.delete(f"{BASE_URL}/api/loans-delete/", json={}, headers=admin_headers)
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()["status"], "error")
    
#     def test_expired_token(self):
#         """Test using an expired token (this is a placeholder, as we can't easily expire a token)"""
#         # In a real test, you might manipulate the token to make it expired
#         # or use a very short-lived token
#         pass

# if __name__ == "__main__":
#     unittest.main()