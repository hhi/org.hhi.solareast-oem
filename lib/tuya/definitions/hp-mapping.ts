/**
 * Hp mapping for Tuya devices
 *
 * This file maps Tuya DPS (Data Point Specification) numbers to Homey capabilities.
 *
 * IMPORTANT NAMING CONVENTION NOTE:
 * Tuya determines the DPS codes (like 'countdown_set', 'capacity_set') and these cannot be changed.
 * However, their functional purpose may not be immediately clear from the name:
 * - DPS 11 'capacity_set' -> Controls hot water curve settings (not system capacity)
 * - DPS 13 'countdown_set' -> Controls heating curve settings (not countdown timer)
 *
 * The capability names maintain the Tuya naming for compatibility, but titles and descriptions
 * clarify the actual functional purpose.
 */

export interface DpsEntry {
  code: string;
  name: string;
  hp: string;
}

export class HpMapping {
  static capabilities: Record<string, number[]> = {
    onoff: [1],
    target_temperature: [4],
    measure_power: [104],
    measure_water: [39],
  };

  static customCapabilities: Record<string, number[]> = {
    'measure_power.internal': [104],
    'meter_power.power_consumption': [18],
    'meter_power.electric_total': [105],
    'measure_current.cur_current': [102],
    'measure_current.b_cur': [109],
    'measure_current.c_cur': [110],
    'measure_voltage.voltage_current': [103],
    'measure_voltage.bv': [111],
    'measure_voltage.cv': [112],
    'measure_frequency.compressor_strength': [20],
    'measure_frequency.fan_motor_frequency': [40],
    'measure_temperature.temp_top': [21],
    'measure_temperature.temp_bottom': [22],
    'measure_temperature.coiler_temp': [23],
    'measure_temperature.venting_temp': [24],
    'measure_temperature.around_temp': [26],
    'measure_temperature.temp_current_f': [35],
    'measure_temperature.top_temp_f': [36],
    'measure_temperature.bottom_temp_f': [37],
    'measure_temperature.around_temp_f': [38],
    'measure_temperature.coiler_temp_f': [41],
    'measure_temperature.eviout': [108],
    'measure_temperature.evlin': [107],
  };

  /**
   * Hp-specific capabilities mapped to DPS numbers
   *
   * NOTE ON CONFUSING NAMES (Tuya-determined, cannot be changed):
   * - hp_enum_capacity_set [11]: Despite name, controls HOT WATER curve settings (OFF, H1-H4)
   * - hp_enum_countdown_set [13]: Despite name, controls HEATING curve settings (H1-H8, L1-L8)
   *
   * DUAL CAPABILITY ARCHITECTURE (v0.99.54+):
   * Some DPS have both picker (user control) and sensor (status display) capabilities:
   * - DPS 11: hp_enum_capacity_set (picker) + hp_sensor_capacity_set (sensor)
   * - DPS 13: hp_enum_countdown_set (sensor) + hp_picker_countdown_set (picker)
   */
  static hpCapabilities: Record<string, number[]> = {
    hp_measure_pulse_steps_temp_current: [16],
    hp_measure_pulse_steps_effluent_temp: [25],
    hp_enum_mode: [2],
    hp_enum_work_mode: [5],
    hp_enum_water_mode: [10],
    // DPS 11: Hot water curve - DUAL CAPABILITIES (picker + sensor)
    // Values: OFF, H1-H4 for domestic hot water temperature curves
    hp_enum_capacity_set: [11], // Picker: user can set hot water curve
    hp_sensor_capacity_set: [11], // Sensor: displays actual hot water curve from device
    // DPS 13: Heating curve - DUAL CAPABILITIES (sensor + picker)
    // Values: OFF, H1-H8 (high), L1-L8 (low) for weather compensation curves
    hp_enum_countdown_set: [13], // Sensor: displays actual heating curve from device
    hp_picker_countdown_set: [13], // Picker: user can set heating curve
    hp_enum_volume_set: [106],
    // DPS 106: 0: No Power Module, 1: Single-Phase Power Module, 2: Three-Phase Power Module
    hp_hotwater: [101],
    hp_state_compressor_state: [27],
    hp_state_backwater: [31],
    hp_state_defrost_state: [33],
    hp_firmware_mcu: [14],
    // DPS 14: MCU mainboard firmware version (e.g., 433 = v4.3.3)
    hp_fault: [15],
  };

  static allCapabilities: Record<string, number[]> = {
    ...HpMapping.capabilities,
    ...HpMapping.customCapabilities,
    ...HpMapping.hpCapabilities,
  };

