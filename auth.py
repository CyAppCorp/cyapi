from librairies import *


def authUser(token,username,user_fullname,user_email,db_infos,db_users):

    existing_user = db_users.users.find_one({"username": username, "user_email": user_email})

    if existing_user:
        # Si l'utilisateur existe déjà, renvoie l'ID existant
        return {"user_id": str(existing_user["user_id"])}

    user_id = str(uuid.uuid4())

    result = {
        "user_id": user_id,
        "token": token,
        "username": username,      
        "user_fullname": user_fullname ,   
        "user_email": user_email,
    }

    response = {
        "user_id" : user_id
    }

    db_users.users.insert_one(result)

    add_Followers_Asso(user_id,"BDE",db_infos,db_users)

    return response

def authName(user_id,db_users):
    user = db_users.users.find_one({"user_id": user_id}, {"user_fullname": 1})
    if user:
        return user["user_fullname"] 
    else:
        return None

def add_Asso(asso,desc, db_infos):

    
    # Create the asso document to insert into the database
    result = {
        "asso" : asso,  # Association name
        "desc": desc,  # Association description
        "followers" : [], # Assocation Followers
    }

    # Insert the asso  into the 'infos' collection in the database
    db_infos.followers_event.insert_one(result)
    result.pop('_id', None)  # Remove MongoDB's internal '_id' before returning the result
    return result  # Return the created poll


def add_Followers_Asso(user_id,asso,db_infos,db_users):
    
    existing_asso = db_infos.followers_event.find_one({"asso": asso})
    existing_user = db_users.users.find_one({"user_id": user_id})

    if not existing_asso:
        return {"status": "Association Not Found"}
    if not existing_user:
        return {"status": "User Not Found"}

    new_follower = {
            "user_id": existing_user["user_id"],
            "user_fullname": existing_user["user_fullname"]
        }

    
    existing_followers = existing_asso.get("followers", [])

    if not any(follower['user_id'] == new_follower['user_id'] for follower in existing_followers):
        db_infos.followers_event.update_one(
            {"asso": asso},
            {"$push": {"followers": new_follower}}
        )
        return {"status": "Follower added successfully"}
    else:
        return {"status": "Follower already exists"}

    return {"status": -1 }


def remove_Followers_Asso(user_id,asso,db_infos,db_users):
    
    existing_asso = db_infos.followers_event.find_one({"asso": asso})
    existing_user = db_users.users.find_one({"user_id": user_id})

    if not existing_asso:
        return {"status": "Association Not Found"}
    if not existing_asso:
        return {"status": "Association Not Found"}

    result = db_infos.followers_event.update_one(
        {"asso": asso},
        {"$pull": {"followers": {"user_id": user_id}}}
    )

    # Check if the update was successful
    if result.modified_count > 0:
        return {"status": "Follower removed successfully"}
    else:
        return {"status": "Follower not found in the association"}



    return {"status": -1 }


def users_Followers_Asso(user_id,db_infos,db_users):

    followed_by_user = db_infos.followers_event.find({"followers.user_id": user_id})

    asso_names = []

    for item in followed_by_user :
        asso_names.append(item["asso"])
    
    result = {"followers_assos" : asso_names}
    
    return result 



def send_push_notification(tokens, title, body):
    # Parcourir la liste des tokens et envoyer la notification à chaque utilisateur
    for token in tokens:
        if token is not None:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                token=token,
            )
        try:
            # Envoyer le message
            response = messaging.send(message)
        except Exception as e:
            print(f'Failed to send message to {token}:', e)




def send_New_Event_notification(event,asso,emoji,desc,db_infos,db_users):
    
    existing_asso = db_infos.followers_event.find_one({"asso": asso})
    device_tokens = []  


    # Récupération du tableau "followers" si le existing_asso existe
    if existing_asso and "followers" in existing_asso:
        followers = existing_asso["followers"]
        for follower in followers:
            try:
                user_id = follower['user_id']  # Try to get user ID 
                device_tokens.append(idToFCMToken(user_id,db_users,False))

            except Exception as e:
                user_id = follower['user_fullname'] # Old API fix
                device_tokens.append(idToFCMToken(user_id,db_users,True))

    else:
        print("Document non trouvé ou le champ 'followers' est absent.")

    notification_title = f' {emoji} {asso} | {event} '
    notification_body = desc
   
    send_push_notification(device_tokens, notification_title, notification_body)

def idToFCMToken(user_id,db_users,old_api_bool):
    if old_api_bool:
        existing_user = db_users.users.find_one({"user_fullname": user_id})
    else:
        existing_user = db_users.users.find_one({"user_id": user_id})
    return existing_user['token']


def send_Remove_Event_notification(event,id_event,db_events,db_users,db_infos):
    db_collection_name = f'{id_event}_event'  # Collection name for the event
    device_tokens = []

    if db_collection_name in db_events.list_collection_names():
        event_collection = db_events[db_collection_name]
        for user in event_collection.find():
            try:
                user_id = user['user_id']  # Try to get user ID 
                device_tokens.append(idToFCMToken(user_id,db_users,False))
            except Exception as e:
                user_id = user['user'] # Old API fix
                device_tokens.append(idToFCMToken(user_id,db_users,True))



    notification_title = f"⚠️ Annulation Évenement ⚠️"
    notification_body = f"L'évenement {event} a été annulé"
   
    send_push_notification(device_tokens, notification_title, notification_body)

