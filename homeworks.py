from librairies import *
from auth import authName

# Function to add a new homework entry to the database
def add_Homework(db_homeworks, title, subject, group, desc, timestamp, user_id, db_users):
    id = uuid.uuid4()  # Generate a unique ID for the homework

    creator = authName(user_id,db_users)

    if creator == None:
        return {"status" : "Not Updated"}

    # Construct the homework document
    result = {
        "id": str(id),  # Convert UUID to a string
        "title": title,  # Title of the homework
        "subject": subject,  # Subject related to the homework
        "group": group,  # Group(s) for which the homework is intended
        "desc": desc,  # Description of the homework
        "timestamp": int(timestamp),  # Timestamp indicating due date/time
        "creator": creator  # The creator (teacher/author) of the homework
    }

    # Debug print to show what is being added
    print(f"Title: {result['title']} | Subject: {result['subject']} | Group: {result['group']} | Creator: {result['creator']} | Desc: {result['desc']}")

    db_homeworks.homeworks.insert_one(result)  # Insert the homework into the MongoDB collection
    result.pop('_id', None)  # Remove MongoDB internal '_id' field from the returned document
    return result  # Return the inserted homework data

# Function to remove a homework by its ID, checking if the creator is the same
def remove_Homework(db_homeworks, id, user_id, db_users):

    creator = authName(user_id,db_users)

    if creator == None:
        return {"status" : "Not Updated"}

    # Remove the homework document that matches both the ID and the creator
    homework_removed = db_homeworks.homeworks.delete_one({"creator": creator, "id": id})
    
    # Return the status based on whether the homework was deleted or not
    return {"status": (homework_removed.deleted_count > 0)}

# Function to retrieve all homework for a specific group
def get_Homeworks(db_homeworks, group):
    all_data = db_homeworks.homeworks.find({})  # Retrieve all homework documents from the database
    homeworks_list = list(all_data)  # Convert the MongoDB cursor to a list
    filtered_homeworks_list = []  # List to store homeworks specific to the group
    nbHomeworks = 0  # Counter for the number of homeworks for the group

    for document in homeworks_list:
        del document['_id']  # Remove internal MongoDB ID from each document
        if group in document['group']:  # Check if the homework is intended for the specified group
            nbHomeworks += 1  # Increment the homework count
            filtered_homeworks_list.append(document)  # Add the homework to the filtered list
    
    # Construct the result with the number of homeworks and the list of filtered homeworks
    result = {
        "nb_homeworks": nbHomeworks,  # Number of homeworks found
        "homeworks": filtered_homeworks_list  # List of homeworks for the group
    }
    
    return result

# Function to edit an existing homework's details
def edit_Homeworks(db_homeworks, modified_title, modified_subject, modified_group, modified_desc, modified_timestamp, modified_user_id, modified_id, db_users):

    modified_creator = authName(modified_user_id,db_users)

    if modified_creator == None:
        return {"status" : "Not Updated"}
    
    # Find the homework by its ID
    result = db_homeworks.homeworks.find_one({"id": modified_id})
    
    if result:
        # If the homework is found, update its details
        updated_data = {
            "title": modified_title,  # New or unchanged title
            "subject": modified_subject,  # New or unchanged subject
            "group": modified_group,  # New or unchanged group(s)
            "desc": modified_desc,  # New or unchanged description
            "timestamp": modified_timestamp,  # New or unchanged timestamp
            "creator": modified_creator  # New or unchanged creator (teacher)
        }

        # Update the homework in the database with the new values
        db_homeworks.homeworks.update_one(
            {"id": modified_id},  # Match homework by ID
            {"$set": updated_data}  # Update only the specified fields
        )

        updated_data["id"] = modified_id  # Preserve the original homework ID
        return updated_data  # Return the updated homework data
    else:
        # Return an error if the homework with the specified ID doesn't exist
        return {"error": "Homework not existing"}
