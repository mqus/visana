#Aufgabe 5: Exploration des Verhältnisses kleiner und großer Partikel

Hierzu bildet man sich einfach 2 Klassen: 
- Class1: kleine partikel
- Class2: große partikel

mit selbst geẅhlten Grenzen(siehe step1.png).
Diese können dann evtl noch geclustert werden oder einfach so betrachtet werden.
Nach Auswahl des Zeitfensters und aktivieren der berechnung der relativen Größe muss dann auf recalculate geclickt 
werden(step2.png).


Ohne Clustering ist dann bei dem Scatterplot(x:Class1,y:Class2, siehe auch step3.png) eine Punktverteilung entlang 
einer absteigenden Gerade zu sehen, wobei rechts unten wesentlich mehr Punkte gezeichnet werden als rechts oben. 
Daraus (auch zu urteilen daraus, dass die y-Achse nur mis 0.12 geht) lässt sich schließen, dass hauptsächlich wenige 
große Partikel und viele kleine Partikel gibt. (step4.png)

Mit Clustering (zB. k=5 und features=(Class1,Class2), siehe step5.png) ist dann im gleichen Graphen sichtbar (alpha auf 
0.4 und dotsize auf 7, siehe step6.png), dass es ein Cluster mit 
einer großen Bereichsabdeckung gibt, welches am oberen linken Ende der "Gerade" ist und dann die Cluster-Abschnitte 
immer kleiner werden. Sieht man sich alerdings den Pie-Chart oder die Timeline an, sieht man, dass der vermeintlich 
große Bereich den kleinsten Teil der Daten ausmacht und das vermeintlich kleine blaue Cluster unten links das größte
(bei der Anzahl der Punkte) ist (vgl. step7.png und step8.png).

Im Histogramm kann man dann einmal vergleichend auf die eigentlichen Verteilungen der Partikel schauen(step9.png)
 
Dieser Ansatz ist bei weitem nicht erschöpfend, mann kann sich aur zB die Zeitliche Verteilung der Cluster und der 
Ausprägung der einzelnen Klassen ansehen, in dem man einfach andere parameter im Scatterplot anwählt, aber für diese 
Erklärung soll das erstmal reichen.
	