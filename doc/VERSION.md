#Status:
- datasource angepasst:
  - groupby-Funktion hinzugefügt(zB.: aggregiere Daten nach Datum)
  - select

- zweiter GUI-Prototyp fertig
	- Scatterplot 2er beliebiger Parameter darstellen
		- mit dunklem Hintergrund
		- mit wählbarer Punktgröße und Transparenz
		- wahlweise mit Regressionsgerade
		- nur einzelne Cluster anzeigen (s.u.)
		- einen Tooltip von Punkten anzeigen, die ausgewählt wurden oder 
		über die die Maus drübergefahren ist.
		- zoombar(Mausrad/ rechtsklick-ziehen)
	- Daten können beliebig begrenzt werden
	- Daten können über eine beliebige Anzahl von Minuten zusammengefasst werden.
	- Staubgrößenklassen-Spalten können pro Zeile normalisiert werden.
	- eigene Staubgrößenklassen können definiert werden
	- Log aller durchgeführten Interaktionen kann anzeigt werden.
	- Zeitleiste
		- welche Daten verfügbar sind (nicht na)
		- zu welchen Clustern sie gehören (s.u.)
	- Cluster können berechnet werden
		- k-means
		- auswählbare Features
		- labelling  und Anzeige in einheitlichen Farben
	- ein kombiniertes Histogramm kann angezeigt werden
		- Durchschnittswert eines Features pro Cluster inkl stdev
		- in Clusterfarbe
	- ein Small-Multiples-Scatterplot kann angezeigt werden
		- pro feature-Combination ein Scatterplot
		- gefärbt nach Cluster
		- zur Vergleichbarkeit angeordnet
		- angezeigt Cluster können ausgewählt werden.
	- ein Tortendiagram kann angezeigt werden
		- zeigt die Anzehl der Datensätze pro Cluster.
		
	- neue Dateien können per File->open geöffnet werden.
	
	
  
  
  - den Messzeitraum der dargestellten Punkte begrenzen
  - Daten über n-Minuten-Zeitfenster zusammenfassen
  - Tooltips beim drüberfahren anzeigen
  - Rein- und rauszoomen
  - Punkte im Rechteck selektieren und dann auf der Zeitleiste darstellen und zusammengefasste Informationen 
  anzeigen.
  - In der Zeitleiste anzeigen, was gerade dargestellt wird
  - in einer editierbaren history den Verlauf anzeigen
  - sich selbst bereinigen
  - alles wieder auf Start stellen
  - Regressionsgerade darstellen
	
	

#TODO:

- Unit-Tests
- zeige Scatterplot-selektion in der Timeline



# Git-Zugang:

Ein detaillierter Fortschritt ist auf https://github.com/mqus/visana.git einsehbar.