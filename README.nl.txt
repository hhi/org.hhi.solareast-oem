Bedien en monitor uw warmtepomp lokaal met Homey Pro, welk merk er ook op de kast staat. Veel warmtepompen worden door SolarEast gebouwd en onder een andere merknaam verkocht (OEM). Deze app ondersteunt die toestellen.
Controleer het typeplaatje of de installatiehandleiding: een modelcode die met BLN begint, betekent dat uw warmtepomp door SolarEast is gebouwd. Sommige merken gebruiken een eigen modelcode; vraag bij twijfel uw leverancier of de unit door SolarEast is gebouwd. Andere warmtepompen die onder dezelfde merknaam worden verkocht, kunnen andere elektronica hebben en worden niet ondersteund. Deze app is niet verbonden aan SolarEast of aan de merken waaronder deze warmtepompen worden verkocht.
Deze app bevat twee drivers: één voor een wifi-verbinding (Tuya) en één voor een Modbus-aansluiting.
De dagelijkse communicatie verloopt via uw lokale netwerk.

KIES UW DRIVER

Warmtepomp via wifi (Tuya)
Voor een warmtepomp met een Tuya-wifiverbinding. Vereist de Device ID, Local Key, het lokale IP-adres en de Tuya-protocolversie van de warmtepomp.
Lokaal dashboard: http://HOMEY-IP:8092

Warmtepomp via Modbus (RS485)
Voor een warmtepomp met een RS485/Modbus-aansluiting. Vereist een Modbus TCP-gateway. Bij het koppelen voert u het IP-adres van de gateway, de TCP-poort en de Modbus Unit ID in. Getest op R32-modellen (BLN-…TB); R290-modellen (BLN-…TC) worden ondersteund.
Lokaal dashboard: http://HOMEY-IP:8090

Vervang HOMEY-IP door het lokale IP-adres van uw Homey Pro. De genoemde poorten zijn de standaardwaarden. Gebruik uw eigen poort als u deze heeft gewijzigd.

MONITORING EN BEDIENING

Bekijk temperaturen, bedrijfsstatus, storingen en beschikbare metingen van vermogen, energieverbruik en waterflow. Bedien aan/uit, bedrijfsmodus, setpunten en ondersteunde stooklijnkeuzes.

Gebruik Homey Flows voor bediening, meldingen en externe meetgegevens. Volg COP en seizoensrendement of gebruik de optionele adaptieve regeling, gebouwmodel-leren en energieprijs- en COP-optimalisatie.

Beschikbare metingen, instellingen en Flow-kaarten verschillen per model en driver. COP-berekeningen zijn afhankelijk van bruikbare vermogens-, temperatuur- en waterflowgegevens.

LOKALE DASHBOARDS

Beide drivers bieden dashboardpagina's voor monitoring, bediening en diagnose.

Dashboard en Live tonen beschikbare waarden en bedrijfsstatus. Interactief biedt bediening van ondersteunde instellingen. Expert geeft een doorzoekbaar overzicht van datapunten of registers. Wijzigingen toont waarden en geregistreerde veranderingen. Stooklijn geeft inzicht in de beschikbare curve-instellingen en regeling.

Tuya toont DPS-datapunten. De Modbus-driver toont de registers van de warmtepomp. De beschikbare dashboardfuncties verschillen per driver.

INSTALLATIE

Kies bij het toevoegen van een apparaat de driver die past bij de aansluiting van uw warmtepomp.

Voor Tuya zijn de lokale apparaatgegevens nodig. Voor Modbus moet de gateway vooraf correct zijn aangesloten en ingesteld. Raadpleeg de handleidingen van uw warmtepomp en gateway.

Een vast lokaal IP-adres of een DHCP-reservering voor de warmtepomp of gateway helpt verbindingsproblemen te voorkomen.

Geavanceerde schrijfbediening kan instellingen van de warmtepomp veranderen. Controleer de betekenis en noteer de oorspronkelijke waarde voordat u een instelling wijzigt.

ONDERSTEUNING

Meld problemen en vragen via de broncodepagina van de app. Vermeld daarbij de driver, het warmtepompmodel en de appversie.
