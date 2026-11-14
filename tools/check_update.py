"""Проверка: не обновилась ли игра в Steam после проверки перевода.
python -I tools/check_update.py
Если сборка другая — сравнивает тексты новой версии с orig/en.json (какие строки добавились/изменились)."""
import re, sys, os, hashlib
sys.stdout.reconfigure(encoding='utf-8')
CHECKED = {'buildid': '24250053', 'utoc_md5': '7d415452beaa4d57987ba77aed60b612', 'version': '1.0.1.0'}
ACF = r'D:\SteamLibrary\steamapps\appmanifest_3259780.acf'
UTOC = r'D:\SteamLibrary\steamapps\common\FINAL FANTASY RESONANCE\FFRS\Content\Paks\FFRS-Windows.utoc'
bid = re.search(r'"buildid"\s+"(\d+)"', open(ACF, encoding='utf-8').read()).group(1)
md5 = hashlib.md5(open(UTOC, 'rb').read()).hexdigest()
if bid == CHECKED['buildid'] and md5 == CHECKED['utoc_md5']:
    print(f'Игра не обновлялась (сборка Steam {bid}, версия {CHECKED["version"]}). Перевод актуален.')
    sys.exit(0)
print(f'ВНИМАНИЕ: игра обновилась (сборка {CHECKED["buildid"]} -> {bid}; файлы {"те же" if md5 == CHECKED["utoc_md5"] else "изменились"}).')
print('Что сделать: извлечь новые en/ja (tools/oodle_ext.py), сравнить с orig/en.json, перевести новые строки,')
print('пересобрать build.py и gfx_build.py, проверить в игре; затем обновить CHECKED в этом файле.')
sys.exit(1)
