import subprocess
import requests
import time
import random

def check_internet_connection(timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get('https://www.google.com', timeout=3)
            if response.status_code == 200:
                print("Internet Werks!")
                return True
        except requests.ConnectionError:
            pass
        except requests.Timeout:
            pass
        time.sleep(1)

    print("No internet connection.")
    return False

def connect(number):
    # 0-170
    locations = [    "Besa",    "Fergese",    "Tango",    "Lofty",    "Oval",    "Bad Koala",    "Good Koala",    "Port Phillip",    "Yarra",    "Herdsman",    "Kings Park",    "Opera House",    "Squidney",    "Boltzmann",    "Hofburg",    "Guildhouse",    "Pisanica",    "Burek",    "Mercadao",    "Pinacoteca",    "Nevski",    "Botum Pagoda",    "Crosby",    "Bagel Poutine",    "Expo 67",    "Comfort Zone",    "The 6",    "Granville",    "Stanley",    "Vansterdam",    "Cueca",    "Rololandia",    "Tkalciceva",    "Blue Lagoon",    "Staromak",    "Vltava",    "LEGO",    "Cuy",    "Lennujaam",    "Station",    "Sauna",    "Tram",    "La Marseillaise",    "Jardin",    "Seine",    "Ghvino",    "Castle",    "Wurstchen",    "Best Jollof",    "Odeon",    "Phooey",    "Victoria",    "Danube",    "Fuzzy Pony",    "Reyka",    "Mahim",    "Chole Bhature",    "Ancol",    "Old Town",    "Dullahan",    "Grafton",    "Yam Park",    "Duomo",    "Galleria",    "Colosseum",    "Shinkansen",    "Wabi-sabi",    "Sigiria",    "Daugava",    "Saeima",    "Neris",    "Chemin",    "Perdana",    "Aqueduct",    "Dendrarium",    "Bicycle",    "Canal",    "Red Light",    "Tulip",    "Hauraki",    "Parnell",    "Vardar",    "Fjord",    "Papers",    "Amaru",    "Pasig",    "Motlawa",    "Curie",    "Vistula",    "Bairro",    "No Vampires",    "Goodbye Lenin",    "Hermitage",    "Shnur",    "Rakia",    "Garden",    "Marina Bay",    "SMRT",    "Devin Castle",    "District",    "Lindfield",    "Springbok",    "Han River",    "Hangang",    "Batllo",    "Prado",    "Djurgarden",    "Ikea",    "Syndrome",    "Alphorn",    "Altstadt",    "Lindenhof",    "Datong",    "Hangover",    "Lumphini",    "Galata",    "Lygos",    "Ghost",    "Khalifa",    "Keeper Willie",    "Biscuits",    "Crumpets",    "Custard",    "United",    "Mountain",    "Piedmont",    "BBQ",    "Ranch",    "Trinity",    "Barley",    "Space City",    "Glinda",    "Harvard",    "MIT",    "Bill",    "Earnhardt",    "Cub",    "Wrigley",    "Brown",    "Coney Dog",    "Florida Man",    "Snow",    "Vice",    "Empire",    "Grand Central",    "Insomnia",    "Tofu Driver",    "Fresh Prince",    "Sunny",    "Hawkins",    "Cuban Sandwich",    "Precedent",    "Oregon Trail",    "Casino",    "Cube",    "Dogg",    "Lamar",    "Pac",    "Floatie",    "Sanitation",    "Santana",    "Inside",    "Cobain",    "Cornell",    "Hendrix",    "Red River",    "Mansbridge",    "Kaiju",    "The Tube",    "Radiohall"]

    command = [r'C:\Program Files\Windscribe\windscribe-cli.exe', 'connect', locations[number]]

    subprocess.run(command)

    time.sleep(3)


def connect_random():
    connect(random.randint(0,170))
def disconnect():
    command = [r'C:\Program Files\Windscribe\windscribe-cli.exe', 'disconnect']

    subprocess.run(command)

connect_random()


