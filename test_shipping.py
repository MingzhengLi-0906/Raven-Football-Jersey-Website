import easypost

easypost.api_key = "YOUR_TEST_API_KEY"  # Replace with your real EasyPost test key

address = easypost.Address.create(
    name="Test User",
    street1="417 Montgomery St",
    city="San Francisco",
    state="CA",
    zip="94104",
    country="US",
    phone="5555555555",
    email="test@example.com"
)

print(address)
