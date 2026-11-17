Control and monitor your heat pump locally with Homey Pro, whatever brand is on the casing. Many heat pumps are built by SolarEast and sold under other brand names (OEM). This app supports those units.
Check the type plate or the installer manual: a model code starting with BLN means your heat pump is built by SolarEast. Some brands use their own model codes; if in doubt, ask your supplier whether the unit is built by SolarEast. Other heat pumps sold under the same brand name may use different electronics and are not supported. This app is not affiliated with SolarEast or with the brands under which these heat pumps are sold.
This app includes two drivers: one for a Wi-Fi (Tuya) connection and one for a Modbus connection.
Daily communication takes place over your local network.

CHOOSE YOUR DRIVER

Heat pump via Wi-Fi (Tuya)
For a heat pump with a Tuya Wi-Fi connection. Requires the heat pump's Device ID, Local Key, local IP address and Tuya protocol version.
Local dashboard: http://HOMEY-IP:8092

Heat pump via Modbus (RS485)
For a heat pump with an RS485/Modbus connection. Requires a Modbus TCP gateway. During pairing, enter the gateway's IP address, TCP port and Modbus Unit ID. Tested on R32 models (BLN-…TB); R290 models (BLN-…TC) are supported.
Local dashboard: http://HOMEY-IP:8090

Replace HOMEY-IP with your Homey Pro's local IP address. The ports shown are the defaults. Use your configured port if you have changed it.

MONITORING AND CONTROL

View temperatures, operating status, faults and available power, energy consumption and water-flow measurements. Control on/off, operating mode, setpoints and supported heating-curve selections.

Use Homey Flows for control, notifications and external measurements. Monitor COP and seasonal efficiency or use optional adaptive control, building-model learning, energy-price optimisation and COP optimisation.

Available measurements, settings and Flow cards vary by model and driver. COP calculations depend on usable power, temperature and water-flow data.

LOCAL DASHBOARDS

Both drivers provide dashboard pages for monitoring, control and diagnostics.

Dashboard and Live show available values and operating status. Controls lets you adjust supported settings. Expert provides a searchable overview of datapoints or registers. Changes shows values and recorded changes. Heating curve provides insight into the available curve settings and control.

Tuya displays DPS datapoints. The Modbus driver displays the heat pump's registers. Available dashboard features vary by driver.

INSTALLATION

When adding a device, select the driver that matches how your heat pump is connected.

Tuya requires the local device details. For Modbus, the gateway must first be connected and configured correctly. Consult the manuals of your heat pump and gateway.

A fixed local IP address or DHCP reservation for the heat pump or gateway helps prevent connection problems.

Advanced write controls can change heat-pump settings. Check what a setting does and record its original value before changing it.

SUPPORT

Report problems and questions on the app's source-code page. Include the driver, the heat-pump model and the app version.
