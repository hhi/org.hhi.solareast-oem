#!/usr/bin/env python3
"""Maak het Modbus-registeroverzicht van de OEM uit het overzicht van de bronrepo.

  python3 scripts/register-overview.py [--src ../org.hhi.adlar-heatpump] [--out <xlsx>]

De bronrepo heeft een Aurora I/II-registeroverzicht (xlsx). De Modbus-code van de OEM is
die code na de vertaalregels van scripts/from-upstream.py, op het koelmiddel (R32 en R290)
en een paar omschrijvingen na. Dit script:

- vertaalt alle teksten met dezelfde regels (translate() uit from-upstream.py);
- rekent elke bronverwijzing pad:regel om naar dezelfde code in deze repo, door het
  vertaalde bronbestand regel voor regel naast het OEM-bestand te leggen;
- vervangt de OEM-eigen regels in de Toelichting (reikwijdte, herkomst, temperatuur,
  koudemiddel, meetunit) en maakt de kolom over de zusterrepo leeg;
- controleert de uitkomst: zelfde rijen en kolommen, elke bronverwijzing bestaat, geen
  merknaam buiten de herkomstregel. Bij een probleem eindigt het met code 1.

Vereist openpyxl. De bronrepo moet naast deze repo staan (of geef --src op). De bronlinks
wijzen naar de commit waarop deze repo staat (git rev-parse HEAD).
"""

import argparse
import difflib
import importlib.util
import os
import re
import subprocess
import sys

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_XLSX = 'docs/Heatpump specs/modbus/HHi/Aurora-II-Modbus-registeroverzicht-nov2026.xlsx'
OUT_XLSX = 'docs/modbus/SolarEast-BLN-TB-TC-Modbus-registeroverzicht-nov2026.xlsx'
TITLE = 'SolarEast BLN-TB/BLN-TC Modbus-registeroverzicht'
UP_REPO = 'https://github.com/hhi/org.hhi.adlar-heatpump/blob/'
OEM_REPO = 'https://github.com/hhi/org.hhi.solareast-oem/blob/'

_spec = importlib.util.spec_from_file_location(
    'from_upstream', os.path.join(ROOT, 'scripts', 'from-upstream.py'))
_up = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_up)
translate = _up.translate

# Tekst die de vertaalregels anders zouden maken dan de OEM-broncode ("R32 is 0/1").
PRE_RULES = [(re.compile(r'Adlar R32'), 'R32')]

# Bronbestanden zonder tegenhanger in deze repo: de verwijzing vervalt.
NO_COUNTERPART = {'docs/Dev support/modbus/adlar2-capability-modbus-register-mapping.md'}

REF = re.compile(r'((?:lib|drivers|test|docs)/[\w./ -]+?\.(?:ts|json|md|js)):(\d+)')
BRANDS = re.compile(r'aurora|adlar|castra|zuster|intelligent-heatpump', re.I)


def read_lines(path):
    with open(path, encoding='utf8') as f:
        return f.read().split('\n')


class Overview:
    def __init__(self, src, oem_sha, up_sha):
        self.src, self.oem_sha, self.up_sha = src, oem_sha, up_sha
        self.maps, self.problems = {}, []

    def line_map(self, up_path):
        """Map upstream line numbers to OEM line numbers of the same (translated) code."""
        if up_path not in self.maps:
            a = [translate(x) for x in read_lines(os.path.join(self.src, up_path))]
            b = read_lines(os.path.join(ROOT, translate(up_path)))
            m = {}
            matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal' or (tag == 'replace' and i2 - i1 == j2 - j1):
                    for k in range(i2 - i1):
                        m[i1 + k + 1] = j1 + k + 1
            self.maps[up_path] = (m, a, b)
        return self.maps[up_path]

    def ref(self, match):
        up_path, line = match.group(1), int(match.group(2))
        m, a, b = self.line_map(up_path)
        oem_path = translate(up_path)
        if line not in m:
            self.problems.append(f'geen OEM-regel voor {up_path}:{line}')
            return match.group(0)
        if a[line - 1].strip() != b[m[line] - 1].strip():
            print(f'  let op: andere inhoud op {oem_path}:{m[line]} (tekst of commentaar?)')
        return f'{oem_path}:{m[line]}'

    def text(self, value):
        prefix = f'{UP_REPO}{self.up_sha}/'
        if value.startswith(prefix) and ' ' not in value:
            path = value[len(prefix):].replace('%20', ' ')
            if path in NO_COUNTERPART:
                return None
            return f'{OEM_REPO}{self.oem_sha}/{translate(path)}'
        for pattern, replacement in PRE_RULES:
            value = pattern.sub(replacement, value)
        return translate(REF.sub(self.ref, value))