  static allArraysSwapped: Record<number, string> = Object.fromEntries(
    Object.entries(HpMapping.allCapabilities).map(([key, value]) => [value[0], key]),
  );

  /**
   * Multi-capability DPS mapping (v0.99.54+)
   *
   * Maps each DPS ID to an array of ALL capabilities that should be updated when that DPS changes.
   * This enables dual picker/sensor architecture where one DPS updates multiple capabilities.
   *
   * IMPORTANT: This is the PRIMARY mapping for DPS-to-capability updates.
   * Use this instead of allArraysSwapped for multi-capability support.
   *
   * Example use cases:
   * - DPS 11: Updates both hot water picker and sensor capabilities
   * - DPS 13: Updates both heating curve sensor and picker capabilities
   * - All other DPS: Single capability mapping (backward compatible)
   */
  static dpsToCapabilities: Record<number, string[]> = (() => {
    const mapping: Record<number, string[]> = {};

    // Build mapping from allCapabilities - each DPS gets an array of capabilities
    Object.entries(HpMapping.allCapabilities).forEach(([capability, dpsArray]) => {
      const dpsId = dpsArray[0];

      // Initialize array if not exists
      if (!mapping[dpsId]) {
        mapping[dpsId] = [];
      }

      // Add capability to array (allows multiple capabilities per DPS)
      mapping[dpsId].push(capability);
    });

    return mapping;
  })();

  /**
   * DPS Scale Factors (v1.0.10+)
   *
   * Tuya compresses decimal values as integers for transmission efficiency.
   * Scale factor indicates the divisor needed to convert raw DPS value to actual value.
   *
   * Scale calculation: actualValue = rawDpsValue / (10 ^ scale)
   *
   * Examples:
   * - Scale 1: 25000 / 10 = 2500 W
   * - Scale 2: 12345 / 100 = 123.45 kWh
   * - Scale 3: 2305 / 1000 = 230.5 V
   *
   * DPS without scale entry are passed through unchanged (no transformation).
   */
  static dpsScales: Record<number, number> = {
    // Power measurements (Scale 1: divide by 10)
    104: 1, // measure_power (Watt)

    // Energy measurements (Scale 2: divide by 100)
    18: 2, // meter_power.power_consumption (kWh)
    105: 2, // meter_power.electric_total (kWh)

    // Current measurements (Scale 3: divide by 1000)
    102: 3, // measure_current.cur_current (Ampère A)
    109: 3, // measure_current.b_cur (Ampère B)
    110: 3, // measure_current.c_cur (Ampère C)

    // Voltage measurements (Scale 3: divide by 1000)
    103: 3, // measure_voltage.voltage_current (Volt A)
    111: 3, // measure_voltage.bv (Volt B)
    112: 3, // measure_voltage.cv (Volt C)
  };

  /**
   * Transform raw DPS value using scale factor (v1.0.10+)
   *
   * Converts Tuya's compressed integer values to actual decimal values.
   * Non-numeric values are passed through unchanged.
   *
   * @param dpsId - DPS identifier
   * @param rawValue - Raw value from Tuya device
   * @returns Transformed value (scaled if numeric and scale defined)
   *
   * @example
   * // Power: Scale 1 (÷ 10)
   * transformDpsValue(104, 25000) // Returns: 2500 (2500 W)
   *
   * @example
   * // Voltage: Scale 3 (÷ 1000)
   * transformDpsValue(103, 2305) // Returns: 230.5 (230.5 V)
   *
   * @example
   * // No scale defined - pass through
   * transformDpsValue(1, true) // Returns: true (onoff capability)
   */
  static transformDpsValue(dpsId: number, rawValue: unknown): unknown {
    // Pass through non-numeric values unchanged (booleans, strings, enums)
    if (typeof rawValue !== 'number') {
      return rawValue;
    }

    // Get scale factor for this DPS
    const scale = this.dpsScales[dpsId];

    // No scale defined - pass through unchanged
    if (scale === undefined) {
      return rawValue;
    }

    // Calculate divisor: 10^scale (scale 1 = 10, scale 2 = 100, scale 3 = 1000)
    const divisor = 10 ** scale;

    // Transform: rawValue / divisor
    const transformedValue = rawValue / divisor;

    return transformedValue;
  }

