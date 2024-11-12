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

# Adds a new event to the database, with admin or creator verification
def add_Event(event, timestamp, lieu, desc, prix, emoji, link, asso, image, encoded_creator, key, db_events, db_infos,db_users):
    creator = decodeEncodedCreator(encoded_creator, key)  # Decode creator from JWT
    if not creator:
        return {"status": "Invalid creator"}

    id_event = str(uuid.uuid4())  # Generate a unique ID for the event

    # Build event details
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

    db_collection_name = f'{id_event}_event'  # Collection name for the event
    if db_collection_name in db_events.list_collection_names():  # If an event with the same name exists
        event_info_removed = db_infos.infos_event.delete_one({"creator": creator, "id": id_event})  # Remove the old event info
        if event_info_removed.deleted_count > 0 or creator == "admin":
            if creator == "admin" and not event_info_removed.deleted_count > 0: # Admin can remove any event but the event is not originally created by him
                event_creator = db_infos.infos_event.find_one({"id": id_event})["creator"]
                db_infos.infos_event.delete_one({"creator": event_creator, "id": id_event})  # Delete the event by creator
                result["creator"] = event_creator
            else: # Admin can remove any event and the event is originally created by him
                result["creator"] = "admin"
            db_events.drop_collection(db_collection_name)  # Drop the old collection
            db_events.create_collection(db_collection_name)  # Create a new collection for the event
            db_infos.infos_event.insert_one(result)  # Insert new event info
            result.pop('_id', None)
            return result
        else:
            return {"status": "Wrong user"}
    else:
        db_events.create_collection(db_collection_name)  # Create a new collection for the event
        db_infos.infos_event.insert_one(result)  # Insert event info
        result.pop('_id', None)

    send_New_Event_notification(event,asso,emoji,desc,db_infos,db_users)
   

    return result

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