def toelichting(oem_sha, up_sha):
    return {
        'Reikwijdte': (
            'bln-modbus-driver (SolarEast BLN-TB R32 en BLN-TC R290). '
            'Geen Tuya-DPS van bln-tuya. Bronstand 19 november 2026.'),
        'Herkomst': (
            f'hhi/org.hhi.solareast-oem @ {oem_sha}. Afgeleid van het registeroverzicht '
            f'van de bovenliggende code (hhi/org.hhi.adlar-heatpump @ {up_sha}): dezelfde '
            'registerdefinities, op hernoemingen, koudemiddel en omschrijvingen na.'),
        'Temperatuur runtime': (
            'De standaard is x1. P119=2 (R32) bepaalt x1. Bij P119=3 (R290, BLN-TC) of een '
            'ander koelmiddel beslist het verwarmingssetpoint 0x0301: raw 10–90 duidt x1 aan '
            'en 100–900 x10. Het OEM-protocol V1.2.9 noemt "X10", maar BLN-TB en BLN-TC '
            'geven hele graden. Conflicten blokkeren temperatuurwrites.'),
        'Schaalverschil zusterrepo': ('Koudemiddel', (
            'P119: 2=R32 (BLN-TB) en 3=R290 (BLN-TC) worden ondersteund '
            '(SUPPORTED_REFRIGERANTS); 1=R410A niet. De omschrijving van P119 in de '
            'metadata noemt nog "moet 2 zijn".')),
        'Hardwaremeting': (
            'Min/max-kolommen uit programma 433 / protocol 143 betreffen één BLN-TB '
            'R32-unit, vastgelegd op 11 november 2026. Niet gemeten op een BLN-TC (R290). '
            'Geen live apparaat aangesloten voor dit overzicht.'),
    }


def generate(src, out):
    wb = openpyxl.load_workbook(os.path.join(src, SRC_XLSX))
    herkomst = next(r[1].value for r in wb['Toelichting'].iter_rows()
                    if r[0].value == 'Herkomst')
    up_sha = herkomst.split('@')[1].strip()
    oem_sha = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, check=True,
                             capture_output=True, text=True).stdout.strip()
    ov = Overview(src, oem_sha, up_sha)

    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str):
                    cell.value = ov.text(cell.value)
    wb.properties.title = TITLE

    for ws in wb.worksheets:
        a2 = ws['A2'].value
        if isinstance(a2, str) and a2.endswith('Modbus-registeroverzicht'):
            ws['A2'].value = TITLE
    regs = wb['Registers']
    regs['A3'].value = regs['A3'].value.replace(
        'Eén unit, programma 433', 'Eén BLN-TB R32-unit, programma 433')

    for row in wb['Polling'].iter_rows(min_row=6):
        if row[8].value == 'Verschil zusterrepo':
            row[8].value = 'Opmerking'
        elif isinstance(row[8].value, str) and 'Zusterrepo' in row[8].value:
            row[8].value = None

    toe = wb['Toelichting']
    texts = toelichting(oem_sha, up_sha)
    empty_sources = []
    for r in range(1, toe.max_row + 1):
        key = toe.cell(r, 1).value
        if key in texts:
            new = texts[key]
            if isinstance(new, tuple):
                toe.cell(r, 1).value, toe.cell(r, 2).value = new
            else:
                toe.cell(r, 2).value = new
        elif key == 'Bron' and toe.cell(r, 2).value is None:
            empty_sources.append(r)
    for r in reversed(empty_sources):
        toe.delete_rows(r)

    os.makedirs(os.path.dirname(os.path.join(ROOT, out)), exist_ok=True)
    wb.save(os.path.join(ROOT, out))
    return ov.problems + check(src, out)


def check(src, out):
    problems = []
    old = openpyxl.load_workbook(os.path.join(src, SRC_XLSX), read_only=True)
    new = openpyxl.load_workbook(os.path.join(ROOT, out), read_only=True)
    lengths = {}
    for ws in new.worksheets:
        old_rows = list(old[ws.title].iter_rows(values_only=True))
        rows = list(ws.iter_rows(values_only=True))
        drop = 1 if ws.title == 'Toelichting' else 0
        cols, old_cols = max(map(len, rows)), max(map(len, old_rows))
        if len(rows) != len(old_rows) - drop or cols != old_cols:
            problems.append(f'{ws.title}: {len(rows)}x{cols} tegen {len(old_rows)}x{old_cols}')
        for row in rows:
            for value in row:
                if not isinstance(value, str):
                    continue
                if BRANDS.search(value) and not value.startswith('hhi/org.hhi.solareast-oem @'):
                    problems.append(f'{ws.title}: merknaam in "{value[:60]}"')
                for path, line in REF.findall(value):
                    full = os.path.join(ROOT, path)
                    if full not in lengths:
                        lengths[full] = len(read_lines(full)) if os.path.exists(full) else 0
                    if int(line) > lengths[full]:
                        problems.append(f'{ws.title}: verwijzing bestaat niet: {path}:{line}')
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--src', default=os.path.join(ROOT, '..', 'org.hhi.adlar-heatpump'))
    parser.add_argument('--out', default=OUT_XLSX)
    args = parser.parse_args()
    problems = generate(args.src, args.out)
    for p in problems:
        print('PROBLEEM:', p)
    print(f'{args.out}: ' + ('in orde' if not problems else f'{len(problems)} problemen'))
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
