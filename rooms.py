from librairies import *  # Import necessary libraries
from auth import authName

# Function to get the list of rooms that are currently booked
def get_Rooms(db_infos):
    # Fetch all room booking data from the 'rooms_booking' collection
    all_data = db_infos.rooms_booking.find({})
    rooms_list = list(all_data)  # Convert cursor to a list to process it
    result = {}  # Initialize an empty result dictionary to hold active bookings

    # Iterate through each room booking document
    for document in rooms_list:
        del document['_id']  # Remove MongoDB's internal '_id' field for cleaner output
        # Check if the room booking is still valid (until time is in the future)
        if document['until'] > time.time():
            # If valid, add it to the result dictionary using room name as key
            result[document['room']] = {
                "creator": document['creator'],  # Store the creator of the booking
                "until": document['until']  # Store the expiration time of the booking
            }
        else:
            # If the booking has expired, delete the document from the database
            db_infos.rooms_booking.delete_one(document)

    # If no active bookings found, set the result to indicate no rooms available
    if not result:
        result = {"status": 0}  # 0 indicates no active rooms

    return result  # Return the result dictionary containing active bookings


# Function to add a room booking
def add_Rooms(db_infos, room, until, user_id, db_users):

    creator = authName(user_id,db_users)

    if creator == None:
        return {"status" : "Not Updated"} 

    # Check if the user has any warnings
    user_warn = db_infos.user_warns.find_one({"creator": creator})
    
    # Verify if a document was found for the user
    if user_warn and user_warn.get("nb_warn", 0) > 4:
        # If user has more than 4 warnings, they cannot book a room
        return {"error": "Too many warns, user can't book a room"}

    # Check if the specified room is already booked
    is_room_booked = db_infos.rooms_booking.find_one({"room": room})    

    # Create the room booking data
    result = {
        "room": room,  # Room name
        "until": until,  # Expiration timestamp for the booking
        "creator": creator,  # Creator of the booking
    }

    # If the room is already booked, update the existing booking
    if is_room_booked:
        db_infos.rooms_booking.update_one(
            {"room": room}, 
            {"$set": result}  # Update the existing booking data
        )
    else:
        # If the room is not booked, insert a new booking
        db_infos.rooms_booking.insert_one(result)

    result.pop('_id', None)  # Remove the internal '_id' field before returning
    return result  # Return the room booking details


# Function to delete a room booking
def delete_Rooms(db_infos, room):
    # Attempt to remove the room booking from the database
    room_removed = db_infos.rooms_booking.delete_one({"room": room})
    # Return status indicating whether the removal was successful
    return {"status": (room_removed.deleted_count > 0)}  # True if a room was removed


# Function to warn a user (increment their warning count)
def warn_User(db_infos, user_id, db_users):

    creator = authName(user_id,db_users)

    if creator == None:
        return {"status" : "Not Updated"}
        
    # Check if the user has already been warned
    is_user_warned = db_infos.user_warns.find_one({"creator": creator})    

    # Prepare the result data
    result = {
        "creator": creator,  # Creator (user) who is being warned
        "nb_warn": 1  # Start with 1 warning
    }
    
    # If the user has been warned before, increment their warning count
    if is_user_warned:
        result["nb_warn"] = is_user_warned["nb_warn"] + 1

        # Update the user's warning count in the database
        db_infos.user_warns.update_one(
            {"creator": creator}, 
            {"$set": result}  # Update the warning count
        )
    else:
        # If the user is new, insert a new warning document
        db_infos.user_warns.insert_one(result)

    result.pop('_id', None)  # Remove the internal '_id' field before returning
    return result  # Return the updated warning information
