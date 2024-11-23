from librairies import *
from auth import authName, send_New_Event_notification, send_Remove_Event_notification
from scheduler_config import scheduler  # Importer le scheduler depuis le fichier de configuration
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
        del document['user_id']

    result = {
        "event": event,
        "nb_users": nbUsers,  # Number of users
        "users": data_list  # List of users
    }
    return result

# Retrieves all available events, filters expired ones
def get_Available_Events(db_infos):
    all_data = db_infos.infos_event.find({})  # Get all events from the database
    events_list = list(all_data)
    nbEventsTotal = db_infos.infos_event.count_documents({})  # Total number of events

    filtered_events_list = []
    filtered_events_expired_list = []

    for document in events_list:
        del document['_id']  # Remove MongoDB ID
        if document['timestamp'] < (time.time() - 3600):  
            filtered_events_expired_list.append(document)
            continue
        filtered_events_list.append(document)  # Add to the available events list
    
    nbEvents = len(filtered_events_list)  # Count non-expired events
    
    result = {
        "nb_events": nbEvents,  # Number of available events
        "nb_events_expired": nbEventsTotal - nbEvents,  # Number of expired events
        "events": filtered_events_list,  # Available events
        "events_expired": filtered_events_expired_list  # Expired events
    }
    return result

# Decodes the creator's information using JWT
def decodeEncodedCreator(encoded_jwt, key):
    try:
        payload = jwt.decode(encoded_jwt, key, algorithms=["HS256"])  # Decode JWT with the provided key
        return payload["encoded_creator"]  # Extract creator information
    except jwt.exceptions.DecodeError as e:
        print("Error decoding JWT token:", e)
        return False  # Return False if decoding fails

# Fonction qui planifie l'insertion d'un événement
def schedule_event(event_data, scheduled_time ,db_events, db_infos, db_users):
    try:
        scheduled_datetime = datetime.fromisoformat(scheduled_time)
    except ValueError:
        print(f"Erreur : format de date invalide '{scheduled_time}'.")
        return

    trigger = DateTrigger(run_date=scheduled_datetime)
    scheduler.add_job(add_event_to_db, trigger, args=[event_data, db_events, db_infos, db_users], id=event_data["id"])



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
        "creator": creator
    }

    if scheduled and scheduled_time:
        # Programmer l'événement pour être ajouté plus tard
        schedule_event(result, scheduled_time,db_events, db_infos, db_users)
        return {"status": "Event scheduled", "event_id": id_event}

    # Ajouter l'événement dans la base de données immédiatement
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
            send_New_Event_notification(event_data["event"], event_data["asso"], event_data["emoji"], event_data["desc"], db_infos, db_users)
            return {"status": "Event updated", "event_id": id_event}
        else:
            return {"status": "Wrong user"}
    else:
        # Créer un nouvel événement
        db_events.create_collection(db_collection_name)
        db_infos.infos_event.insert_one(event_data)
        send_New_Event_notification(event_data["event"], event_data["asso"], event_data["emoji"], event_data["desc"], db_infos, db_users)
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
            if existing_event["timestamp"] != timestamp:
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
        send_Remove_Event_notification(event,id_event,db_events,db_users,db_infos)
        event_collection = db_events[db_collection_name]
        info_removed = db_infos.infos_event.delete_one({"creator": creator, "id": id_event})  # Delete event info
        if info_removed.deleted_count > 0 or creator == "admin":
            if creator == "admin":
                db_infos.infos_event.delete_one({"id": id_event})  # Admin can remove any event
            event_collection.drop()  # Drop the event collection
            return {"event_removed": True}
    return {"event_removed": False}
