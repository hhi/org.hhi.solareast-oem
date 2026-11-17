# SolarEast OEM Heat Pump

Local control and monitoring on Homey Pro for heat pumps that are built by
SolarEast and sold under other brand names (OEM), whatever brand is on the
casing. This app is not affiliated with SolarEast or with the brands under which
these heat pumps are sold.

The app provides two device drivers; choose the one that matches how your heat
pump is connected:

| Driver | Connection | When to choose it |
| --- | --- | --- |
| **Heat pump via Wi-Fi (Tuya)** | Tuya Local API over the local network | Your heat pump is connected to Wi-Fi and you have its Device ID and Local Key. |
| **Heat pump via Modbus (RS485)** | RS485 through a Modbus TCP gateway | Your heat pump has an RS485/Modbus connection and you have a gateway such as an Elfin EW11A (`9600 8N1`). |

Both drivers operate locally. The Modbus driver does not require Tuya cloud or
Tuya Local credentials.

## Is My Heat Pump Supported?

Check the type plate or the installer manual. A model code starting with `BLN`
means the heat pump is built by SolarEast. Some brands use their own model
codes; if in doubt, ask your supplier whether the unit is built by SolarEast.
Other heat pumps sold under the same brand name may use different electronics
and are not supported. Units sold under another brand name may use their own
Tuya firmware; see [Important Limitations](#important-limitations).

## Requirements

- Homey Pro with firmware `12.3.0` or newer
- A heat pump built by SolarEast (often a model code starting with `BLN`) on
  the same local network as Homey
- For the Tuya driver: Device ID, Local Key, IP address and the correct Tuya protocol version
- For the Modbus driver: a wired RS485/Modbus connection and a reachable Modbus TCP gateway

## What the App Provides

- Local readout of temperatures, operating state, defrost, antifreeze,
  sterilization and decoded fault information
- Power, energy, voltage, current, compressor frequency, fan speed, valve
  position, pump PWM and water-flow measurements when the connected heat pump
  supplies them
- Control of main on/off, operating mode, heating, cooling and DHW setpoints,
  plus supported heating and hot-water curve settings
- COP calculation based on available power, water-temperature delta and flow;
  external power, flow, ambient, indoor-temperature, price, solar and wind
  data can also be supplied through Homey Flows
- Flow cards for thresholds, alerts, faults, setpoints, external data and
  advanced curve calculations
- Optional adaptive temperature control, building-model learning, COP and
  energy-price optimisation, and weather-based advice
- English, Dutch, German and French user interface strings

Available measurements and controls vary by driver and heat-pump firmware.

## Adaptive Control

In Classic mode, the configured Kp, Ki and deadband are applied when the device
starts and when its settings change. The deadband setting applies while building
model learning is disabled; with the building model enabled, the app derives the
deadband from heat loss (0.3–0.8 °C).

Pre-heating estimates use the building model averaged over the past 24 hours once
at least 18 hours of history are available. Until then, they use the current
model. This applies to the insight, pre-heating recommendation and calculation
Flow card.

## Installation

1. Install the app from the Homey App Store.
2. In Homey, add a device and select the driver matching the connection method
   above.
3. Complete the driver-specific pairing steps below.

### Tuya Local API

1. Select **Heat pump via Wi-Fi (Tuya)**.
2. Enter the heat pump's Device ID, Local Key and local IP address.
3. Select the Tuya protocol version. Start with `3.3`; try `3.4` or `3.5` if
   the device cannot connect.

### Modbus TCP Gateway

1. Connect the heat pump's RS485/Modbus bus to an Elfin EW11A or equivalent
   Modbus TCP gateway.
2. Ensure that the gateway is reachable from Homey on the local network.
3. Select **Heat pump via Modbus (RS485)**.
4. Enter the gateway IP address, TCP port and Modbus Unit ID.
5. Adjust the polling intervals only when necessary.

The usual defaults are TCP port `502` and Modbus Unit ID `1`. Give the gateway
a fixed DHCP lease or static IP address to prevent avoidable reconnect issues.

## Local Dashboards

Both drivers offer local dashboards. From a browser on the same network, open
the address for your driver:

| Driver | Default dashboard address |
| --- | --- |
| Heat pump via Wi-Fi (Tuya) | `http://<homey-ip>:8092` |
| Heat pump via Modbus (RS485) | `http://<homey-ip>:8090` |

Replace `<homey-ip>` with the local IP address of your Homey Pro. If you change
the Dashboard port setting, use that port instead.

The following pages are available for both drivers:

- `/` — heat-pump overview with available measurements and operating status
- `/interactive` — controls for supported settings
- `/live` — device capabilities grouped by category
- `/expert` — searchable overview of Tuya DPS datapoints or Modbus registers,
  with supported write controls
- `/changelog` — an overview per datapoint or register, with current and previous
  values and change statistics
- `/processchema` — the refrigerant cycle, water circuit and available live measurements

Tuya Expert supports searches by DPS number, name, unit, value and capability.
It offers views by DPS number, function and unit, plus a writable-only filter.
The Tuya Changes page supports searching, sorting, a changed-only filter and
filtered JSON or Markdown exports. Statistics are kept while the app runs,
including when the page is closed, and reset when the app restarts.

Heating-curve pages differ by driver:

- Tuya: `http://<homey-ip>:8092/heating-curve` shows the reported Tuya curve
  selections and the app's linear heating curve when its parameters are
  available. It does not reconstruct the Tuya H/L preset curves.
- Modbus: `http://<homey-ip>:8090/heating-curve` provides the DIY heating-curve
  editor.

> **Caution:** Dashboard write controls and direct Modbus read/write Flow cards
> can change heat-pump behaviour. Check the meaning of a setting and record its
> original value before changing it.

## Important Limitations

- The Modbus driver is tested on R32 models (BLN-…TB). R290 models (BLN-…TC)
  use the same register map and are supported. The temperature scale is
  detected from the heating setpoint when the driver connects.
- Whether R290 models (BLN-…TC) and units sold under another brand name use
  the same Tuya datapoints has not been verified for every model.
- The floor-heating setpoint is available as a Modbus device capability, but
  does not yet have its own Flow action.
- COP can be unavailable or less accurate when usable power or flow data is
  missing.
- Tuya Local and Modbus are separate drivers. A Modbus gateway cannot be used
  with the Tuya driver, and the Modbus driver does not use Tuya credentials.
- The local dashboards have no password; anyone on the local network can open
  them, including the write functions.

## Support

Please report bugs and feature requests through the repository's GitHub
[issues](https://github.com/hhi/org.hhi.solareast-oem/issues). Include the driver,
heat-pump model, app version and steps needed to reproduce the problem.

## Development

```sh
npm install
npm run build
npm run lint
homey app validate
```

Use `homey app run` for local development on a paired Homey Pro.

## License

Developed for the Homey platform following the Homey app-development
guidelines.
