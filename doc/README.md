#VisualAnalytics
Willkommen bei unserem explorativen Analysetool für Staubdaten!

Wir haben unser Daten-Backend in python 3 geschrieben und dabei pandas verwendet.

Das Frontend verwendet Matplotlib und tkinter.
## How to start:

	markus@my-pc visana $> prototype/start.sh

## Compiler/Version
Python 3.6 (sollte auch in 3.5.2 funktionieren)

## Externe Bibliotheken und Version
gebraucht:
- python3-pandas
- python3-tkinter
- python3-matplotlib
- python3-sklearn
- python3-numpy
- (evtl auch pip zum Installieren der Pakete)

Wir haben es leider nicht geschafft, unsere python-Bibliotheken beizulegen, weil diese wohl erst auf dem Zielgerät 
kompiliert werden müssen... deshalb ist es wohl am Benutzer, für die Installation dieser Abhängigkeiten zu sorgen.

## Eigene Leistung
- Aufbau eines GUI
- Eigenständiges verknüpfen aller Features etc
- Ausdenken des Layouts
- Ausdenken eines Konzepts


## KEINE eigene Leistung:
- Scatterplot-Darstellungsfunktion und 
	Koordinaten-Transformierung von matplotlib
- Übersetzung von python-Code in ein Grafisches Interface von tkinter
- die vorgefertigten Widgets und die matplotlib-integration von tkinter
- ultraschnelle Listenverarbeitung von numpy und pandas
  - unter anderem in handle_mouse_event und der datasource
- clustern der Daten und k-means-Berechnung (von scikit)
- Einstellen des Hintergrunds der Graphen  sowie die Zoom-Funktion per Mausrad 
	ist teilweise von github (siehe src/v2/util.py, Quellen sind dort zu finden.)





# Informationen für den Anwender:
Wenn Dateien eingelesen werden sollen, die andere Spaltennamen enthalten, müssten bei datasource.py eventuell die 
Funktionen <code>get_time_columns</code> (gibt den Spaltennamen der Zeitspalte zurück) und 
<code>get_grain_columns</code> (gibt die Namen aller Spalten, die auf die Staubgröße hinweisen, zurück)
angepasst werden.




