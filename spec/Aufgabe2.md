#Aufgabe 2: Visualisierungskonzept

Unser Visualisierungskonzept verwendet grundlegend den gleichen Scatterplot wie im vorherigen Meilenstein, färbt 
allerdings die punkte nach der Clusterzugehörigkeit ein.

Um die Zusammensetzung eines Clusters gut sichtbar zu machen, gibt es ebenfalls noch ein Histogramm.

Für eine grobe Übersicht der geclusterten Features sorgt ein Small Multiples-Scatterplot.

In einem Tortendiagramm wird außerdem dargestellt, welches Cluster wie oft auftritt.

Auch die Timeline wird je nach dem, zu welchem Cluster das angezeigte Zeitfenster gehört, eingefärbt.

## ScatterPlot
Der Scatterplot ist das Hauptelement, das verwendet werden kann um die geclusterten Daten zu explorieren. Es können 
einzelne Cluster 
an/ab-geschaltet werden um eine mögliche Überlagerung im Graphen auszuschließen, es kann der Hintergrund von weiß auf
 Schwarz umgestellt werden, sowie die Transparenz und Größe der einzelnen Punkte, um die Sichtbarkeit der Daten zu 
 verbessern. 

An der linken Seite kann man außerdem von den Optionen in die Details wechseln, wo beim Maushover oder per 
Rechteck-Selektion alle genauen Daten angezeigt werden.

Als Achsen des Graphs sind alle Spalten des Originalen Datensatzes verfügbar, zusätlich dazu die selbst gewählten 
Staubkorngrößenklassen und eine Spalte namens Daytime, welche nur die tageszeit in Minuten seit Mitternacht angibt.

Im Scatterplot selbst kann per Mausrad oder auch per rechtsklick-and-drag und Rechteck gezoomt werden, so kann der 
Blick auf das wesentliche gerichtet werden.
Wenn man sich "verzoomt" hat kann man auf den Apply&Reset View Button links klicken um wieder alle Daten im Blick zu 
haben.

Optional kann auch eine Regressionsgerade gezeichnet werden.

Auch eine Besonderheit ist, dass sich die x- und y-Grenzen des sichtbaren Graphen nicht verändern, wenn man lediglich
 ein anderes Clustering oder eine andere Aggregation verwendet. So kann man Unterschiede besser bemerken und muss 
 nicht ständig den Kontext des aktuellen Graphen wieder herstellen.


#Histogramm

Das Histogramm zeigt die Verteilung der Features(mit Clustern)/Staubkorngrößenklassen(ohne Clustern)
in linearer oder logarithmischer Scala an. 
Jeder Balken gibt die durchschnittliche Größe des Parameters an, 
außerdem sind die Standardabweichungen der Werte abgetragen, um die Varianz der Werte sichtbar zu machen.

