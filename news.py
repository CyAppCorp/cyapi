from librairies import *
from events import decodeEncodedCreator  # Importing function to decode creator information

# Function to retrieve available news articles
def get_Available_News(db_news):
    # Fetch all news articles from the database collection 'news'
    all_data = db_news.news.find({})
    news_list = list(all_data)  # Convert cursor to list
    filtered_news_list = []  # List to store active news articles (not expired)
    filtered_news_expired_list = []  # List to store expired news articles
    nbNewsTotal = db_news.news.count_documents({})  # Total number of news articles in the collection

    # Loop through each news document in the list
    for document in news_list:
        del document['_id']  # Remove MongoDB's internal '_id' field for cleaner output
        # Check if the news article is expired (timestamp less than the current time + 1 hour)
        if document['timestamp'] < (time.time() + 3600):
            filtered_news_expired_list.append(document)  # Add to expired list if it has expired
            continue  # Skip to the next news article
        filtered_news_list.append(document)  # Add to active news list if it hasn't expired
    
    nbNews = len(filtered_news_list)  # Count the number of active news articles
    
    # Prepare the result as a dictionary
    result = {
        "nb_news": nbNews,  # Number of active news articles
        "nb_news_expired": nbNewsTotal - nbNews,  # Number of expired news articles
        "news": filtered_news_list,  # Active news articles
        "news_expired": filtered_news_expired_list  # Expired news articles
    }
    
    return result  # Return the result dictionary


# Function to add a new news article
def add_News(title, timestamp, desc, asso, link, encoded_creator, key, db_news):
    # Decode the creator information using the custom function
    creator = decodeEncodedCreator(encoded_creator, key)
    if not creator:
        return {"status": "Fuck la CORP"}  # Unauthorized access error message
    
    # Generate a unique ID for the news article
    id_news = str(uuid.uuid4())

    # Create the news document to insert into the database
    result = {
        "id_news": id_news,  # Unique news article ID
        "title": title,  # Title of the news article
        "asso": asso,  # Association or group related to the news
        "timestamp": int(timestamp),  # Expiration timestamp
        "desc": desc,  # News description
        "link": link,  # Link to the news article
        "creator": creator  # Creator of the news article
    }

    # Insert the news document into the 'news' collection in the database
    db_news.news.insert_one(result)
    result.pop('_id', None)  # Remove MongoDB's internal '_id' before returning the result
    return result  # Return the created news article


# Function to remove a news article
def remove_News(id_news, encoded_creator, key, db_news):
    # Decode the creator information using the custom function
    creator = decodeEncodedCreator(encoded_creator, key)

    # If decoding fails, return an error message
    if not creator:
        return {"status": "Fuck la CORP"}  # Unauthorized user error message
    else:
        # If the user is an admin, they can delete any news article by its ID
        if creator == "admin":
            news_removed = db_news.news.delete_one({"id_news": id_news})
        else:
            # Otherwise, only the creator of the news article can delete it
            news_removed = db_news.news.delete_one({"creator": creator, "id_news": id_news})
        
        # Return a status indicating whether the news article was successfully removed
        return {"status": (news_removed.deleted_count > 0)}


# Function to modify an existing news article
def modify_News(id_news, modified_news, modified_timestamp, modified_link, modified_desc, modified_asso, encoded_creator, key, db_news):
    # Decode the creator information using the custom function
    creator = decodeEncodedCreator(encoded_creator, key)
    
    # If decoding fails, return an error message
    if not creator:
        return {"status": "Créateur invalide"}  # Invalid creator error message
    
    # Find the existing news article by its unique ID
    existing_news = db_news.news.find_one({"id_news": id_news})
    
    # If no news article found, return an error message
    if not existing_news:
        return {"status": "Actualité non trouvée"}  # News article not found error message
    else:
        # Prepare updated data for the news article
        updated_data = {
            "title": modified_news,  # Updated title
            "asso": modified_asso,  # Updated association
            "timestamp": int(modified_timestamp),  # Updated expiration timestamp
            "desc": modified_desc,  # Updated description
            "link": modified_link,  # Updated link
            "creator": creator  # Creator remains the same
        }

        # Update the news document in the database with the new data
        db_news.news.update_one(
            {"id_news": id_news}, 
            {"$set": updated_data}
        )
        
        updated_data["id_news"] = id_news  # Preserve the custom identifier
        return updated_data  # Return the updated news article data
