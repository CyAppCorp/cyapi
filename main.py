from librairies import *
from events import remove_Event, add_Event, modify_Event, get_Available_Events, users_Event, removeUser_Event, addUser_Event, reset_Users
from homeworks import add_Homework, remove_Homework, get_Homeworks, edit_Homeworks
from rooms import add_Rooms, get_Rooms, delete_Rooms, warn_User
from inh import get_ics_json, build_Json, combine_calendar, import_calendar, fetch
from polls import add_Poll, get_Available_Polls, add_user_vote, remove_Poll
from news import add_News, get_Available_News, remove_News, modify_News
from auth import authUser, add_Asso, add_Followers_Asso, remove_Followers_Asso,users_Followers_Asso,add_All_Followers_Asso,remove_All_Followers_Asso

load_dotenv()

# Récupérer les variables d'environnement PROD
uri = os.environ.get("MONGO_URL")
key = os.environ.get("KEY")
fb_key = os.environ.get("FIREBASE_KEY")


if uri is None:
    print("Error: MONGO_URL environment variable is not set.")
    exit(1)

if key is None:
    print("Error: KEY environment variable is not set.")
    exit(1)

if fb_key is None:
    print("Error Firebase Key environment variable is not set")
    exit(1)


"""
Function NameRoute
Handles API/Application connection isBorisHere
Waits for a POST request and returns data based on conditions
"""

app = Flask(__name__)

try :
    cred = credentials.Certificate(fb_key)
    firebase_admin.initialize_app(cred)
    print("Connexion à Firebase établie")
except:
    print("Connexion pas réussi à Firebase")


# Create a MongoDB client and connect to the database
client = MongoClient(uri)
# Test the connection by pinging the server
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Get databases for events, infos, homeworks, polls, and news
db_events = client.get_database('cy_events')
db_infos = client.get_database('cy_infos')
db_homeworks = client.get_database('cy_homeworks')
db_polls = client.get_database('cy_polls')
db_news = client.get_database('cy_news')
db_users = client.get_database('cy_users')


# Helper function to build a CORS preflight response
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

