#!/usr/bin/env python3
"""Vertaal de bronrepo naar de OEM-repo (route 1).

Twee modi:

  export --src <bronrepo> --rev <commit> --out <map>
      Schrijft de bestanden van <commit> vertaald naar <map>. Uitgesloten paden
      worden overgeslagen. Leest uit git, niet uit de werkmap.

  patch < bron.patch > oem.patch
      Vertaalt een `git format-patch`-uitvoer. Bestanden die uitgesloten zijn,
      vallen uit de patch; paden en regels worden met dezelfde regels vertaald.

De regels zijn bijectief op de bron: `check --src <bronrepo> --rev <commit>`
toetst dat geen vertaalde naam al als onvertaalde naam in de bron voorkomt.

Alleen standaardbibliotheek. Zichtbare tekst, het verwijderen van Aurora III uit
gedeelde code en afbeeldingen zijn handwerk in de OEM-repo; dit script raakt ze
niet anders dan met de regels hieronder.
"""

import argparse
import fnmatch
import os
import re
import subprocess
import sys

# --------------------------------------------------------------------------
# Regels
# --------------------------------------------------------------------------

# Volgorde is belangrijk: specifiek vóór algemeen.
CONTENT_RULES = [
    (re.compile(r'org\.hhi\.adlar-heatpump(?![\w-])'), 'org.hhi.solareast-oem'),
    (re.compile(r'\|intelligent-heatpump-aurora3'), ''),
    (re.compile(r'intelligent-heatpump-modbus'), 'bln-modbus'),
    (re.compile(r'intelligent-heat-pump'), 'bln-tuya'),
    # Proza (vóór adlar→hp, dus op de upstreamtekst). Aurora I/II is de R32-reeks:
    # BLN-TB. Aurora III en "Aurora (I/)II and III" blijven staan, zodat de
    # merkcheck ze als handwerk aanwijst.
    (re.compile(r'Adlar Castra Aurora II(?!I)'), 'SolarEast BLN-TB'),
    (re.compile(r'Adlar Castra'), 'SolarEast'),
    (re.compile(r'Adlar Aurora II(?!I)'), 'BLN-TB'),
    (re.compile(r'Adlar Custom'), 'Custom'),
    (re.compile(r'Aurora I/II(?! and III)'), 'BLN-TB'),
    (re.compile(r'Aurora II(?!I| and III)'), 'BLN-TB'),
    (re.compile(r'adlar'), 'hp'),
    (re.compile(r'Adlar'), 'Hp'),
    (re.compile(r'ADLAR'), 'HP'),
    (re.compile(r'aurora2'), 'bln'),
    (re.compile(r'Aurora2'), 'Bln'),
    (re.compile(r'AURORA2'), 'BLN'),
]

EXCLUDE_PREFIXES = [
    'docs/',
    'lib/aurora3/',
    'drivers/intelligent-heatpump-aurora3/',
    'public/aurora3/',
    'test/aurora3/',
    'test/unit/aurora3/',
    'scripts/migration/aurora3/',
    '.claude/',
    '.agents/',
    'todo/',
    'plans/',
]

EXCLUDE_FILES = {
    'app.json',  # gegenereerd uit .homeycompose; in de OEM-repo opnieuw bouwen
    'CLAUDE.md',
    'AGENTS.md',
    'GEMINI.md',
    '.homeychangelog.json',
    'org.hhi.adlar-heatpump.code-workspace',
    '.github/copilot-instructions.md',
    '.github/workflows/claude.yml',
    '.github/workflows/claude-code-review.yml',
    # Eenmalige migratiescripts van de samenvoeging (verify.py blijft)
    'scripts/migration/01-restructure-lib.py',
    'scripts/migration/02-import-modbus.py',
    'scripts/migration/03-split-flowcards.py',
    'scripts/migration/04-split-capabilities.py',
    'scripts/migration/05-merge-app-ts.py',
}

