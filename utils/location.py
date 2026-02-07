from geopy.geocoders import Nominatim
import asyncio
from functools import partial

geolocator = Nominatim(user_agent="afif_delivery_bot")

async def get_address_from_coords(lat, lon):
    try:
        loop = asyncio.get_running_loop()
        
        location = await loop.run_in_executor(
            None, 
            partial(geolocator.reverse, f"{lat}, {lon}", language='uz') 
        )
        
        if location:
            data = location.raw.get('address', {})
            parts = []
            
            city = data.get('city') or data.get('state') or data.get('province')
            if city: parts.append(city)
            
            district = data.get('county') or data.get('district') or data.get('suburb')
            if district: parts.append(district)
            
            street = data.get('road') or data.get('residential') or data.get('neighbourhood')
            if street: parts.append(street)
            
            house = data.get('house_number')
            if house: parts.append(f"{house}-uy")
            
            clean_address = ", ".join(parts)
            
            return clean_address
            
        return None
    except Exception as e:
        print(f"Manzilni aniqlashda xatolik: {e}")
        return None