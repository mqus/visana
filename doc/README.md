#VisualAnalytics
Willkommen bei unserem explorativen Analysetool für Staubdaten!

Wir haben unser Daten-Backend in python 3 geschrieben und dabei pandas verwendet.
## How to start:

	markus@tp-x250 visana $> prototype/start.sh

## Compiler/Version
Python 3.5.2

## Externe Bibliotheken und Version
gebraucht:
- python3-pandas
- python3-tkinter
- python3-matplotlib
- (evtl auch pip zum Installieren der Pakete)

Wir haben es leider nicht geschafft, unsere python-Bibliotheken beizulegen, weil diese wohl erst auf dem Zielgerät 
kompiliert werden müssen... deshalb ist es wohl am Benutzer, für die Installation dieser Abhängigkeiten zu sorgen.
Wir werden trotzdem beim nächsten Meilenstein versuchen, etwas mehr Komfort in die Sache zu bekommen.

## Eigene Leistung
- Aufbau eines GUI
- Eigenständiges verknüpfen aller Features etc
- uvm.

## KEINE eigene Leistung:
- Scatterplot-Darstellungsfunktion und 
	Koordinaten-Transformierung von matplotlib
- Übersetzung von python-Code in ein Grafisches Interface von tkinter
- die vorgefertigten Widgets und die matplotlibintegration von tkinter
- ultraschnelle Listenverarbeitung von numpy und pandas
  - unter anderem in handle_mouse_event und der datasource



# Informationen für den Anwender:
Wenn Dateien eingelesen werden sollen, die andere Spaltennamen enthalten, müssten bei datasource.py eventuell die 
Funktionen <code>get_time_columns</code> (gibt den Spaltennamen der Zeitspalte zurück) und 
<code>get_grain_columns</code> (gibt die Namen aller Spalten, die auf die Staubgröße hinweisen, zurück)
angepasst werden.




