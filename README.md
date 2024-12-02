# CYAPI - REST API FOR CYAPP



## "auth_token"

```json
{
    "usage": "auth_token",
    "token": "abcd1234",
    "username": "john_doe",
    "user_fullname": "John Doe",
    "user_email": "john.doe@example.com"
}

```

## "add_asso"

```json
{
    "usage": "add_asso",
    "asso": "BDE",
    "desc": "Bureau des étudiants"
}

```

## "add_followers_asso"

```json
{
    "usage": "add_followers_asso",
    "user_id": "12345",
    "asso": "BDE"
}

```


## "remove_followers_asso"

```json
{
    "usage": "remove_followers_asso",
    "user_id": "12345",
    "asso": "BDE"
}

```

## "users_followers_asso"

```json
{
    "usage": "users_followers_asso",
    "user_id": "12345"
}

```


## "add_user"

```json
{
    "usage": "add_user",
    "id_event": "6789",
    "user_id": "12345"
}

```


## "remove_user"

```json
{
    "usage": "remove_user",
    "id_event": "6789",
    "user_id": "12345"
}

```

## "users"

```json
{
    "usage": "users",
    "id_event": "6789"
}

```


## "available_events"

```json
{
    "usage": "available_events"
}

```


## "add_event"

```json
{
    "usage": "add_event",
    "event": "Concert de Noël",
    "timestamp": 1645963235,
    "lieu": "Salle des fêtes",
    "desc": "Concert de Noël de l'association BDE",
    "prix": "Gratuit",
    "emoji": "🎉",
    "link": "https://www.exemple.com/evenement",
    "asso": "BDE",
    "image": "https://www.exemple.com/image.jpg",
    "encoded_creator": "abcd1234"
}

```


## "modify_event"

```json
{
    "usage": "modify_event",
    "id_event": "6789",
    "event": "Mise à jour du Concert de Noël",
    "timestamp": 1645963235,
    "lieu": "Salle des fêtes",
    "desc": "Mise à jour de l'événement",
    "prix": "Gratuit",
    "emoji": "🎉",
    "link": "https://www.exemple.com/evenement",
    "asso": "BDE",
    "image": "https://www.exemple.com/image.jpg",
    "encoded_creator": "abcd1234"
}

```

## "remove_event"

```json
{
    "usage": "remove_event",
    "id_event": "event_12345",
    "encoded_creator": "abcd1234"
}

```

## "reset_users"

```json
{
    "usage": "reset_users",
    "id_event": "event_12345",
    "encoded_creator": "abcd1234"
}

```

## "add_homework"

```json
{
    "usage": "add_homework",
    "title": "Devoir 1",
    "subject": "Mathématiques",
    "group": "Groupe A",
    "desc": "Exercice sur les équations",
    "timestamp": 1645963235,
    "user_id": "user_12345"
}

```


## "remove_homework"

```json
{
    "usage": "remove_homework",
    "id": "homework_12345",
    "user_id": "user_12345"
}

```


## "get_homework"

```json
{
    "usage": "get_homework",
    "group": "P1G1"
}

```

## "edit_homework"

```json
{
    "usage": "edit_homework",
    "id": "homework_12345",
    "title": "Devoir 1",
    "subject": "Mathématiques",
    "group": "P1G1",
    "desc": "Exercice sur les équations",
    "timestamp": 1645963235,
    "user_id": "user_12345"
}

```

## "get_booked_rooms"

```json
{
    "usage": "get_booked_rooms"
}

```

## "book_room"

```json
{
    "usage": "book_room",
    "room": "Salle 101",
    "until": "2024-12-01T18:00:00",
    "user_id": "user_12345"
}

```

## "delete_room"

```json
{
    "usage": "delete_room",
    "room": "Salle 101"
}

```

## "warn_user"

```json
{
    "usage": "warn_user",
    "user_id": "user_12345"
}

```

## "available_polls"

```json
{
    "usage": "available_polls"
}

```

## "add_poll"

```json
{
    "usage": "add_poll",
    "title": "Quel événement préférez-vous ?",
    "options": ["Concert", "Conférence", "Atelier"],
    "hide_bool": true,
    "timestamp": 1645963235,
    "desc": "Sondage sur les événements futurs",
    "asso": "BDE",
    "encoded_creator": "abcd1234"
}

```

## "add_user_vote"

```json
{
    "usage": "add_user_vote",
    "id_poll": "poll_12345",
    "id_options": "option_1"
}

```

## "remove_poll"

```json
{
    "usage": "remove_poll",
    "id_poll": "poll_12345",
    "encoded_creator": "abcd1234"
}

```

## "add_news"

```json
{
    "usage": "add_news",
    "title": "Nouvelle actualité",
    "timestamp": 1645963235,
    "desc": "Nouvelle importante à lire",
    "asso": "BDE",
    "link": "https://www.exemple.com/nouvelle",
    "encoded_creator": "abcd1234"
}

```

## "available_news"

```json
{
    "usage": "available_news"
}

```

## "remove_news"

```json
{
    "usage": "remove_news",
    "id_news": "12345",
    "encoded_creator": "abcd1234"
}

```

## "modify_news"

```json
  {
    "id_news": "12345",
    "usage": "modify_news",
    "desc": "Nouvelle mise à jour sur le projet X",
    "link": "https://www.exemple.com/nouvelle-x",
    "title": "Mise à jour du projet X",
    "timestamp": 1645963235,
    "asso": "BDE",
    "encoded_creator": "abcd1234"
}
```

