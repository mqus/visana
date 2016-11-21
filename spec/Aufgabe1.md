# Aufgabe 1, Semantik und Datenstrukturen
Wir haben uns beim Datentyp für eine Relation entscheiden(siehe Meilenstein1) 
und haben das in einer In-Memory-Lösung verarbeitet, da der Umfang der Daten absehbar klein ist und eine 
Realtime-Verarbeitung erforderlich ist, um schnell auf Eingaben des Nutzers zu reagieren.
Diese Lösung sieht im konkreten so aus, dass die Ursprungsdaten sowie alle (Zwischen-)Ergebnisse in Form je eines 
DataFrames der pandas-Bibliothek im Heap liegen, wo dann auf sie zugegriffen wird.

Die Wahl der DataFrames ist leicht zu rechtfertigen; pandas und seine DataFrames sind eine gängige Wahl bei der 
Verarbeitung und Analyse von Daten und das macht sie deshalb kampferprobt und ermöglicht eine einfachere Entwicklung 
aufgrund des umfangreichen Dokumentationsmaterials. Außerdem sind hier die Performancekritischen Teile in c 
geschrieben, so dass es zu keinen Leistungseinbußen kommt. 

Die mit table gewrappten DataFrames werden in einem dict() zur späteren Benutzung aufbewahrt (datasource.py:9).