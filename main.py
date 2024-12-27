import requests
import json
import os
from datetime import date


def clear():
    os.system("clear")


# units
units = {
    'm': 'meters',
    'km': 'kilometers',
    'mi': 'miles',
    'ft': 'feet'
}

# Select Date
print('If you would like to search for a custom date enter 0. If you would like to search for today enter 1. Enter your response in the prompt below:')
q1 = input()
if q1 == str(0):
    print('Please enter date you would like to browse. Format must be YYYY-MM-DD: ')
    searchDate = input()
elif q1 == str(1):
    searchDate = date.today()
else:
    print('\nSorry there has been an error. Please try again.\n')
    exit()

# API
try:
    response_API = requests.get(
        f'https://api.nasa.gov/neo/rest/v1/feed?start_date={searchDate}&end_date={searchDate}&api_key=a891sk5lkhJVt0YJTSxd5bk97uCxc95HfsfjBAHP', timeout=300000)
    response_API.raise_for_status()
    data = response_API.text
    parse_json = json.loads(data)
    allAsteroids = parse_json['near_earth_objects'][str(searchDate)]
    elementCount = parse_json['element_count']
except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching data: {e}")
    exit()

# Select Unit
print("Select the unit of measurement for the asteroid's diameter and miss distance:")
for key, value in units.items():
    print(f"{key}: {value}")
selected_unit = input("Enter the unit (m/km/mi/ft): ").strip().lower()
if selected_unit not in units:
    print("Invalid unit selected. Defaulting to meters.")
    selected_unit = 'm'

# Data from asteroid highest on AH Index
print("\nEnter the highest number for # of asteroids you would like to view below. Available numbers are 1 to", elementCount, "| Enter highest value:")
maxRangeVal = int(input())
print("\nIf you want to receive data from all asteroids, regardless of AHI value, press 1. If you want data from asteroids with only an AHI value of 1 or higher (default) press 0.")
datainp = int(input())

class Asteroid:
    def __init__(self, data):
        self.array = data
        self.name = self.array['name']
        self.cADat = self.array['close_approach_data']
        self.EstD = self.array['estimated_diameter']
        self.MissDis = self.cADat[0]
        self.MissDisLuna = self.MissDis['miss_distance']
        self.AstD = self.EstD[units[selected_unit]]
        self.MinD = self.AstD['estimated_diameter_min']
        self.MaxD = self.AstD['estimated_diameter_max']
        self.avgAstD = round((self.MinD + self.MaxD) / 2, 3)
        self.cADate1 = self.cADat[0]
        self.cADate2 = self.cADate1['close_approach_date']
        self.velocity = self.cADate1['relative_velocity']['kilometers_per_hour']
        self.orbiting_body = self.cADate1['orbiting_body']
        self.hazardous = self.array["is_potentially_hazardous_asteroid"]

def calculate_ahi_level(astDat):
    try:
        lunar_distance = float(astDat.MissDisLuna['lunar'])
        avg_diameter = astDat.avgAstD

        if lunar_distance >= 1 or avg_diameter < 10:
            return 0
        elif 0.1 <= lunar_distance < 1:
            if 10 <= avg_diameter < 25:
                return 1
            elif 25 <= avg_diameter < 50:
                return 2
            elif 50 <= avg_diameter < 100:
                return 3
            elif 100 <= avg_diameter < 200:
                return 4
            elif avg_diameter >= 500:
                return 4
            else:
                return 0
        elif lunar_distance <= 0.01 and avg_diameter > 100:
            return 5
        elif 0.01 <= lunar_distance < 0.1:
            if 100 <= avg_diameter <= 500:
                return 3
            elif avg_diameter <= 10:
                return 0
        elif 0.1 <= lunar_distance <= 0.25:
            if 200 <= avg_diameter <= 500:
                return 2
            elif avg_diameter >= 500:
                return 3
        elif 0.25 <= lunar_distance <= 0.5:
            if 200 <= avg_diameter <= 500:
                return 1
            elif avg_diameter >= 500:
                return 2
        else:
            return 0
    except (TypeError, ValueError):
        print("An error has occurred in gathering data. Please check the code or the data you are drawing from")
        return 0

def display_asteroid_data(astDat, ahiLevel):
    print()
    print(" Asteroid Name:", astDat.name, "\n", "Average Asteroid Diameter:",
          astDat.avgAstD, units[selected_unit], "\n", "Asteroid miss distance in LD:",
          round(float(astDat.MissDisLuna['lunar']), 2), "\n Date of closest approach:", astDat.cADate2,
          "\n Velocity (km/h):", astDat.velocity, "\n Orbiting Body:", astDat.orbiting_body)
    if float(astDat.MissDisLuna['lunar']) < 0.01:
        print(" Alert! Closest approach is less than 0.01 LD")
    elif 0.01 < float(astDat.MissDisLuna['lunar']) < 0.1:
        print(" Concern may be warranted. Closest approach is between 0.01 and 0.1 LD")
    else:
        print(" Close approach is far enough away to be safe.")
    print(" AHI Level: Level", ahiLevel)
    if astDat.hazardous:
        print(" This asteroid is classified as a potentially hazardous asteroid.")
    else:
        print(" This asteroid is not classified as a potentially hazardous asteroid.")
    print()

def display_summary_statistics(asteroids):
    total_asteroids = len(asteroids)
    avg_diameter = sum(ast.avgAstD for ast in asteroids) / total_asteroids
    print(f"\nSummary Statistics:\nTotal number of asteroids: {total_asteroids}\nAverage diameter: {avg_diameter:.2f} {units[selected_unit]}")

asteroids = []
for i in range(0, maxRangeVal):
    astDat = Asteroid(allAsteroids[i])
    ahiLevel = calculate_ahi_level(astDat)
    if datainp == 0 and ahiLevel >= 1:
        display_asteroid_data(astDat, ahiLevel)
    elif datainp == 1:
        display_asteroid_data(astDat, ahiLevel)
    asteroids.append(astDat)

display_summary_statistics(asteroids)

# Save asteroid data to a file
save_data = input("Would you like to save the asteroid data to a file? (yes/no): ").strip().lower()
if save_data == 'yes':
    file_name = input("Enter the file name (with .txt extension): ").strip()
    with open(file_name, 'w') as file:
        for astDat in asteroids:
            ahiLevel = calculate_ahi_level(astDat)
            file.write(f"Asteroid Name: {astDat.name}\n")
            file.write(f"Average Asteroid Diameter: {astDat.avgAstD} {units[selected_unit]}\n")
            file.write(f"Asteroid miss distance in LD: {round(float(astDat.MissDisLuna['lunar']), 2)}\n")
            file.write(f"Date of closest approach: {astDat.cADate2}\n")
            file.write(f"Velocity (km/h): {astDat.velocity}\n")
            file.write(f"Orbiting Body: {astDat.orbiting_body}\n")
            file.write(f"AHI Level: Level {ahiLevel}\n")
            if astDat.hazardous:
                file.write("This asteroid is classified as a potentially hazardous asteroid.\n")
            else:
                file.write("This asteroid is not classified as a potentially hazardous asteroid.\n")
            file.write("\n")
    print(f"Asteroid data has been saved to {file_name}")
else:
    print("Asteroid data was not saved.")

print("Thank you for using Asteroid.py, have a nice day.")
