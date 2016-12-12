#Aufgabe 8: Datenaggregation
Zur Reduktion des statistischen Rauschens der Daten lassen sich aufeinanderfolgende Punkte zusammenfassen. Es kann 
also in einem Textfeld auf der linken Seite die Anzahl von Minuten eingestellt werden, die aufeinanderfolgend 
jeweils zu einem einzigen Datenpunkt mit einem Durchschnittswert aggregiert werden. Fehlende Werte werden ebenfalls 
korrekt behandelt, d.h. fehlende Werte ergeben aggregiert ebenfalls einen fehlenden Wert, und für die 
Durchschnittsberechnung werden nur die Werte miteinbezogen, die auch tatsächlich gemessen wurden.
Die Option ist von einer Minute (also minutenweise Originaldaten ohne Aggregation) bis zu 1440 Minuten, also einem 
Tag, einstellbar. Bei wiederholtem Aggregieren werden die zuvor aggregierten Daten aktualisiert. Da der vorgang 
relativ viel Zeit beansprucht, muss man den darunterliegenden Button betätigen, um die Aggregation herbeizuführen.