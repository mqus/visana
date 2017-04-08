#Aufgabe 6: Wet Deposits
Ähnlich wie in Aufgabe 5 erläutert kommt man auch auf das finden der Wet-Deposits-Muster.
Bilder dazu liegen in screenshots/Aufgabe6.

0. Wir öffnen die Datei dust-32-grain-size-classes-2014.dat
1. Wir Begrenzen zunächst unsere Daten auf solche mit akzeptablen Luftfeuchtigkeitswerten
	- tidy up data-> or->and-> Daten eintragen
	- auf Apply klicken.
2. Jetzt bilden wir einige Staubkorngrößeklassen, diese sollten von Class1 bis ClassX aufsteigende Korngrößen haben. 
Die Anzahl und genaue Verteilung ist nicht so wichtig. Prinzipiell gehen auch nur die small/large-Klassen der 
einfacheren Datensätze.
3. Wir wählen unsere Clustering-Parameter:
	- n=20 (nicht so wichtig, sollte aber nicht zu groß werden. kleinere Werte hier sorgen dafür, dass die Berechnung
	 länger dauert.)
	- relative count [x]
	- k=6 (auch nicht so wichtig, sollte größer als 3 sein.)
	- features: die zuvor gebildeten Klassen
	- klick auf recalculate
4. Danach bekommen wir einen gefärbten Scatterplot zu sehen, bei welchem die Cluster hauptsächlich diagonale Streifen
 ausmachen.
5. Im Histogramm sehen wir, dass das blaue Cluster viele kleine Teilchen(Class1) und relativ wenige große Teilchen 
enthält(Class2,3,4). Das braune und das fliederfarbene Cluster (4 und 5) haben dagegen weniger kleine Teilchen und mehr 
große Teilchen, was bei einer relativ konstant hohen Anzahl von großen Partikeln auf eine insgesamt kleine Anzahl von
 Partikeln hinweist. Das merken wir uns erstmal.
6. Wir gehen zurück in den Scatterplot und ändern die Achsen auf MasterTime und RelHumidity. zur besseren 
Sichtbarkeit stellen wir den Hintergrund des Plots auf Schwarz.
7. Wir passen die Sichtbarkeit weiter mit alpha und dotsize an, so dass alle Cluster möglichst gut sichtbar sind.
8. jetzt schauen wir uns nur das fliederfarbene Cluster 5 an, welches relativ viele große und wenige kleine Partikel 
hatte und sehen, dass dieses vor allem auftritt, wenn Die Luftfeuchtigkeit hoch ist.
Wie bei 7. gesehen ist aber sonst die Luftfeuchtigkeit über das ganze Spektrum verteilt, so dass wir hier schon ein 
Muster erkannt haben.
9. Wenn wir jetzt mal einen Zeitbereich betrachten, wo das Cluster auftritt, können wir
10. Den ungefähren Verlauf der Luftfeuchtigkeit sehen, wenn wir die anderen Cluster wieder sichtbar machen.
Hier kann man auch ablesen, wie lange es dauert, bis so ein wet deposit "abgebaut" ist.


Alternativ kann man auch nach der Luftfeuchtigkeit Clustern und sich dann den Verlauf der Partikelanzahl über die Zeit 
anschauen.