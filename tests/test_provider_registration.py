# test_provider_registration.py
from app.provider_agent import register_provider

def main():
    provider_data = register_provider()
    if provider_data:
        print("Registration successful:", provider_data)
    else:
        print("Registration failed.")

if __name__ == "__main__":
    main()
