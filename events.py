from librairies import *
from auth import authName, send_New_Event_notification, send_Remove_Event_notification
# Adds a user to an event, returns the user if already added or adds them to the event
def addUser_Event(id_event, event, user_id, db_events,db_users):

    name = authName(user_id,db_users)

    if name == None:
        return {"status" : "Not Updated"}

    event_name = f'{id_event}_event'

    db_event_collection = db_events.get_collection(event_name)  # Get the MongoDB collection for the event
    existing_user = db_event_collection.find_one({"user_id": user_id})  # Check if the user is already registered
    if existing_user:
        existing_user.pop('_id', None)  # Remove the internal MongoDB ID
        return {"status" : "Already registred"}  # Return the existing user if found
    else:
        # If the user doesn't exist, create a new user record
        add_user = {
            "user": name,
            "user_id" : user_id,
            "timestamp": time.time()  # Record the current time as timestamp
        }

    db_event_collection.insert_one(add_user)  # Insert the new user into the event collection
    add_user.pop('_id', None)  # Remove the MongoDB ID before returning
    return {"status" : True}  # Return the added user data

# Removes a user from an event by their name
def removeUser_Event(id_event, event, user_id, db_events, db_users):

    name = authName(user_id,db_users)

    if name == None:
        return {"status" : "Not Updated"}
    
    event_name = f'{id_event}_event'  # Collection name for the event
    db_event_collection = db_events.get_collection(event_name)
    result = db_event_collection.delete_one({"user_id": user_id})  # Delete the user document
    if result.deleted_count == 1:  # Check if a user was successfully removed
        result = {"user_removed": True}
    else:
        result = {"user_removed": False}  # No user found to remove
    return result

# Resets (removes) all users from an event, with admin authorization
def reset_Users(id_event, event, encoded_creator, key, db_events, db_infos):
    creator = decodeEncodedCreator(encoded_creator, key)  # Decode the creator from JWT
    
    if not creator:
        return {"status": "Invalid creator"}

    result = False
    db_collection_name = f'{id_event}_event'  # Event-specific collection
    if db_collection_name in db_events.list_collection_names():
        existing_event = db_infos.infos_event.find_one({"id": id_event})  # Check if the event exists
        if existing_event and (existing_event["creator"] == creator or creator == "admin"):
            db_event_collection = db_events.get_collection(db_collection_name)
            result = db_event_collection.delete_many({})  # Remove all users from the event

    if result.deleted_count:
        result = {"users_removed": result.deleted_count}  # Return how many users were removed
    else:
        result = {"users_removed": False}
    return result

# Fetches all users for a specific event
def users_Event(id_event, event, db_events):
    event_name = f'{id_event}_event'  # Collection name for the event
    db_event_collection = db_events.get_collection(event_name)
    nbUsers = db_event_collection.count_documents({})  # Count the number of users in the event

    all_data = db_event_collection.find({})  # Retrieve all users from the event
    data_list = list(all_data)  # Convert MongoDB cursor to a list

    for document in data_list:
        del document['_id']  # Remove internal MongoDB ID from each document
        if 'user_id' in document:
            del document['user_id']

    result = {
        "event": event,
        "nb_users": nbUsers,  # Number of users
        "users": data_list  # List of users
    }
    return result
# Retrieves all available events and filters expired ones
def get_Available_Events(db_infos, db_events, db_users, admin=False):  # Effectuer une requête GET

    api_url = "https://tekiens.net/api/events"


    try:
        response = requests.get(api_url, params={})
        response.raise_for_status()  # Vérifie que la requête s'est bien passée (status code 200)
        data = response.json()  # Les données renvoyées sont au format JSON

        if data.get("success"):
            events = data.get("data", [])
            old_events = events
            for event in events:
                if not db_infos.infos_event.find_one({"old_id": event["id"]}):
                    if event["asso_id"] == "bde":
                        event["asso_id"] = "bde_cergy"
                    if event["asso_id"] == "bds":
                        event["asso_id"] = "bds_cergy"
                    event["old_id"] = event.pop("id")
                    event["id"] = str(uuid.uuid4())  # Générer un ID unique pour l'événement

                    event["asso"] = event.pop("asso_id").upper()
                    event["event"] = event.pop("title")
                    if event.get("poster"):  # Vérifie si "poster" existe et n'est pas None
                        base_url = "https://tekiens.net"
                        event["image"] = f"{base_url}{event.pop('poster')}"
                    else:
                        event.pop("poster", None)  # Supprime la clé "poster" si elle existe
                        event["image"] = ""
                    event["desc"] = event.pop("description")
                    event["emoji"] = "😍"
                    event["lieu"] = event.pop("place")
                    if event.get("price"):  # Vérifie si "poster" existe et n'est pas None
                        event["prix"] = str(event.pop('price'))
                    else:
                        event.pop("price", None)  # Supprime la clé "poster" si elle existe
                        event["prix"] = "0"
                    date_format = "%Y-%m-%d %H:%M:%S"
                    date_obj = datetime.strptime(event.pop('date'), date_format)
                    timestamp = int(date_obj.timestamp())
                    event["timestamp"] = timestamp
                    event.pop("createDate")
                    event.pop("lastUpdateDate")
                    event.pop("capacity")
                    event.pop("access")
                    event.pop("status")
                    event.pop("duration")
                    event["creator"] = "Cergy"
                    event["scheduled_bool"] = False
                    event["scheduled_time"] = None
                    add_event_to_db(event, db_events, db_infos, db_users)
                    event.pop("_id")
        # Affiche le JSON unique de façon lisible
        else:
            print(f"Erreur lors de la récupération des événements : {data.get('error')}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête : {e}")



    # nbEvents = len(filtered_events_list)  # Count non-expired events
    
    # # Prepare the result to return
    # result = {
    #     "nb_events": nbEvents,  # Number of non-expired events
    #     "nb_event_scheduled" : nbEventScheduled,
    #     "nb_events_expired": nbEventsTotal - (nbEvents+nbEventScheduled),  # Number of expired events
    #     "events": filtered_events_list,  # List of available events
    #     "events_expired": filtered_events_expired_list  # List of expired events
    # }
    return events


