import asyncpg
import os
from database.queries import DBCommands

class Database(DBCommands):
    def __init__(self):
        self.pool = None
        self.db_url = os.getenv("DATABASE_PUBLIC_URL")

    async def connect(self):
        if not self.db_url:
            print("❌ XATOLIK: DATABASE_PUBLIC_URL topilmadi!")
            return
        try:
            self.pool = await asyncpg.create_pool(dsn=self.db_url, ssl='require')
            print("✅ Bazaga muvaffaqiyatli ulandi!")
        except Exception as e:
            print(f"❌ Bazaga ulanishda xatolik: {e}")

    # Yordamchi funksiya (Queries ichida ishlatiladi)
    async def execute(self, sql, *args):
        if not self.pool: return
        async with self.pool.acquire() as connection:
            await connection.execute(sql, *args)

    # ================= 1. JADVALLARNI YARATISH (MIGRATSIYA) =================
    async def create_tables(self):
        if not self.pool: return
        
        print("⏳ Jadvallar tekshirilmoqda va yangilanmoqda...")

        # 1. USERS JADVALI
        await self.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")
        
        await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(255);")
        await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);")
        await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'uz';")
        await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20);")
        await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
        await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS latitude FLOAT;")
        await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS longitude FLOAT;")
        await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_address TEXT;")

        # 2. ADMINS JADVALI
        await self.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id BIGINT PRIMARY KEY,
            full_name VARCHAR(255),
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")
        await self.execute("ALTER TABLE admins ADD COLUMN IF NOT EXISTS added_by BIGINT;")

        # 3. PRODUCTS JADVALI
        await self.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            category VARCHAR(100),
            photo_id VARCHAR(255),
            price DECIMAL(12, 2),
            is_active BOOLEAN DEFAULT TRUE
        );""")
        await self.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS category VARCHAR(100);")
        await self.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS name_uz VARCHAR(255);")
        await self.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS name_ru VARCHAR(255);")
        await self.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS desc_uz TEXT;")
        await self.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS desc_ru TEXT;")

        # 4. ORDERS JADVALI
        await self.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            total_amount DECIMAL(12, 2),
            status VARCHAR(20) DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")
        await self.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS address_text TEXT;")
        await self.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_type VARCHAR(50);")

        await self.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INT,
            product_name VARCHAR(255),
            quantity INT,
            price DECIMAL(12, 2)
        );""")

        await self.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            product_id INT, 
            quantity INT,
            price DECIMAL(12, 2)
        );""")
        await self.execute("ALTER TABLE cart ADD COLUMN IF NOT EXISTS product_name VARCHAR(255);")

        await self.execute("""
        CREATE TABLE IF NOT EXISTS promotions (
            id SERIAL PRIMARY KEY,
            photo VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE
        );""")
        await self.execute("ALTER TABLE promotions ADD COLUMN IF NOT EXISTS caption_uz TEXT;")
        await self.execute("ALTER TABLE promotions ADD COLUMN IF NOT EXISTS caption_ru TEXT;")
        await self.execute("ALTER TABLE promotions ADD COLUMN IF NOT EXISTS name_uz VARCHAR(255);")
        await self.execute("ALTER TABLE promotions ADD COLUMN IF NOT EXISTS name_ru VARCHAR(255);")
        await self.execute("ALTER TABLE promotions ADD COLUMN IF NOT EXISTS price DECIMAL(12, 2) DEFAULT 0;")

        print("✅ Jadvallar to'liq yangilandi (Migratsiya yakunlandi).")