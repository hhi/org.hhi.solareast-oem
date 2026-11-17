/**
 * Tests for refrigerant support (P119): R32 (BLN-TB) and R290 (BLN-TC) are supported,
 * R410A is not. The temperature scale: R32 decides x1, the heating setpoint (0x0301) checks it.
 */

'use strict';

const { test } = require('node:test');
const assert = require('node:assert');
const Module = require('node:module');

const originalLoad = Module._load;
Module._load = function load(request, parent, isMain) {
  if (request === 'homey') return {};
  return originalLoad.call(this, request, parent, isMain);
};

const { Hp2ModbusService } = require('../../.homeybuild/lib/modbus/protocol/hp2-modbus-service');
const { validateRefrigerant } = require('../../.homeybuild/lib/modbus/protocol/hp-modbus-registers');

test('validateRefrigerant accepts R32 and R290', () => {
  assert.strictEqual(validateRefrigerant(2).valid, true);
  assert.strictEqual(validateRefrigerant(2).name, 'R32');
  assert.strictEqual(validateRefrigerant(3).valid, true);
  assert.strictEqual(validateRefrigerant(3).name, 'R290');
  assert.strictEqual(validateRefrigerant(3).expected, 'R32/R290');
});

test('validateRefrigerant rejects R410A and unknown values', () => {
  assert.strictEqual(validateRefrigerant(1).valid, false);
  assert.strictEqual(validateRefrigerant(1).name, 'R410A');
  assert.strictEqual(validateRefrigerant(0).valid, false);
  assert.strictEqual(validateRefrigerant(0).name, 'Unknown(0)');
});

function serviceWithScale(scale) {
  const service = new Hp2ModbusService({ transport: { host: '127.0.0.1' }, temperatureRegisterScale: scale });
  const writes = [];
  service.tcp.writeSingleRegister = async (addr, value) => {
    writes.push([addr, value]);
  };
  return { service, writes };
}

test('setDiyHeatingCurve writes L27-L29 on R32 (x1)', async () => {
  const { service, writes } = serviceWithScale('x1');
  await service.setDiyHeatingCurve(-0.5, 55);
  assert.deepStrictEqual(writes, [[0x0810, 0], [0x0811, -5], [0x0812, 55]]);
});

// Temperature scale (P119 + setpoint 0x0301): see modbus-temperature-scale.test.js
