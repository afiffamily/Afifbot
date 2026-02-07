import os
from dotenv import load_dotenv

load_dotenv()

admins_env = os.getenv("ADMINS")
ADMINS = [int(id_str) for id_str in admins_env.split(",")] if admins_env else []
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")