from uuid import uuid4

def get_random_code():
  code = str(uuid4())[:8].replace('-', '').lower()
  return code
  