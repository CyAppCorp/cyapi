# INH Project Transféré sur CYAPI inh.py

## Request "Refresh Data"

   Effectué par le serveur qui actualise les BDD dès qu'un étudiant exporte son agenda et qu'un nouvel emploi du temps est rajouté à la BDD

   Requête entrante :

```json
   {
    "usage": "refresh_data",
    "data": {
        "P1G1": "4avRKnJDX7",
        "P1G2": "nKm32pZ49F",
        "P1G3": "DLqbGUnI8d",
        "P2G1": "47UWNJxCkO",
        "P2G2": "xMi3Wr4JIT",
        "ING1GIG1": "quHb25OHiT",
        "ING1GIG2": "vfrX1YLOr8",
        "ING1GM": "AOpmxthx2j",
        "ING2GSI1": "Q7Xfxy9Pwx",
        "ING2GSI2": "lqtiw77Fho",
        "ING2GMI": "6fWlJfNPTA",
        "ING3CS": "",
        "ING3HPDA": "",
        "ING3ICC": "",
        "ING3IA": ""
    }
   }
```

   Requête sortante :

```json
  {
    "salle_remplis": [
        {
            "A001": {
                "Début": "08:00",
                "Fin": "09:30",
                "Prof": "BARRAU NELLY",
                "Résumé": "CM - Algèbre"
            }
        },
        {
            "E218": {
                "Début": "08:00",
                "Fin": "09:30",
                "Prof": "DECOURCHELLE INES",
                "Résumé": "CM - Informatique"
            }
        }
    ],
    "salle_vide_prochain_cours": [
        {
            "A001": {
                "Début": "09:45",
                "Fin": "11:15",
                "Prof": "LOUBIERE PEIO",
                "Résumé": "CM - Informatique"
            }
        },
        {
            "E106": {
                "Début": "11:30",
                "Fin": "13:00",
                "Prof": "DUJOL ROMAIN",
                "Résumé": "TD - Informatique"
            }
        },
        {
            "E108": {
                "Début": "11:30",
                "Fin": "13:00",
                "Prof": "LOUBIERE PEIO",
                "Résumé": "TD - Informatique"
            }
        },
        {
            "E218": {
                "Début": "09:45",
                "Fin": "11:15",
                "Prof": "MODESTE THIBAULT",
                "Résumé": "CM - Statistiques"
            }
        }
    ],
    "salles_vide_journee": {
        "locations": [
            "E101",
            "E102",
            "E103",
            "E104",
            "E105",
            "E106",
            "E107",
            "E108",
            "E109",
            "E209",
            "E210",
            "E211",
            "E212",
            "E213",
            "E214",
            "E215",
            "E217",
            "E218"
         ]
      }
   }
```



## Requête "Fetch"
 
   Effectué dès qu'un utilisateur va sur la page Salles de l'application


```json
   {
    "usage": "fetch"
   }
```

   Requête sortante :

```json
  {
    "salle_remplis": [
        {
            "A001": {
                "Début": "08:00",
                "Fin": "09:30",
                "Prof": "BARRAU NELLY",
                "Résumé": "CM - Algèbre"
            }
        },
        {
            "E218": {
                "Début": "08:00",
                "Fin": "09:30",
                "Prof": "DECOURCHELLE INES",
                "Résumé": "CM - Informatique"
            }
        }
    ],
    "salle_vide_prochain_cours": [
        {
            "A001": {
                "Début": "09:45",
                "Fin": "11:15",
                "Prof": "LOUBIERE PEIO",
                "Résumé": "CM - Informatique"
            }
        },
        {
            "E106": {
                "Début": "11:30",
                "Fin": "13:00",
                "Prof": "DUJOL ROMAIN",
                "Résumé": "TD - Informatique"
            }
        },
        {
            "E108": {
                "Début": "11:30",
                "Fin": "13:00",
                "Prof": "LOUBIERE PEIO",
                "Résumé": "TD - Informatique"
            }
        },
        {
            "E218": {
                "Début": "09:45",
                "Fin": "11:15",
                "Prof": "MODESTE THIBAULT",
                "Résumé": "CM - Statistiques"
            }
        }
    ],
    "salles_vide_journee": {
        "locations": [
            "E101",
            "E102",
            "E103",
            "E104",
            "E105",
            "E106",
            "E107",
            "E108",
            "E109",
            "E209",
            "E210",
            "E211",
            "E212",
            "E213",
            "E214",
            "E215",
            "E217",
            "E218"
         ]
      }
   }
```

