# Aufgabe 4 und 5: Benchmark und Skalierbarkeit
Bei diesen Aufgaben sind wir ein wenig von der Aufgabenstellung abgewichen, um nicht nur die 3 Operatoren, sondern 
auch die Einlese-Geschwindigkeit zu testen. Dafür generiert das python-skript make_sample.py die Testdaten, welche 
ungefähr die gleichen Eigenschaften haben(gleich viele Spalten, ähnlicher Datenbereich). Die Ausgabe dieses Skripts 
wird in eine Datei umgeleitet, welche dann als Eingabe für profile.py, das eigentliche Benchmark-Skript fungiert.

Dieses führt bei jeder Eingabe die gleichen Operationen mit den gleichen zufällig generierten 10 (über einen Seed) 
Optionen einen Testdurchgang durch und mittelt die Ausführungszeit. So fällt einem auf, dass die Ausführungszeit eher
von der Größe der Eingabe und nicht von der Größe der Ausgabe abhängt. Deshalb wird zum besseren Vergleich mit den 
anderen Testgrößen auch eine Herunterrechnung auf die Berechnungszeit von 1000 Werten vorgenommen.
 
