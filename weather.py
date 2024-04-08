'''
Šis ir Python skripts, kas izmanto OpenWeatherMap API, lai iegūtu laika apstākļu datus par konkrētu atrašanās vietu.
Tas izmanto SQLite datu bāzi, lai saglabātu laika apstākļu datus par dažādām atrašanās vietām.
'''

import requests
import base64
import json
import os
import sqlite3

'''
Izveido SQLite datu bāzi ar divām tabulām: Locations un WeatherData.
'''
def create_database():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()

    '''
    Izveido Locations tabulu ar divām kolonnām: id un name.
    '''
    c.execute('''
        CREATE TABLE IF NOT EXISTS Locations (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')

    '''
    Izveido WeatherData tabulu ar sešām kolonnām: id, location_id, description, temperature, feels_like, high, low.
    location_id ir svešā atslēga, kas atsaucas uz Locations tabulas id.
    '''
    c.execute('''
        CREATE TABLE IF NOT EXISTS WeatherData (
            id INTEGER PRIMARY KEY,
            location_id INTEGER,
            description TEXT,
            temperature INTEGER,
            feels_like INTEGER,
            high INTEGER,
            low INTEGER,
            FOREIGN KEY(location_id) REFERENCES Locations(id)
        )
    ''')

    conn.commit()
    conn.close()

'''
Ievieto atrašanās vietu Locations tabulā un atgriež tās id.
'''
def insert_location(name):
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()

    c.execute('INSERT INTO Locations (name) VALUES (?)', (name,))
    location_id = c.lastrowid

    conn.commit()
    conn.close()

    return location_id

'''
Ievieto laika apstākļu datus WeatherData tabulā.
'''
def insert_weather_data(location_id, weather_data):
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO WeatherData (location_id, description, temperature, feels_like, high, low)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (location_id, weather_data['description'], weather_data['temperature'], weather_data['feels_like'], weather_data['high'], weather_data['low']))

    conn.commit()
    conn.close()

'''
Lasīt šifrēto API atslēgu no faila.
'''
def read_encrypted_api_key(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

'''
Atšifrē base64 kodēto API atslēgu.
'''
def decrypt_api_key(encrypted_key):
    try:
        decoded_bytes = base64.b64decode(encrypted_key)
        return decoded_bytes.decode("utf-8")
    except Exception as e:
        print(f"Error decoding API key: {e}")
        return None

'''
Iegūst laika apstākļu datus no OpenWeatherMap API izmantojot norādīto atrašanās vietu un API atslēgu.
'''
def get_weather_data(location, api_key):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={api_key}'
    result = requests.get(url)
    data = result.json()
    if data.get('cod') == 200:
        return {
            'description': data['weather'][0]['description'],
            'temperature': round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'high': round(data['main']['temp_max']),
            'low': round(data['main']['temp_min'])
        }
    else:
        print(f"Error fetching weather data for {location}.")
        return None

'''
Iegūst laika apstākļu datus no OpenWeatherMap API izmantojot norādīto atrašanās vietu un API atslēgu.

Location:
    name - norāda uz konkrētu vietu.
    latitude un longitude - koordinātu dati, kas norāda uz konkrētu ģeogrāfisko atrašanās vietu.

WeatherData:
    description - laikapstākļi konkrētā vietā, lai informētu lietotāju par pašreizējiem laikapstākļiem.
    temperature - temperatūra konkrētā vietā, lai informētu lietotāju par pašreizējo temperatūru.
    feels_like - temperatūra, ņemot vērā vēja ātrumu un mitrumu, lai informētu lietotāju par to, kāda temperatūra šķiet, ņemot vērā šos faktorus.
    high - augstākās dienas temperatūra, lai informētu lietotāju par dienas augstāko temperatūru.
    low - zemākā dienas temperatūra, lai informētu lietotāju par dienas zemāko temperatūru
'''
def get_weather_data(location, api_key):
def main():
    create_database()

    api_key_file = "api_key.txt"
    encrypted_api_key = read_encrypted_api_key(api_key_file)
    if encrypted_api_key:
        api_key = decrypt_api_key(encrypted_api_key)
        if api_key:
            location = input("Enter location: ")
            weather_data = get_weather_data(location, api_key)
            if weather_data:
                print(f"The weather in {location.capitalize()} is {weather_data['temperature']}°C with {weather_data['description']}.")
                print(f"It feels like {weather_data['feels_like']}°C.")
                print(f"Today's high is {weather_data['high']}°C and today's low is {weather_data['low']}°C.")
                location_id = insert_location(location)
                insert_weather_data(location_id, weather_data)
        else:
            print("Failed to decrypt API key. Check your encryption method.")
    else:
        print(f"API key not found in {api_key_file}.")

if __name__ == "__main__":
    '''
    Ja __name__ == "__main__", šī funkcija tiek izsaukta, kad skripts tiek izpildīts tieši.
    Tā izsauc galveno funkciju, lai sāktu programmu.
    '''
    main()