# Eigen bestanden van de OEM-repo (store-teksten, README, app-icoon,
# driverafbeeldingen). Paden in upstreamvorm. Upstreamwijzigingen vallen eruit;
# de patchmodus meldt ze, zodat de OEM-versie zo nodig met de hand volgt.
OWN_FILES = {
    'README.md',
    'README.txt',
    'README.en.txt',
    'README.nl.txt',
    'readme.de.txt',
    'readme.fr.txt',
    'assets/icon.svg',
    'assets/adlar-icon-white.svg',
    'assets/adlar-icon-yellow.svg',
    'drivers/intelligent-heatpump-modbus/assets/icon.svg',
}
for _drv in ('intelligent-heat-pump', 'intelligent-heatpump-modbus'):
    for _size in ('small', 'large', 'xlarge'):
        OWN_FILES.add(f'drivers/{_drv}/assets/images/Aurora2-drv-{_size}.png')
EXCLUDE_FILES |= OWN_FILES

EXCLUDE_GLOBS = [
    '.homeycompose/flow/*/*_aurora3.json',
]

# Flowkaarten zonder suffix die alleen voor Aurora III zijn
AURORA3_ONLY_FLOWCARDS = [
    'silent_mode_is', 'dhw_heating_active', 'set_silent_mode',
    'set_dhw_function', 'set_backup_heater',
]

# Capabilities die alleen Aurora III gebruikt, en twee die nergens gebruikt worden
EXCLUDED_CAPABILITIES = [
    'adlar_backup_heater_forced', 'adlar_compressor_on', 'adlar_dhw_active',
    'adlar_dhw_enabled', 'adlar_disinfection_enabled', 'adlar_high_pressure',
    'adlar_low_pressure', 'adlar_mode_aurora3', 'adlar_silent_mode',
    'adlar_measure_pressure_effluent_temp', 'adlar_measure_pressure_temp_current',
]

for _card in AURORA3_ONLY_FLOWCARDS:
    EXCLUDE_GLOBS.append(f'.homeycompose/flow/*/{_card}.json')
for _cap in EXCLUDED_CAPABILITIES:
    EXCLUDE_FILES.add(f'.homeycompose/capabilities/{_cap}.json')


def is_excluded(path):
    if path in EXCLUDE_FILES:
        return True
    if any(path.startswith(p) for p in EXCLUDE_PREFIXES):
        return True
    return any(fnmatch.fnmatchcase(path, g) for g in EXCLUDE_GLOBS)


def translate(text):
    for pattern, repl in CONTENT_RULES:
        text = pattern.sub(repl, text)
    return text


def is_binary(data):
    if b'\0' in data[:8192]:
        return True
    try:
        data.decode('utf-8')
    except UnicodeDecodeError:
        return True
    return False


# --------------------------------------------------------------------------
# Git-hulpjes
# --------------------------------------------------------------------------

def git(src, *args):
    return subprocess.run(['git', '-C', src, *args], check=True,
                          capture_output=True).stdout


def list_files(src, rev):
    out = git(src, 'ls-tree', '-r', '-z', '--name-only', rev)
    return [p for p in out.decode('utf-8').split('\0') if p]


# --------------------------------------------------------------------------
# export
# --------------------------------------------------------------------------

def cmd_export(args):
    files = list_files(args.src, args.rev)
    kept = 0
    skipped = 0
    for path in files:
        if is_excluded(path):
            skipped += 1
            continue
        data = git(args.src, 'show', f'{args.rev}:{path}')
        if not is_binary(data):
            data = translate(data.decode('utf-8')).encode('utf-8')
        dest = os.path.join(args.out, translate(path))
        os.makedirs(os.path.dirname(dest) or '.', exist_ok=True)
        with open(dest, 'wb') as fh:
            fh.write(data)
        kept += 1
    print(f'export: {kept} bestanden geschreven, {skipped} uitgesloten', file=sys.stderr)


# --------------------------------------------------------------------------
# patch
# --------------------------------------------------------------------------

DIFF_HEADER = re.compile(r'^diff --git a/(.+?) b/(.+)$')
MAIL_START = re.compile(r'^From [0-9a-f]{40} ')
MAIL_FROM = re.compile(r'^(From: .*<)[^>]*(>\s*)$')


def author_email():
    """Het auteursadres voor overgezette commits.

    Uit OEM_AUTHOR_EMAIL, anders uit de *lokale* git-config van de map waarin
    het script draait (de OEM-repo). Nooit de globale config: daar staat mogelijk
    een privéadres. Zonder adres weigert de patchmodus.
    """
    email = os.environ.get('OEM_AUTHOR_EMAIL', '').strip()
    if email:
        return email
    try:
        res = subprocess.run(['git', 'config', '--local', 'user.email'],
                             capture_output=True, text=True, check=False)
    except OSError:
        return None
    return res.stdout.strip() or None


