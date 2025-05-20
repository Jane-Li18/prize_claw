import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

# Print the values
print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_ANON_KEY: {SUPABASE_ANON_KEY}")
