# OEM upstream synchronization

Source: `hhi/org.hhi.adlar-heatpump`, main commit
`9b0556e1e25022ca439faad9139323b18fc5cbf4` (code version 3.12.3).
`UPSTREAM` records this commit for subsequent synchronizations.

## Included changes

- 3.12.1: use the 24-hour building-model mean for pre-heating insights, calculation
  Flow cards and recommendations; persist and reset its history with the model.
- 3.12.2: apply Classic PI settings at construction and settings changes. The
  configured deadband applies when building-model learning is disabled.
- Lint cleanup, a dedicated test tsconfig, and the upstream lint CI job. Validation
  runs on pushes to main and on pull requests.
- Port the corresponding regression tests for both OEM drivers.

## OEM adaptations

The app keeps its ID `org.hhi.solareast-oem`, the `bln-tuya` and `bln-modbus`
drivers, `hp_*` identifiers, OEM documentation and artwork. No Aurora III driver,
registers, capabilities, Flow cards or process-schema adapter are imported.
The 3.12.3 schema changes are Aurora III-specific and do not apply here.

Version 1.0.0 is retained on this development branch; this synchronization does
not create a new release or move the existing v1.0.0 tag.

## Validation

Run `npm test`, `npm run lint`, `npm run check:caps`, and `homey app validate`.
The imported tests cover day-mean warm-up, persistence and reset, plus custom PI
settings at restart and the deadband with building-model learning on and off.