def cmd_patch(_args):
    email = author_email()
    if not email:
        print('patch: geen auteursadres; zet `git config --local user.email` in de '
              'OEM-repo of OEM_AUTHOR_EMAIL', file=sys.stderr)
        return 2
    raw = sys.stdin.buffer.read().decode('utf-8', errors='surrogateescape')
    lines = raw.splitlines(keepends=True)
    in_mail_header = False

    out = []
    dropped = []
    block = []          # regels van het huidige bestandsblok
    block_path = None   # bronpad van het huidige blok
    in_binary = False

    def flush():
        nonlocal block, block_path
        if block_path is not None and is_excluded(block_path):
            dropped.append(block_path)
        else:
            out.extend(block)
        block = []
        block_path = None

    for line in lines:
        m = DIFF_HEADER.match(line.rstrip('\n'))
        if m:
            flush()
            block_path = m.group(1)
            in_binary = False
            block.append(translate(line))
            continue
        if block_path is None:
            if MAIL_START.match(line):
                in_mail_header = True
            elif in_mail_header and line.strip() == '':
                in_mail_header = False
            if in_mail_header and line.startswith('From: '):
                # Auteursadres vervangen; de naam blijft als herkomst staan
                m_from = MAIL_FROM.match(line)
                if not m_from:
                    print('patch: onbekende From-regel, gestopt', file=sys.stderr)
                    return 2
                out.append(translate(f'{m_from.group(1)}{email}{m_from.group(2)}'))
                continue
            # Kop van de commit of afsluiting (`-- `, versieregel): vertalen
            out.append(line if line == '-- \n' else translate(line))
            continue
        if line.startswith('GIT binary patch'):
            in_binary = True
            block.append(line)
            continue
        if in_binary:
            # base85-gegevens nooit vertalen
            block.append(line)
            continue
        if line.startswith('index '):
            block.append(line)
            continue
        if line == '-- \n':
            # einde van de patch in format-patch-uitvoer
            flush()
            out.append(line)
            continue
        block.append(translate(line))
    flush()

    for path in dropped:
        print(f'patch: uitgesloten {path}', file=sys.stderr)
        if path in OWN_FILES:
            print(f'patch: LET OP — upstream wijzigde {path}; de OEM-versie is eigen werk, '
                  'kijk of die bijgewerkt moet worden', file=sys.stderr)
    if not any(DIFF_HEADER.match(line.rstrip('\n')) for line in out):
        print('patch: niets over na uitsluiting; overslaan', file=sys.stderr)
        return 3
    sys.stdout.buffer.write(''.join(out).encode('utf-8', errors='surrogateescape'))
    return 0


# --------------------------------------------------------------------------
# check
# --------------------------------------------------------------------------

TOKEN = re.compile(r'[A-Za-z0-9_.\-|/]+')


def cmd_check(args):
    tokens = set()
    for path in list_files(args.src, args.rev):
        if is_excluded(path):
            continue
        tokens.add(path)
        data = git(args.src, 'show', f'{args.rev}:{path}')
        if is_binary(data):
            continue
        tokens.update(TOKEN.findall(data.decode('utf-8')))
    collisions = []
    for tok in tokens:
        new = translate(tok)
        if new != tok and new in tokens:
            collisions.append((tok, new))
    for old, new in sorted(collisions):
        print(f'botsing: {old} -> {new}')
    print(f'check: {len(collisions)} botsingen', file=sys.stderr)
    return 1 if collisions else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='cmd', required=True)
    p_export = sub.add_parser('export')
    p_export.add_argument('--src', required=True)
    p_export.add_argument('--rev', default='HEAD')
    p_export.add_argument('--out', required=True)
    sub.add_parser('patch')
    p_check = sub.add_parser('check')
    p_check.add_argument('--src', required=True)
    p_check.add_argument('--rev', default='HEAD')
    args = parser.parse_args()
    if args.cmd == 'export':
        cmd_export(args)
        return 0
    if args.cmd == 'patch':
        return cmd_patch(args)
    return cmd_check(args)


if __name__ == '__main__':
    sys.exit(main())