# Decodes the creator's information using JWT
def decodeEncodedCreator(encoded_jwt, key):
    try:
        payload = jwt.decode(encoded_jwt, key, algorithms=["HS256"])  # Decode JWT with the provided key
        return payload["encoded_creator"]  # Extract creator information
    except jwt.exceptions.DecodeError as e:
        print("Error decoding JWT token:", e)
        return False  # Return False if decoding fails


def add_Event(event, timestamp, lieu, desc, prix, emoji, link, asso, image, encoded_creator, key, db_events, db_infos, db_users, scheduled=False, scheduled_time=None):
    # Décoder le créateur
    creator = decodeEncodedCreator(encoded_creator, key)  
    if not creator:
        return {"status": "Invalid creator"}

    id_event = str(uuid.uuid4())  # Générer un ID unique pour l'événement

    # Détails de l'événement
    result = {
        "id": id_event,
        "event": event,
        "asso": asso,
        "timestamp": int(timestamp),
        "emoji": emoji,
        "lieu": lieu,
        "link": link,
        "desc": desc,
        "image": image,
        "prix": prix,
        "creator": creator,
        "scheduled_bool": scheduled,
        "scheduled_time":scheduled_time

    }


    return add_event_to_db(result, db_events, db_infos, db_users)

def add_event_to_db(event_data, db_events, db_infos, db_users):
    
    id_event = event_data["id"]
    creator = event_data["creator"]
    db_collection_name = f'{id_event}_event' 

    # Gestion des événements existants
    if db_collection_name in db_events.list_collection_names():
        event_info_removed = db_infos.infos_event.delete_one({"creator": creator, "id": id_event})
        if event_info_removed.deleted_count > 0 or creator == "admin":
            db_events.drop_collection(db_collection_name)
            db_events.create_collection(db_collection_name)
            db_infos.infos_event.insert_one(event_data)
            if event_data["scheduled_time"] == None and event_data["scheduled_bool"] == False:
                print("Envoyer notif")
                # send_New_Event_notification(event_data["event"], event_data["asso"], event_data["emoji"], event_data["desc"], db_infos, db_users)
            return {"status": "Event updated", "event_id": id_event}
        else:
            return {"status": "Wrong user"}
    else:
        # Créer un nouvel événement
        db_events.create_collection(db_collection_name)
        db_infos.infos_event.insert_one(event_data)
        if event_data["scheduled_time"] == None  and event_data["scheduled_bool"] == False:
            # send_New_Event_notification(event_data["event"], event_data["asso"], event_data["emoji"], event_data["desc"], db_infos, db_users)
            print("Envoyer notif")
        return {"status": "Event added", "event_id": id_event}



# Modifies an existing event's details
def modify_Event(id_event, event, timestamp, lieu, desc, prix, emoji, link, asso, image, encoded_creator, key, db_events, db_users ,db_infos):
    creator = decodeEncodedCreator(encoded_creator, key)  # Decode creator from JWT
    
    if not creator:
        return {"status": "Invalid creator"}
    
    db_collection_name = f'{id_event}_event'  # Collection name for the event
    
    if db_collection_name in db_events.list_collection_names():
        existing_event = db_infos.infos_event.find_one({"id": id_event})  # Find the event in the database
        if existing_event and (existing_event["creator"] == creator or creator == "admin"):
            if timestamp > time.time() and existing_event["timestamp"] != timestamp : # On modifie la date de l'event
                send_New_Event_notification(event,asso,emoji,desc,db_infos,db_users)
            
            updated_event = {
                "id": id_event,
                "event": event,
                "asso": asso,
                "timestamp": int(timestamp),
                "emoji": emoji,
                "lieu": lieu,
                "image": image,
                "link": link,
                "desc": desc,
                "prix": prix,
                "creator": existing_event["creator"]  # Keep the original creator
            }
            db_infos.infos_event.update_one({"id": id_event}, {"$set": updated_event})  # Update event info                
            return {"status": "Event updated"}
        else:
            return {"status": "Permission denied, invalid creator"}
    else:
        return {"status": "Event not found"}

# Removes an event and its data, verifies the creator or admin
def remove_Event(id_event, event, encoded_creator, key, db_events,db_users,db_infos):
    creator = decodeEncodedCreator(encoded_creator, key)  # Decode creator from JWT

    db_collection_name = f'{id_event}_event'
    if db_collection_name in db_events.list_collection_names():
        existing_event = db_infos.infos_event.find_one({"creator": creator, "id": id_event})

        if existing_event["timestamp"] > time.time():
            send_Remove_Event_notification(event,id_event,db_events,db_users,db_infos)

        event_collection = db_events[db_collection_name]
        info_removed = db_infos.infos_event.delete_one({"creator": creator, "id": id_event})  # Delete event info
        if info_removed.deleted_count > 0 or creator == "admin":
            if creator == "admin":
                db_infos.infos_event.delete_one({"id": id_event})  # Admin can remove any event
            event_collection.drop()  # Drop the event collection
            return {"event_removed": True}
    return {"event_removed": False}
