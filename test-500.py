import requests

# Test a non-existent URL or trigger a known 500 error
res = requests.post('http://127.0.0.1:8000/api/v1/auth/reset-password', json={'token': 'invalid_token', 'new_password': 'test'})
print("Status:", res.status_code)
print("Headers:", res.headers)
print("Body:", res.text)
