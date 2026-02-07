import asyncpg

class DBCommands:
    # ================= 1. USER FUNKSIYALARI =================
    async def add_user(self, user_id, username, full_name, lang='uz', phone=None):
        sql = """
        INSERT INTO users (user_id, username, full_name, language, phone_number) 
        VALUES ($1, $2, $3, $4, $5) 
        ON CONFLICT (user_id) DO UPDATE 
        SET username=$2, full_name=$3, language=$4, phone_number=$5
        """
        await self.execute(sql, user_id, username, full_name, lang, phone)

    async def get_user_lang(self, user_id):
        if not self.pool: return 'uz'
        sql = "SELECT language FROM users WHERE user_id = $1"
        async with self.pool.acquire() as connection:
            return await connection.fetchval(sql, user_id)

    async def get_user_info(self, user_id):
        sql = """
        SELECT u.*, COUNT(o.id) as order_count 
        FROM users u 
        LEFT JOIN orders o ON u.user_id = o.user_id 
        WHERE u.user_id = $1 
        GROUP BY u.user_id
        """
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(sql, user_id)

    async def get_users_by_lang(self, lang):
        sql = "SELECT user_id FROM users WHERE language = $1"
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(sql, lang)
            return [row['user_id'] for row in rows]

    async def get_all_user_ids(self):
        sql = "SELECT user_id FROM users"
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(sql)
            return [row['user_id'] for row in rows]
            
    async def count_users(self):
        async with self.pool.acquire() as connection:
            return await connection.fetchval("SELECT COUNT(*) FROM users")
            
    async def get_all_users_detailed(self):
        sql = """
        SELECT user_id, full_name, username, phone_number, language, reg_date 
        FROM users 
        ORDER BY reg_date DESC
        """
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(sql)
            return rows

    # --- SOZLAMALAR ---
    async def update_user_lang(self, user_id, lang):
        await self.execute("UPDATE users SET language = $1 WHERE user_id = $2", lang, user_id)

    async def update_user_phone(self, user_id, phone):
        await self.execute("UPDATE users SET phone_number = $1 WHERE user_id = $2", phone, user_id)

    async def update_user_fullname(self, user_id, full_name):
        await self.execute("UPDATE users SET full_name = $1 WHERE user_id = $2", full_name, user_id)

    # --- LOKATSIYA VA MANZIL TARIXI ---
    async def update_user_location(self, user_id, lat, lon):
        sql = "UPDATE users SET latitude = $1, longitude = $2 WHERE user_id = $3"
        await self.execute(sql, lat, lon, user_id)

    async def get_user_last_location(self, user_id):
        sql = "SELECT latitude, longitude FROM users WHERE user_id = $1"
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(sql, user_id)
            
    async def update_user_last_address(self, user_id, address):
        await self.execute("UPDATE users SET last_address = $1 WHERE user_id = $2", address, user_id)

    async def get_user_last_address(self, user_id):
        sql = "SELECT last_address FROM users WHERE user_id = $1"
        async with self.pool.acquire() as connection:
            return await connection.fetchval(sql, user_id)


    # ================= 2. MAHSULOTLAR =================
    async def get_categories(self):
        sql = "SELECT DISTINCT category FROM products WHERE is_active = TRUE AND category IS NOT NULL"
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(sql)
            return [row['category'] for row in rows]

    async def get_products_by_category(self, category):
        sql = "SELECT * FROM products WHERE category = $1 AND is_active = TRUE"
        async with self.pool.acquire() as connection:
            return await connection.fetch(sql, category)

    async def add_product(self, category, photo, n_uz, n_ru, d_uz, d_ru, price):
        sql = """
        INSERT INTO products (category, photo_id, name_uz, name_ru, desc_uz, desc_ru, price, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE)
        """
        await self.execute(sql, category, photo, n_uz, n_ru, d_uz, d_ru, price)

    async def get_all_products(self):
        async with self.pool.acquire() as connection:
            return await connection.fetch("SELECT * FROM products WHERE is_active = TRUE ORDER BY id DESC")

    async def get_product_by_id(self, product_id):
        sql = "SELECT * FROM products WHERE id = $1"
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(sql, int(product_id))

    async def update_product_field(self, product_id, field, value):
        allowed_fields = ["name_uz", "name_ru", "desc_uz", "desc_ru", "price", "photo_id", "category"]
        if field not in allowed_fields: return
        sql = f"UPDATE products SET {field} = $1 WHERE id = $2"
        await self.execute(sql, value, int(product_id))

    async def delete_product(self, product_id):
        await self.execute("UPDATE products SET is_active = FALSE WHERE id = $1", int(product_id))


    # ================= 3. AKSIYA (PROMOTIONS) =================
    async def add_promotion(self, photo, name_uz, name_ru, cap_uz, cap_ru, price):
        sql = """
        INSERT INTO promotions (photo, name_uz, name_ru, caption_uz, caption_ru, price, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, TRUE)
        """
        await self.execute(sql, photo, name_uz, name_ru, cap_uz, cap_ru, price)

    async def get_all_promotions(self):
        sql = "SELECT * FROM promotions WHERE is_active = TRUE ORDER BY id DESC"
        async with self.pool.acquire() as connection:
            return await connection.fetch(sql)

    async def get_promotion_by_id(self, promo_id):
        sql = "SELECT * FROM promotions WHERE id = $1"
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(sql, int(promo_id))

    async def update_promotion_field(self, promo_id, field, value):
        allowed_fields = ["name_uz", "name_ru", "caption_uz", "caption_ru", "price", "photo"]
        if field not in allowed_fields: return
        sql = f"UPDATE promotions SET {field} = $1 WHERE id = $2"
        await self.execute(sql, value, int(promo_id))

    async def delete_promotion(self, promo_id):
        await self.execute("UPDATE promotions SET is_active = FALSE WHERE id = $1", int(promo_id))


    # ================= 4. SAVAT (CART) =================
    async def add_to_cart(self, user_id, product_name, quantity, price):
        sql = "INSERT INTO cart (user_id, product_name, quantity, price) VALUES ($1, $2, $3, $4)"
        await self.execute(sql, user_id, product_name, quantity, price)

    async def get_user_cart(self, user_id):
        sql = """
        SELECT c.id, c.product_name, c.quantity, c.price, (c.quantity * c.price) as total_price 
        FROM cart c 
        WHERE c.user_id = $1
        ORDER BY c.id
        """
        async with self.pool.acquire() as connection:
            return await connection.fetch(sql, user_id)

    async def clear_cart(self, user_id):
        await self.execute("DELETE FROM cart WHERE user_id = $1", user_id)

    async def delete_cart_item(self, cart_id):
        await self.execute("DELETE FROM cart WHERE id = $1", int(cart_id))


    # ================= 5. BUYURTMA (ORDER) =================
    async def create_order(self, user_id, total_amount, address_text=None, payment_type=None):
        sql = """
        INSERT INTO orders (user_id, total_amount, address_text, payment_type, status) 
        VALUES ($1, $2, $3, $4, 'new') RETURNING id
        """
        async with self.pool.acquire() as connection:
            return await connection.fetchval(sql, user_id, total_amount, address_text, payment_type)

    async def add_order_item(self, order_id, product_name, quantity, price):
        sql = """
        INSERT INTO order_items (order_id, product_name, quantity, price)
        VALUES ($1, $2, $3, $4)
        """
        await self.execute(sql, order_id, product_name, quantity, price)

    async def get_user_last_orders(self, user_id):
        sql = "SELECT * FROM orders WHERE user_id = $1 ORDER BY id DESC LIMIT 5"
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, user_id)

    async def get_order_items(self, order_id):
        sql = "SELECT * FROM order_items WHERE order_id = $1"
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, order_id)

    async def update_order_status(self, user_id, status):
        sql = "UPDATE orders SET status = $2 WHERE user_id = $1 AND status = 'new'"
        await self.execute(sql, user_id, status)


    # ================= 6. ADMIN VA STATISTIKA =================
    async def is_admin(self, user_id):
        if not self.pool: return False
        sql = "SELECT 1 FROM admins WHERE user_id = $1"
        async with self.pool.acquire() as connection:
            return await connection.fetchval(sql, user_id) is not None

    async def add_admin(self, user_id, full_name, added_by):
        await self.execute("INSERT INTO admins (user_id, full_name, added_by) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING", user_id, full_name, added_by)

    async def delete_admin(self, user_id):
        await self.execute("DELETE FROM admins WHERE user_id = $1", user_id)
        
    async def get_all_admins(self):
        if not self.pool: return []
        async with self.pool.acquire() as connection:
            return await connection.fetch("SELECT * FROM admins")
            
    async def count_admins(self):
        if not self.pool: return 0
        async with self.pool.acquire() as connection:
            return await connection.fetchval("SELECT COUNT(*) FROM admins")

    async def get_admin_info(self, user_id):
        sql = "SELECT full_name FROM admins WHERE user_id = $1"
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(sql, user_id)

    async def get_full_stats(self):
        async with self.pool.acquire() as conn:
            users = await conn.fetchval("SELECT COUNT(*) FROM users")
            users_uz = await conn.fetchval("SELECT COUNT(*) FROM users WHERE language='uz'")
            users_ru = await conn.fetchval("SELECT COUNT(*) FROM users WHERE language='ru'")
            
            sales = await conn.fetchval("SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE created_at::date = CURRENT_DATE")
            orders = await conn.fetchval("SELECT COUNT(*) FROM orders WHERE created_at::date = CURRENT_DATE")
            
            return {
                "users": users, 
                "users_uz": users_uz, 
                "users_ru": users_ru,
                "sales": sales, 
                "orders": orders
            }