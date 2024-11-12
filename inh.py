from librairies import *
from datetime import datetime, timezone
import pytz, requests
import os

# Function to write JSON data to a file, returns True if successful, otherwise False
def get_ics_json(json_data):
    try:
        with open('./data/ics.json', 'w') as json_file:
            json.dump(json_data, json_file, indent=4)  # Write JSON data with indentation
        return True
    except Exception as e:
        print(f"Erreur lors de l'écriture : {e}")  # Catch any errors during file writing
        return False


# Function to fetch calendar URLs from the local ics.json file
def get_calendar_from_db():
    with open('./data/ics.json', 'r') as file:
        data = json.load(file)  # Load the JSON data
        print(data)
    
    ids = [value for value in data.values() if value != ""]  # Extract non-empty values (calendar IDs)
    base_url = "https://cytt.app/"
    urls = [f"{base_url}{id}.ics" for id in ids]  # Construct .ics URLs
    return urls


# Function to import calendar files by fetching .ics files from URLs
def import_calendar():
    urls = get_calendar_from_db()  # Get the list of calendar URLs
    calendar = []
    
    for url in urls:
        response = requests.get(url)  # Fetch the .ics file from the URL
        file_name = f'{url.split("/")[-1]}'  # Extract the filename from the URL
        file_path = os.path.join('./data', file_name)  # Create a path to save the file locally
        
        # Write the content to a file
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        calendar.append(file_name)  # Add the filename to the calendar list
    return calendar


# Function to combine multiple .ics files into a single file
def combine_calendar(calendar):
    combined_calendar = "./data/all.ics"  # File path for the combined calendar
    
    with open(combined_calendar, 'wb') as combined_file:
        for file_name in calendar:
            file_path = os.path.join('./data', file_name)  # Get the file path for each .ics file
            
            # Read and write the content of each .ics file
            with open(file_path, 'rb') as file:
                combined_file.write(file.read())
    
    return combined_calendar  # Return the path to the combined calendar


# Function to build a JSON file from the .ics calendar for the current day's courses
def build_Json(calendar_file, fixed_time=None):
    paris_tz = pytz.timezone('Europe/Paris')  # Set Paris timezone

    if fixed_time:
        current_time = datetime.fromisoformat(fixed_time)  # Use provided fixed time
    else:
        current_time = datetime.now(tz=paris_tz)  # Use current time in Paris timezone

    today = current_time.date()  # Get today's date
    json_file = "./data/cours_du_jour.json"  # Path to save today's courses
    courses_today = []

    # Read the .ics file and parse events
    with open(calendar_file, 'r') as file:
        inside_vevent = False
        event = {}
        for line in file:
            if line.startswith('BEGIN:VEVENT'):
                inside_vevent = True
                event = {}
            elif line.startswith('DTSTART:') and inside_vevent:
                value = line.strip().split(':', 1)[1].replace('TZ', '')
                dtstart = datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=pytz.utc)
                dtstart_paris = dtstart.astimezone(paris_tz)
                if dtstart_paris.date() == today:
                    event['start_time'] = dtstart_paris.strftime('%H:%M')
            elif line.startswith('DTEND:') and inside_vevent:
                value = line.strip().split(':', 1)[1].replace('TZ', '')
                dtend = datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=pytz.utc)
                dtend_paris = dtend.astimezone(paris_tz)
                if dtend_paris.date() == today:
                    event['end_time'] = dtend_paris.strftime('%H:%M')
            elif line.startswith('SUMMARY:') and inside_vevent:
                event['summary'] = line.strip().split(':', 1)[1].strip()
            elif line.startswith('LOCATION:') and inside_vevent:
                location = line.strip().split(':', 1)[1]
                if len(location) > 5:
                    event['location'] = location.split(",")
                else:
                    event['location'] = location.strip()
            elif line.startswith('ORGANIZER:') and inside_vevent:
                event['organizer'] = line.strip().split(':', 1)[1].strip()
            elif line.startswith('END:VEVENT'):
                # Handle multiple locations for a single event
                if isinstance(event.get('location'), list):
                    for loc in event['location']:
                        duplicated_event = event.copy()
                        duplicated_event['location'] = loc.strip()
                        if all(k in duplicated_event for k in ['start_time', 'end_time', 'summary', 'organizer']):
                            courses_today.append(duplicated_event)
                else:
                    if all(k in event for k in ['start_time', 'end_time', 'summary', 'location', 'organizer']):
                        courses_today.append(event)
                inside_vevent = False

    # Write today's courses to a JSON file
    with open(json_file, 'w') as outfile:
        json.dump(courses_today, outfile, indent=4)


