"""Подпись переводчика в первой строке копирайта титульного экрана -> edits/95_credit.json
(третья строка наезжает на номер версии, поэтому только так)."""
import json
S = '␟'
ru = json.load(open('ru/ru.json', encoding='utf-8'))
k = 'ST_UI_TitleMenu' + S + 'UI_Title_Copyright'
new = ru[k].replace('© SQUARE ENIX ', '© SQUARE ENIX   РУССКИЙ ПЕРЕВОД: MAKSAMI', 1).replace('ИЛЛЮСТРАЦИЯ ЛОГОТИПА:', 'LOGO ILLUSTRATION:')
# копирайт оставляем в оригинале
json.dump({k: new}, open('edits/95_credit.json', 'w', encoding='utf-8'), ensure_ascii=False)
