# CYAPI - REST API FOR CYAPP

## Request "Refresh Data"

```json
   {
    "usage": "refresh_data",
    "data": {
        "P1G1": "--------------",
        "P1G2": "--------------",
        "P1G3": "--------------",
        "P2G1": "--------------",
        "P2G2": "--------------",
        "ING1GIG1": "--------------",
        "ING1GIG2": "--------------",
        "ING1GM": "--------------",
        "ING2GSI1": "--------------",
        "ING2GSI2": "--------------",
        "ING2GMI": "--------------",
        "ING3CS": "--------------",
        "ING3HPDA": "--------------",
        "ING3ICC": "--------------",
        "ING3IA": "--------------"
    }
   }
```

   Response :

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
 

```json
   {
    "usage": "fetch"
   }
```

   Response :

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

