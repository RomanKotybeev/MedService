from django import template
import re

by_values = [
    'Дата рождения', 'Дата осмотра', 'Дата заболевания', 'Возраст',
    'Время поступления', 'Время заболевания', 'рост', 'вес', 'IMT',
    'давление диаст', 'давление сист', 'температура поступления',
    'мах температура', 'аллергическая реакция',
]

others = [
    'др заболевания в анамнезе',
    'предрасполагающие факторы',
    'провоцирущие факторы'
]

by_keys = [
    'озноб', 'слабость', 'вялость', 'головная боль',
    'нарушение сна', 'нарушение аппетита', 'ломота', 'тошнота', 'нарушение сознания',
    'Судороги', 'Парестезии', 'эритема', 'с четкими границами', 'валик', 'боль', 'Гиперемия',
    'Отек', 'Лимфаденит', 'Лимфангит', 'речная рыба',
    'сопутствующий диагноз', 'основной диагноз'
]

register = template.Library()


@register.filter(name='mark')
def mark(text, features):
    for key, value in features.items():
        if value is not None:
            reg = '[,| |\.|?|!]+'
            if key in by_keys:
                text = text.replace(key, '<mark>%s</mark>' % key.lower())
                # pattern = key + reg
                # marked = '<mark>%s</mark> ' % key
            if key in by_values:
                feature = str(value)
                # pattern = str(value) + reg
                # marked = '<mark>%s</mark> ' % str(value)
                text = text.replace(feature, '<mark>%s</mark>' % feature)
            # print(re.sub(pattern, marked, text))
            # text = re.sub(pattern, marked, text)
    return text

# @register.filter(name='mark')
# def mark(text, feat_indices):
#     output_parts = list()
#     text = text.replace('\ufeff', '')
#     text = text.replace('\n', ' \n ')
#     text = text.replace('\\', ' ')
#     text = text.replace('<mark>', ' ')
#     text = text.replace('</mark>', ' ')
#     last_index = 0
#     cleared_feat_indices = sort_indices(feat_indices)
#     for indices in cleared_feat_indices:
#         start = indices[0]
#         stop = indices[1]
#         print(start, stop, end=', ')
#         marked = [text[last_index:start], '<mark>',
#                   text[start:stop], '</mark>']
#         last_index = stop
#
#         output_parts.extend(marked)
#
#     output_parts.append(text[last_index:])
#     res = ''.join(output_parts)
#     return res
#
#
# def sort_indices(feat_indices):
#     filtered = []
#     for key, value in feat_indices.items():
#         if value:
#             if isinstance(value, list):
#                 for item in value:
#                     if not isinstance(item, int):
#                         filtered.append(item)
#             elif not isinstance(value, int):
#                 filtered.append(value)
#     filtered.sort()
#     return filtered
