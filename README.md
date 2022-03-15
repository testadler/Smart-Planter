# SmartPlant
 
Lib/Settings.py = Config für die Einstellungen
Lib/Version.py = Versionsnummer
Lib/Pins.py = Pin Out für das Relay + Sensoren
Lib/Websocket = Port Einstellungen für Flask

Dashboard ist über die IP des Pi erreichbar unter http:/IP-RAspi:7411 erreichbar

Reboot funktioniert aktuell nur wenn man Node installiert hat und das PM2 Paket !
mittels 

Datareader.py - Ließt die Sensordaten aus und speicher sie in der Datenbank ( SQLLite ) unter /db ab
Server.py - Stellt das Dashboard und steuert das Display sowie die Pins fürs Relay

Mit PM2 lass ich die beiden Processe Parallel laufen und kann über das Dashboard entsprechend die Dienste neustarten lassen
(per Dashboard wird dann der PM2 Process restartet welches meine beiden Scripts startet. 

Der PM2 Daemon startet beim booten automatisch die beiden Scripts neu und killt eventuelle alten Instanzen.

