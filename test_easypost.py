import easypost

easypost.api_key = "EASYPOST_API_KEY"

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
