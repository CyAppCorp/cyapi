from librairies import *
from events import decodeEncodedCreator  # Custom function to decode the creator information

# Function to get available polls
def get_Available_Polls(db_polls):
    # Fetch all poll documents from the database collection 'polls'
    all_data = db_polls.polls.find({})
    polls_list = list(all_data)  # Convert cursor to list
    filtered_polls_list = []  # List to store active polls (not expired)
    filtered_polls_expired_list = []  # List to store expired polls
    nbPollsTotal = db_polls.polls.count_documents({})  # Total number of polls in the collection

    # Loop through each poll document in the list
    for document in polls_list:
        del document['_id']  # Remove MongoDB's internal '_id' field for cleaner output
        # Check if poll is expired (i.e., timestamp is less than the current time + 1 hour)
        if document['timestamp'] < (time.time() + 3600):
            filtered_polls_expired_list.append(document)  # If expired, add to the expired list
            continue  # Skip the rest and go to the next poll
        filtered_polls_list.append(document)  # If not expired, add to the active poll list
    
    nbPolls = len(filtered_polls_list)  # Count the number of active polls
    
    # Prepare the result as a dictionary
    result = {
        "nb_polls": nbPolls,  # Number of active polls
        "nb_polls_expired": nbPollsTotal - nbPolls,  # Number of expired polls
        "polls" : filtered_polls_list,  # Active polls list
        "polls_expired" : filtered_polls_expired_list  # Expired polls list
    }
    
    return result  # Return the result dictionary


# Function to add a new poll
def add_Poll(title, options, hide_bool, timestamp, desc, asso, encoded_creator, key, db_polls):
    # Decode the creator information using the custom function
    creator = decodeEncodedCreator(encoded_creator, key)

    # If decoding fails, return an error message
    if not creator:
        return {"status": "Fuck la CORP"}  # This is an intentional error message for unauthorized access
    
    # Generate a unique ID for the poll
    id_poll = str(uuid.uuid4())

    print(id_poll)  # Print the generated poll ID (for debugging purposes)

    # Create the poll document to insert into the database
    result = {
        "id_poll" : id_poll,  # Unique poll ID
        "title": title,  # Title of the poll
        "hide_votes" : hide_bool,  # Boolean to hide votes or not
        "asso" : asso,  # Association or group related to the poll
        "timestamp" : int(timestamp),  # Expiration timestamp
        "desc": desc,  # Poll description
        "creator": creator  # Creator of the poll
    }

    # Create a list to store poll options
    options_array = []
    for option in options:
        option_details = {
            "id" : str(uuid.uuid4()),  # Unique ID for each option
            "text" : option,  # Text of the option
            "num_votes" : 0  # Initial number of votes (set to 0)
        }
        options_array.append(option_details)  # Add option to the array

    # Add the options array to the poll document
    result["options"] = options_array

    # Insert the poll document into the 'polls' collection in the database
    db_polls.polls.insert_one(result)
    result.pop('_id', None)  # Remove MongoDB's internal '_id' before returning the result
    return result  # Return the created poll


# Function to remove a poll
def remove_Poll(id_poll, encoded_creator, key, db_polls):
    # Decode the creator information using the custom function
    creator = decodeEncodedCreator(encoded_creator, key)

    # If decoding fails, return an error message
    if not creator:
        return {"status": "Fuck la CORP"}  # Unauthorized user error message
    else:
        # If the user is an admin, they can delete any poll by its ID
        if creator == "admin":
            poll_removed = db_polls.polls.delete_one({"id_poll" : id_poll})
        else:
            # Otherwise, only the creator of the poll can delete their own poll
            poll_removed = db_polls.polls.delete_one({"creator": creator, "id_poll" : id_poll})
        
        # Return a status indicating whether the poll was successfully removed
        return {"status" : (poll_removed.deleted_count > 0)}


# Function to add a user's vote to a poll
def add_user_vote(id_poll, id_options, db_polls):
    # Find the poll document by its unique ID
    result = db_polls.polls.find_one({"id_poll": id_poll})

    i = 0
    # Loop through the options of the poll
    for option in result["options"]:
        # If the option ID matches the provided option ID, increment the vote count
        if option["id"] == id_options:
            result["options"][i]["num_votes"] += 1  # Increment the vote count
        i += 1  # Move to the next option
    
    # Update the poll document in the database with the new vote count
    db_polls.polls.update_one({"id_poll": id_poll}, {"$set": result})

    # Return a success message
    return {"message": "User vote successfully added"}