@app.route('/cyapi', methods = ['POST','OPTIONS'])
def nameRoute():
    
    # Handle CORS preflight request
    if request.method == "OPTIONS": 
        return _build_cors_preflight_response()
    
    result = False
    request_data = json.loads(request.data.decode('utf-8'))  # Decode incoming JSON request
    
    # Add user to database (First connection)
    if (request_data['usage']) == "auth_token":
        result = authUser(request_data["token"],request_data["username"],request_data["user_fullname"],request_data["user_email"],db_infos,db_users)

    if(request_data['usage']) == "add_asso":
        result = add_Asso(request_data["asso"],request_data["desc"],db_infos)

    if(request_data['usage']) == "add_followers_asso":
        result = add_Followers_Asso(request_data["user_id"],request_data["asso"],db_infos,db_users)

    if(request_data['usage']) == "remove_followers_asso":
        result = remove_Followers_Asso(request_data["user_id"],request_data["asso"],db_infos,db_users)

    if(request_data['usage']) == "add_all_followers_asso":
        result = add_All_Followers_Asso(request_data["user_id"],request_data["assos"],db_infos,db_users)

    if(request_data['usage']) == "remove_all_followers_asso":
        result = remove_All_Followers_Asso(request_data["user_id"],request_data["assos"],db_infos,db_users)


    if(request_data['usage']) == "users_followers_asso":
        result = users_Followers_Asso(request_data["user_id"],db_infos,db_users)
            


    # Add a user to an event
    if (request_data['usage']) == "add_user":
        try:
            id_event = request_data['id_event']  # Try to get event ID from request
        except Exception as e:
            # If event ID is missing, fall back to old API connection to find the event by name
            print("Connecting to old API")
            existing_event = db_infos.infos_event.find_one({"event": request_data['event']})
            if existing_event: 
                id_event = existing_event["id"]
        try:
            user_id = request_data['user_id']  # Try to get user ID from request
        except Exception as e:
            # If user ID is missing, fall back to old API connection to find the event by name
            print("Connecting to old API")
            existing_user = db_users.users.find_one({"user_fullname": request_data['name']})
            if existing_user: 
                user_id = existing_user["user_id"]
            else :
                print("User not found")
                return {"status" : "User not found"}
            

        result = addUser_Event(id_event, request_data['event'],user_id, db_events, db_users)
        
    # Remove a user from an event
    if (request_data['usage']) == "remove_user":
        try:
            id_event = request_data['id_event']  # Get event ID
        except Exception as e:
            # If event ID is missing, use old API connection to find the event by name
            print("Connecting to old API")
            existing_event = db_infos.infos_event.find_one({"event": request_data['event']})
            if existing_event: 
                id_event = existing_event["id"]

        try:
            id_event = request_data['user_id']  # Try to get user ID from request
        except Exception as e:
            # If user ID is missing, fall back to old API connection to find the event by name
            print("Connecting to old API")
            existing_user = db_users.users.find_one({"user_fullname": request_data['name']})
            if existing_user: 
                user_id = existing_user["user_id"]

        result = removeUser_Event(id_event, request_data['event'], user_id , db_events, db_users) 
        
    # Retrieve all users for a specific event
    if (request_data['usage']) == "users":
        try:
            id_event = request_data['id_event']  # Get event ID
        except Exception as e:
            # If event ID is missing, find the event by name
            print("Connecting to old API")
            existing_event = db_infos.infos_event.find_one({"event": request_data['event']})
            if existing_event: 
                id_event = existing_event["id"]
        result = users_Event(id_event, request_data['event'], db_events)
 
    ##### ADMIN SECTION ####

    # Retrieve all available events
    if (request_data['usage']) == "available_events":
        result = get_Available_Events(db_infos,db_events,db_users,request_data.get('admin', False))
        
    # Add a new event
    if request_data['usage'] == "add_event":
        result = add_Event(
            event=request_data['event'],
            timestamp=request_data['timestamp'],
            lieu=request_data['lieu'],
            desc=request_data['desc'],
            prix=request_data['prix'],
            emoji=request_data['emoji'],
            link=request_data['link'],
            asso=request_data['asso'],
            image=request_data['image'],
            encoded_creator=request_data['encoded_creator'],
            key=key,
            db_events=db_events,
            db_infos=db_infos,
            db_users=db_users,
            scheduled=request_data.get('scheduled', False),
            scheduled_time=request_data.get('scheduled_time', None)
        )
    
    # Modify an existing event
    if (request_data['usage']) == "modify_event":
        result = modify_Event(request_data['id_event'], request_data['event'], request_data['timestamp'], 
                              request_data['lieu'], request_data['desc'], request_data['prix'], 
                              request_data['emoji'], request_data['link'], request_data['asso'], 
                              request_data['image'], request_data['encoded_creator'], key, db_events, db_users , db_infos)

    # Remove an event
    if (request_data['usage']) == "remove_event":
        result = remove_Event(request_data['id_event'], request_data['event'], request_data['encoded_creator'], key, db_events,db_users, db_infos)
    
    # Reset users for an event
    if (request_data['usage']) == "reset_users":
        result = reset_Users(request_data['id_event'], request_data['event'], request_data['encoded_creator'], key, db_events, db_infos)


    ## HOMEWORK SECTION ###

    # Add a new homework
    if(request_data['usage']) == "add_homework":
        result = add_Homework(db_homeworks, request_data['title'], request_data['subject'], request_data['group'], 
                              request_data['desc'], request_data['timestamp'], request_data['user_id'],db_users)
        
    # Remove a homework
    if(request_data['usage']) == "remove_homework":
        result = remove_Homework(db_homeworks, request_data['id'], request_data['user_id'],db_users)
        
    # Retrieve homework for a specific group
    if(request_data['usage']) == "get_homework":
        result = get_Homeworks(db_homeworks, request_data['group'])
    
    # Edit an existing homework
    if(request_data['usage']) == "edit_homework":
        result = edit_Homeworks(db_homeworks, request_data['title'], request_data['subject'], request_data['group'], 
                                request_data['desc'], request_data['timestamp'], request_data['user_id'], request_data['id'],db_users)
        

    ## ROOM SECTION ###
        
    # Retrieve all booked rooms
    if(request_data['usage']) == "get_booked_rooms":
        result = get_Rooms(db_infos)

    # Book a new room
    if(request_data['usage']) == "book_room":
        result = add_Rooms(db_infos, request_data["room"], request_data["until"], request_data["user_id"],db_users)
    
    # Delete a room booking
    if(request_data['usage']) == "delete_room":
        result = delete_Rooms(db_infos, request_data["room"])
    
    # Warn a user about something related to room bookings
    if(request_data['usage']) == "warn_user":
        result = warn_User(db_infos, request_data["user_id"],db_users)


    #########    POLLS SECTION      #############

    # Add a new poll
    if(request_data['usage']) == "add_poll":
        result = add_Poll(request_data["title"], request_data["options"], request_data["hide_bool"], request_data["timestamp"], 
                          request_data["desc"], request_data["asso"], request_data["encoded_creator"], key, db_polls)
    
    # Retrieve all available polls
    if(request_data['usage']) == "available_polls":
        result = get_Available_Polls(db_polls)

    # Add a user's vote to a poll
    if(request_data['usage']) == "add_user_vote":
        result = add_user_vote(request_data["id_poll"], request_data["id_options"], db_polls)

    # Remove a poll
    if(request_data['usage']) == "remove_poll":
        result = remove_Poll(request_data["id_poll"], request_data["encoded_creator"], key, db_polls)


    #########    NEWS SECTION      #############

    # Add a new news item
    if(request_data['usage']) == "add_news":
        result = add_News(request_data["title"], request_data["timestamp"], request_data["desc"], request_data["asso"], 
                          request_data["link"], request_data["encoded_creator"], key, db_news)
    
    # Retrieve all available news
    if(request_data['usage']) == "available_news":
        result = get_Available_News(db_news)

    # Remove a news item
    if(request_data['usage']) == "remove_news":
        result = remove_News(request_data["id_news"], request_data["encoded_creator"], key, db_news)

    # Modify an existing news item
    if(request_data['usage']) == "modify_news":
        result = modify_News(request_data["id_news"], request_data["title"], request_data["timestamp"], 
                             request_data["link"], request_data["desc"], request_data["asso"], 
                             request_data["encoded_creator"], key, db_news)


    # Build a JSON response based on the result
    if result:
        response = jsonify(result)
        response.headers['Accept'] =  '*/*'
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    else:
        response = {"status" : 0}

    return response


@app.route('/inh_api', methods=['POST'])
def build_response_api():
    
    request_data = json.loads(request.data.decode("utf-8"))  # Decode incoming JSON request
    
    fixed_time = None

    # Refresh ICS calendar data and rebuild the calendar
    if request_data["usage"] == "refresh_data":
        print("Refreshing data")
        result = get_ics_json(request_data["data"])  # Get ICS data from calendar
        if result:
            print("Building JSON")
            # Combine and build calendar from ICS files
            build_Json(combine_calendar(import_calendar()), fixed_time)
            response = fetch(fixed_time)  # Fetch the newly built calendar
            return jsonify(response)
        else:
            return jsonify({"error": "Failed to refresh data."}), 500

    # Fetch the existing calendar data
    if(request_data["usage"]) == "fetch":
        print("Fetching data")
        response = fetch(fixed_time)
        return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)