# Function to find the next course at a specified location
def next_course(json_file, location1, fixed_time=None):
    paris_tz = pytz.timezone('Europe/Paris')  # Paris timezone
    
    # Get the current time or use fixed_time if provided
    if fixed_time:
        current_time = datetime.fromisoformat(fixed_time).astimezone(paris_tz)
    else:
        current_time = datetime.now(tz=paris_tz)

    # Load the JSON data of today's courses
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Filter courses by the specified location
    courses_in_location = [course for course in data if course["location"] == location1]
    
    if not courses_in_location:
        return None  # Return None if no courses are found for the location

    # Sort the courses by their start time
    sorted_courses = sorted(courses_in_location, key=lambda x: x.get('start_time'))
    
    # Loop through the courses to find the next one
    for course in sorted_courses:
        start_time = datetime.strptime(course['start_time'], '%H:%M').replace(tzinfo=paris_tz)
        if start_time.time() > current_time.time():
            return {
                "Début": course['start_time'],
                "Fin": course['end_time'],
                "Prof": course['organizer'],
                "Résumé": course['summary']
            }
    
    return None  # If no upcoming course is found, return None


# Function to check room availability based on today's course schedule
def fetch(fixed_time=None):
    toutes_salles = ["A001", "E101", "E102", "E103", "E104", "E105", "E106", "E107", "E108", "E109", "E201", "E209", "E210", "E211", "E212", "E213", "E214", "E215", "E217", "E218"]  # List of rooms

    with open('./data/cours_du_jour.json', 'r') as f:
        cours_du_jour = json.load(f)  # Load the JSON file with today's courses

    paris_tz = pytz.timezone('Europe/Paris')  # Set Paris timezone

    if fixed_time:
        current_time = datetime.fromisoformat(fixed_time).replace(tzinfo=paris_tz)
    else:
        current_time = datetime.now(tz=paris_tz)
    
    salles_remplies = []  # List for occupied rooms
    salles_vide_prochain_cours = []  # List for rooms with upcoming courses

    for salle in toutes_salles:
        current_courses = verif_time("./data/cours_du_jour.json", fixed_time)
        location_data = verif_location(current_courses, salle)

        if location_data:
            for current_course in location_data:
                course_info = {
                    "Début": current_course['start_time'],
                    "Fin": current_course['end_time'],
                    "Prof": current_course['organizer'],
                    "Résumé": current_course['summary']
                }
                already_exists = any(course.get(salle) == course_info for course in salles_remplies)
                if not already_exists:
                    salles_remplies.append({salle: course_info})

        next_course_info = next_course("./data/cours_du_jour.json", salle, fixed_time)
        if next_course_info:
            course_info = {
                "Début": next_course_info.get('Début', 'Non spécifié'),
                "Fin": next_course_info.get('Fin', 'Non spécifié'),
                "Prof": next_course_info.get('Prof', 'Non spécifié'),
                "Résumé": next_course_info.get('Résumé', 'Non spécifié')
            }
            already_exists = any(course.get(salle) == course_info for course in salles_vide_prochain_cours)
            if not already_exists:
                salles_vide_prochain_cours.append({salle: course_info})

    salles_vide_journee = [salle for salle in toutes_salles if salle != "A001" and salle not in salles_remplies and salle not in salles_vide_prochain_cours]

    resultat = {
        "salles_vide_journee": {"locations": salles_vide_journee},
        "salle_remplis": salles_remplies,
        "salle_vide_prochain_cours": salles_vide_prochain_cours
    }

    return resultat


# Function to verify which courses are currently happening
def verif_time(json_file, fixed_time=None):
    paris_tz = pytz.timezone('Europe/Paris')  # Set Paris timezone

    with open(json_file, 'r') as file:
        data = json.load(file)  # Load today's courses JSON data

    if fixed_time:
        current_time = datetime.fromisoformat(fixed_time).astimezone(paris_tz).strftime('%H:%M')
    else:
        current_time = datetime.now(tz=paris_tz).strftime('%H:%M')

    current_courses = []

    for course in data:
        start_time = datetime.strptime(course['start_time'], '%H:%M').replace(tzinfo=paris_tz).strftime('%H:%M')
        end_time = datetime.strptime(course['end_time'], '%H:%M').replace(tzinfo=paris_tz).strftime('%H:%M')
        if start_time <= current_time <= end_time:
            current_courses.append(course)

    return current_courses


# Function to verify if a course is happening in a specific location
def verif_location(courses, location):
    verif_location = []
    for course in courses:
            if course['location'] == location:
                verif_location.append(course)
    return verif_location