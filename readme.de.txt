Steuern und überwachen Sie Ihre Wärmepumpe lokal mit Homey Pro, unabhängig von der Marke auf dem Gehäuse. Viele Wärmepumpen werden von SolarEast gebaut und unter anderen Markennamen verkauft (OEM). Diese App unterstützt diese Geräte.
Prüfen Sie das Typenschild oder die Installationsanleitung: Ein Modellcode, der mit BLN beginnt, bedeutet, dass Ihre Wärmepumpe von SolarEast gebaut wurde. Einige Marken verwenden eigene Modellcodes; fragen Sie im Zweifel Ihren Lieferanten, ob das Gerät von SolarEast gebaut wurde. Andere Wärmepumpen, die unter demselben Markennamen verkauft werden, können eine andere Elektronik haben und werden nicht unterstützt. Diese App steht in keiner Verbindung zu SolarEast oder zu den Marken, unter denen diese Wärmepumpen verkauft werden.
Diese App enthält zwei Treiber: einen für eine WLAN-Verbindung (Tuya) und einen für einen Modbus-Anschluss.
Die tägliche Kommunikation erfolgt über Ihr lokales Netzwerk.

WÄHLEN SIE IHREN TREIBER

Wärmepumpe über WLAN (Tuya)
Für eine Wärmepumpe mit Tuya-WLAN-Verbindung. Benötigt werden die Geräte-ID, der lokale Schlüssel, die lokale IP-Adresse und die Tuya-Protokollversion der Wärmepumpe.
Lokales Dashboard: http://HOMEY-IP:8092

Wärmepumpe über Modbus (RS485)
Für eine Wärmepumpe mit RS485/Modbus-Anschluss. Ein Modbus-TCP-Gateway ist erforderlich. Geben Sie beim Koppeln die IP-Adresse des Gateways, den TCP-Port und die Modbus-Unit-ID ein. Getestet mit R32-Modellen (BLN-…TB); R290-Modelle (BLN-…TC) werden unterstützt.
Lokales Dashboard: http://HOMEY-IP:8090

Ersetzen Sie HOMEY-IP durch die lokale IP-Adresse Ihres Homey Pro. Die angegebenen Ports sind die Standardwerte. Falls Sie den Port geändert haben, verwenden Sie Ihren eingestellten Port.

ÜBERWACHUNG UND STEUERUNG

Sehen Sie Temperaturen, Betriebsstatus, Störungen und verfügbare Messwerte für Leistung, Energieverbrauch und Wasserdurchfluss ein. Steuern Sie Ein/Aus, Betriebsmodus, Sollwerte und unterstützte Heizkurvenoptionen.

Nutzen Sie Homey Flows für Steuerung, Benachrichtigungen und externe Messdaten. Verfolgen Sie COP und saisonale Effizienz oder nutzen Sie die optionale adaptive Regelung, das Lernen des Gebäudemodells sowie Energiepreis- und COP-Optimierung.

Verfügbare Messwerte, Einstellungen und Flow-Karten unterscheiden sich je nach Modell und Treiber. COP-Berechnungen setzen verwertbare Leistungs-, Temperatur- und Wasserdurchflussdaten voraus.

LOKALE DASHBOARDS

Beide Treiber bieten Dashboard-Seiten zur Überwachung, Steuerung und Diagnose.

Dashboard und Live zeigen verfügbare Werte und den Betriebsstatus. Die interaktive Seite ermöglicht die Bedienung unterstützter Einstellungen. Expert bietet eine durchsuchbare Übersicht der Datenpunkte oder Register. Die Änderungsübersicht zeigt Werte und aufgezeichnete Änderungen. Die Heizkurvenseite gibt Einblick in die verfügbaren Kurveneinstellungen und die Regelung.

Tuya zeigt DPS-Datenpunkte. Der Modbus-Treiber zeigt die Register der Wärmepumpe. Die verfügbaren Dashboard-Funktionen unterscheiden sich je nach Treiber.

INSTALLATION

Wählen Sie beim Hinzufügen eines Geräts den Treiber, der zum Anschluss Ihrer Wärmepumpe passt.

Für Tuya werden die lokalen Gerätedaten benötigt. Bei Modbus muss das Gateway zuvor korrekt angeschlossen und konfiguriert sein. Beachten Sie die Anleitungen Ihrer Wärmepumpe und Ihres Gateways.

Eine feste lokale IP-Adresse oder DHCP-Reservierung für die Wärmepumpe oder das Gateway hilft, Verbindungsprobleme zu vermeiden.

Erweiterte Schreibfunktionen können Einstellungen der Wärmepumpe verändern. Prüfen Sie die Bedeutung einer Einstellung und notieren Sie den ursprünglichen Wert, bevor Sie sie ändern.

UNTERSTÜTZUNG

Melden Sie Probleme und Fragen auf der Quellcode-Seite der App. Geben Sie dabei den Treiber, das Wärmepumpenmodell und die App-Version an.