  static dps: Record<string, DpsEntry> = {
    dps_1: { code: 'switch', name: 'Switch', hp: 'Schakelaar' },
    dps_2: { code: 'mode', name: 'Mode', hp: '(Verwarmings)modus' },
    dps_4: { code: 'temp_set', name: 'Target temp', hp: 'Doeltemperatuur' },
    dps_5: { code: 'work_mode', name: 'Working mode', hp: 'Bedrijfsmodus' },
    dps_10: { code: 'water_mode', name: 'Control Temperature', hp: 'Temperatuurregeling Water' },
    dps_11: { code: 'capacity_set', name: 'Hot water curve setting', hp: 'Instelling warmwater curve' }, // Functional: Hot water curves (OFF, H1-H4)
    dps_13: { code: 'countdown_set', name: 'Heating curve setting', hp: 'Instelling verwarmingscurve' }, // Functional: Heating curves (H1-H8, L1-L8)
    dps_14: { code: 'countdown_left', name: 'MCU Firmware Version', hp: 'MCU Firmware versie' },
    dps_15: { code: 'fault', name: 'Fault', hp: 'Fout toestand' },
    dps_16: { code: 'temp_current', name: 'EEV Open', hp: 'EEV Open' },
    dps_18: { code: 'power_consumption', name: 'Electricity Consumption of Today', hp: 'Stroom dagverbruik' },
    dps_20: { code: 'compressor_strength', name: 'Compressor Frequency', hp: 'Compressor frequentie' },
    dps_21: { code: 'temp_top', name: 'Inlet temp', hp: 'Water intrede temperatuur' },
    dps_22: { code: 'temp_bottom', name: 'Outlet temp', hp: 'Water uittrede temperatuur' },
    dps_23: { code: 'coiler_temp', name: 'Coiler temp', hp: 'Verdampingscondensator temperatuur' },
    dps_24: { code: 'venting_temp', name: 'Discharge temp', hp: 'Persgas temperatuur' },
    dps_25: { code: 'effluent_temp', name: 'EVI Open', hp: 'EVI-openingsstap' },
    dps_26: { code: 'around_temp', name: 'Ambient temp', hp: 'Buitentemperatuur' },
    dps_27: { code: 'compressor_state', name: 'Compressor state', hp: 'Compressor status' },
    dps_31: { code: 'backwater', name: 'Backwater state', hp: 'Retourwater status' },
    dps_33: { code: 'defrost_state', name: 'Defrosting', hp: 'Ontdooi status' },
    dps_35: { code: 'temp_current_f', name: 'High pressure temp', hp: 'Hogedruk verzadigingstemperatuur' },
    dps_36: { code: 'top_temp_f', name: 'Low presure temp', hp: 'Lagedruk verzadigingstemperatuur' },
    dps_37: { code: 'bottom_temp_f', name: 'Incoiler temp', hp: 'Condensor temperatuur' },
    dps_38: { code: 'around_temp_f', name: 'Tank temp', hp: 'Tapwater temperatuur' },
    dps_39: { code: 'venting_temp_f', name: 'Water flow', hp: 'Water flow' },
    dps_40: { code: 'effluent_temp_f', name: 'Fan motor frequency', hp: 'Ventilator frequentie' },
    dps_41: { code: 'coiler_temp_f', name: 'Suction Temp', hp: 'Zuiggas temperatuur' },
    dps_101: { code: 'minitemp_set', name: 'Hot Water Set Temp', hp: 'Warmwater stel temperatuur' },
    dps_102: { code: 'cur_current', name: 'Current A', hp: 'Hudige stroomsterkte' },
    dps_103: { code: 'voltage_current', name: 'Voltage A', hp: 'Huidige spanning' },
    dps_104: { code: 'cur_power', name: 'Power', hp: 'Huidig vermogen' },
    dps_105: { code: 'electric_total', name: 'Total Electricity Consumption', hp: 'Totaal stroomverbruik' },
    dps_106: { code: 'volume_set', name: 'Electricity Consumption Checking', hp: 'Stroomverbruik controle' },
    dps_107: { code: 'evlin', name: 'Economizer inlet Temp', hp: 'EVI wamtewisselaar zuiggas temperatuur' },
    dps_108: { code: 'eviout', name: 'Economy outlet temp', hp: 'EVI wamtewisselaar persgas temperatuur' },
    dps_109: { code: 'b_cur', name: 'Current B', hp: 'Amperage B' },
    dps_110: { code: 'c_cur', name: 'Current C', hp: 'Amperage C' },
    dps_111: { code: 'bv', name: 'Voltage B', hp: 'Voltage B' },
    dps_112: { code: 'cv', name: 'Voltage C', hp: 'Voltage C' },
  };
}
