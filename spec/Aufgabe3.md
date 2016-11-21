#Aufgabe 3: 3 Operatoren
Während die ersten beiden Operatoren einfach mit der pandas-Library auszuführen sind(select: datasource.py:42-43 und 
project: datasource.py:57 ), ist der Aggregate-Operator ein wenig umfangreicher. In unserem Fall iterieren wir für 
alle ausgewählten Spalten(datasource.py:72,78) jeweils über die einzelnen Werte(datasource.py:85) und merken uns den 
aggregierten Wert von jeweils RANGE Werten (datasource.py:99-107 (RANGE = limit))und fügen ihn zu unserer neuen Spalte 
hinzu. Am Schluss werden alle Spalten wieder zu einem DataFrame zusammengefügt.