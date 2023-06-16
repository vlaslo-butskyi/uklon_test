import asyncio
import requests
import random

from geopy.geocoders import Nominatim
from src.settings import config

API_ENDPOINT = 'http://driver:8080/api/v1/driver-geo/'

geolocator = Nominatim(user_agent='uklon-generator').geocode("Lviv, Ukraine")
bounding_box = geolocator.raw['boundingbox']
bounding_box = [float(coord) for coord in bounding_box]


async def loop():
    while True:
        tasks = []
        for driver_id in range(1, config.get('NUM_DRIVERS') + 1):
            task = asyncio.create_task(generate_and_send_coordinates(driver_id))
            tasks.append(task)

        await asyncio.gather(*tasks)

        await asyncio.sleep(config.get('DELAY_REQUEST'))


async def generate_and_send_coordinates(driver_id):
    latitude, longitude, speed, altitude = generate_coordinates()
    await send_coordinates(driver_id, latitude, longitude, speed, altitude)


def generate_coordinates():
    min_lat, max_lat, min_lon, max_lon = bounding_box

    latitude = random.uniform(min_lat, max_lat)
    longitude = random.uniform(min_lon, max_lon)

    speed = random.uniform(0, 200)
    altitude = random.uniform(-100, 1000)

    return latitude, longitude, speed, altitude


async def send_coordinates(driver_id, latitude, longitude, speed, altitude):
    data = {
        'driver_id': driver_id,
        'latitude': latitude,
        'longitude': longitude,
        'speed': speed,
        'altitude': altitude
    }
    try:
        response = requests.post(API_ENDPOINT, json=data)
    except requests.exceptions.ConnectionError as ex:
        print(f"Error sending data for driver {driver_id}")
    else:
        if response.status_code == 200:
            print(f"Data for driver {driver_id} successfully sent")
        else:
            print(f"Error sending data for driver {driver_id}")


def main():
    asyncio.run(loop())


if __name__ == "__main__":
    main()
