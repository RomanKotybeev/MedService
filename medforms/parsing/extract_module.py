#!/usr/bin/env python
# coding: utf-8

from yargy import rule, and_, or_, Parser, not_
from yargy.predicates import gram, normalized, caseless, gte, lte, in_
from yargy.pipelines import morph_pipeline
from datetime import datetime
from yargy.tokenizer import MorphTokenizer
import time
import re
import pymorphy2
import os
morph = pymorphy2.MorphAnalyzer()


def extract(text):
    with open(os.path.join(os.getcwd(), 'list_diseases/diseases'), encoding='utf-8') as f:
        diseases = f.read().split('\n')

    text = text.replace('\ufeff', '')
    text = text.replace('\n', ' \n ')
    text = text.replace('\\', ' ')

    symptoms = ['Дата рождения', 'Дата осмотра','Дата заболевания', 'Возраст', 'Болен дней','Болен часов','Возраст в днях','Время поступления', 
                'Время заболевания', 'рост','вес', 'IMT', 'давление диаст', 'давление сист', 'температура поступления','мах температура',
                'пол', 'др заболевания в анамнезе', 'побочное действие лекартсв','аллергическая реакция', 'озноб', 'слабость', 'вялость','головная боль', 
                'нарушение сна', 'нарушение аппетита', 'ломота','тошнота', 'нарушение сознания', 'Судороги', 'Парестезии', 'эритема', 
                'с четкими границами', 'валик', 'боль','Гиперемия', 'Отек', 'Лимфаденит', 'Лимфангит', 'квартира, дом','контакт с зараженными','речная рыба','провоцирущие факторы',
                'предрасполагающие факторы','кол-во сопут заболеваний','соц категория','сопутствующий диагноз','основной диагноз', 'контакт с зараженными', 'пищевой анамнез',
                'раневые ворота', 'аллергия на лекарства', 'клещ', 'географический анамнез', 'вредные привычки', 'домашние животные', 'условия труда','избыточное питание',
                'бытовые условия', 'питание', 'интоксикация', 'ЧСС', 'болезненность лимфоузлов', 'увеличенность лимфоузлов','размер лимфоузлов', 'острое начало']

    dict_symp = dict.fromkeys(symptoms)

    dates_lst = []

    # Rule for dates detecting
    DAY = and_(gte(1),lte(31))
    MONTH = and_(gte(1),lte(12))
    YEAR = and_(gte(1),lte(19))
    YEARFULL = and_(gte(1900),lte(2020))
    DATE = or_(
        rule(YEAR,'.',MONTH,'.',DAY),
        rule(DAY,'.',MONTH,'.',YEAR),
        rule(DAY,'.',MONTH,'.',YEARFULL),
        rule(DAY,'.',MONTH),
        rule(DAY,'.',MONTH,YEARFULL),
        rule(DAY,'.',MONTH,YEAR))

    parser = Parser(DATE)
    for match in parser.findall(text):
        dates_lst.append(''.join([_.value for _ in match.tokens]))

    # Sometimes we dont have information about birthday and we should check difference between years
    # in first two dates to determine there is information about birthday or not
    if int(dates_lst[1][-2:])-int(dates_lst[0][-2:])<0:
        # According medical cards dates have this order
        dict_symp['Дата рождения'] = dates_lst[0]
        dict_symp['Дата осмотра'] = dates_lst[1]
        dict_symp['Дата заболевания'] = dates_lst[2]
    else: 
        birth = None
        dict_symp['Дата осмотра'] = dates_lst[0]
        dict_symp['Дата заболевания'] = dates_lst[1]

    # If date was written without year, we take year from previous date
    if len(dict_symp['Дата заболевания'])==5:
        dict_symp['Дата заболевания'] += dict_symp['Дата осмотра'][dict_symp['Дата осмотра'].rfind('.'):]

    # Rule for detecring dates with such situation "болен 5 дней"
    DAY_RULE = morph_pipeline(['дней'])
    parser = Parser(DAY_RULE)
    day_lst = []
    for match in parser.findall(text):
        day_lst.append((match.span, [_.value for _ in match.tokens]))

    if day_lst and dict_symp['Дата заболевания'] is None:
        dict_symp['Дата заболевания'] = text[day_lst[0][0][0]-20:day_lst[0][0][0]+20]
        dict_symp['Дата заболевания'] = re.findall(r'\d+', dict_symp['Дата заболевания'])[0]
        dict_symp['Дата заболевания'] = str(int(dict_symp['Дата осмотра'][:2])-int(dict_symp['Дата заболевания']))
        dict_symp['Дата заболевания'] = dict_symp['Дата заболевания']+dict_symp['Дата осмотра'][2:]

    # Rule for detecting Age
    age_lst = []

    AGE = and_(gte(0),lte(100))
    AGE_RULE = or_(rule("(",AGE,")"),
                  rule(gram('ADJF'),",",AGE))

    parser = Parser(AGE_RULE)
    for match in parser.findall(text):
        s = ''.join([_.value for _ in match.tokens])
        age_lst.append((re.findall(r'\d+', s)[0]))

    if age_lst:
        dict_symp['Возраст'] = int(age_lst[-1])
    
    # Transform dates to datetime format to make calculations
    try:
        d1 = datetime.strptime(dict_symp['Дата осмотра'], '%d.%m.%Y')
    except:
        d1 = datetime.strptime(dict_symp['Дата осмотра'], '%d.%m.%y')
        d1 = d1.strftime('%d.%m.%Y')
        d1 = datetime.strptime(d1, '%d.%m.%Y')
    try:
        d2 = datetime.strptime(dict_symp['Дата заболевания'], '%d.%m.%Y')
    except:
        d2 = datetime.strptime(dict_symp['Дата заболевания'], '%d.%m.%y')
        d2 = d2.strftime('%d.%m.%Y')
        d2 = datetime.strptime(d2, '%d.%m.%Y')

    dict_symp['Болен дней'] = (d1 - d2).days
    dict_symp['Болен часов'] = (int(dict_symp['Болен дней'])-1)*24

    if dict_symp['Дата рождения'] is None:
        dict_symp['Возраст в днях'] = int(dict_symp['Возраст'])*365
    else:
        d1 = datetime.strptime(dict_symp['Дата осмотра'], '%d.%m.%Y')
        d2 = datetime.strptime(dict_symp['Дата рождения'], '%d.%m.%Y')
        dict_symp['Возраст в днях'] = (d1 - d2).days

    # Rule for time detecting
    time_lst = []
    time_spans = []

    HOURS = and_(gte(0),lte(24))

    MINUTES = and_(gte(0),lte(59))

    TIME = or_(rule(HOURS,':',MINUTES),
               rule(HOURS, normalized('час')),)

    parser = Parser(TIME)
    for match in parser.findall(text):
        s = (''.join([_.value for _ in match.tokens]))
        time_spans.append(match.span)
        s = s.replace('часов', ':00')
        s = s.replace('час', ':00')
        time_lst.append(s)

    # if we have only 1 date 'Время поступления' = 'Время заболевания'
    if time_lst: 
        dict_symp['Время поступления'] = time_lst[0]
        dict_symp['Время заболевания'] = time_lst[0]
        dict_index['Время поступления'] = time_spans[0]
        dict_index['Время заболевания'] = time_spans[0]
    if len(time_lst)>1: 
        dict_symp['Время заболевания'] = time_lst[1]
        dict_index['Время заболевания'] = time_spans[1]

    t1 = dict_symp['Время поступления']
    t2 = dict_symp['Время заболевания']
    delta = int(t1[:t1.find(':')])+24-int(t2[:t2.find(':')])
    dict_symp['Болен часов'] = dict_symp['Болен часов'] + delta

    # Rules for detecting Weight, Height and IMT
    HEIGHT = and_(gte(50),lte(250))
    WEIGHT = and_(gte(10),lte(150))

    HEIGHT_RULE = or_(rule(normalized('рост'),'-',HEIGHT),
                      rule(normalized('рост'),'–',HEIGHT),
                      rule(normalized('рост'),':',HEIGHT),
                      rule(normalized('рост'),HEIGHT))

    WEIGHT_RULE = or_(rule(normalized('вес'),'-',WEIGHT),
                      rule(normalized('вес'),'–',WEIGHT),
                      rule(normalized('вес'),':',WEIGHT),
                      rule(normalized('вес'),WEIGHT))

    height = None
    parser = Parser(HEIGHT_RULE)
    for match in parser.findall(text):
        height = (''.join([_.value for _ in match.tokens]))
        height = re.findall(r'\d+', height)[0]

    if height:
        dict_symp['рост'] = int(height)

    weight = None
    parser = Parser(WEIGHT_RULE)
    for match in parser.findall(text):
        weight = (''.join([_.value for _ in match.tokens]))
        weight = re.findall(r'\d+', weight)[0]

    if weight:
        dict_symp['вес'] = int(weight)

    if (dict_symp['рост'] is not None) and (dict_symp['вес'] is not None):
        dict_symp['IMT'] = round(dict_symp['вес']/(dict_symp['рост']/100*dict_symp['рост']/100),2)

    # Rules for detecting pressure
    ADSIST = and_(gte(50),lte(250))
    ADDIAST = and_(gte(20),lte(200))

    PRES_RULE = or_(rule('АД', ADSIST,'/',ADDIAST),
                    rule('АД', ADSIST,ADDIAST),
                    rule('АД', ADSIST, ':',ADDIAST),
                    rule('АД','-', ADSIST, '/',ADDIAST),
                    rule('А/Д', ADSIST, '/',ADDIAST),
                    rule('А/Д', ADSIST, ADDIAST),
                    rule('А/Д',' ', ADSIST, '/',ADDIAST),
                    rule(ADSIST, '/',ADDIAST))

    pres = None
    parser = Parser(PRES_RULE)
    for match in parser.findall(text):
        pres = (''.join([_.value for _ in match.tokens]))
        pres = re.findall(r'\d+', pres)

    if pres:
        dict_symp['давление сист'] = int(pres[0])
        dict_symp['давление диаст'] = int(pres[1])

    # Rule for detecting Pulse
    PULSE = and_(gte(40),lte(150))

    PULSE_RULE = or_(rule('ЧСС','-',PULSE),
                     rule('ЧСС',PULSE),
                     rule('ЧСС','-',PULSE),
                     rule('ЧСС','/',PULSE),
                     rule('пульс',PULSE),)

    pulse = None
    parser = Parser(PULSE_RULE)
    for match in parser.findall(text):
        pulse = (''.join([_.value for _ in match.tokens]))
        pulse = re.findall(r'\d+', pulse)

    if pulse:
        dict_symp['ЧСС'] = int(pulse[0])

    #Rules for detecting temperatures
    DEGREES = and_(gte(34),lte(42))
    SUBDEGREES = and_(gte(0),lte(9))

    TEMP_RULE = or_(rule(DEGREES,',',SUBDEGREES),
                    rule(DEGREES,'.',SUBDEGREES),
                    rule(DEGREES))
    
    # Find 'Объективный статус', because this pert contains information about 'температура поступления'
    status = text[text.find('Объективный статус'): 
                  text.find('Объективный статус')+text[text.find('Объективный статус')+1:].find(' \n  \n')]
    temp_lst = []
    parser = Parser(TEMP_RULE)
    for match in parser.findall(status):
        temp_lst.append(''.join([_.value for _ in match.tokens]))

    if temp_lst:
        dict_symp['температура поступления'] = temp_lst[0]

    # Find temperatures in whole text
    temp_text = text[text.find('Жалобы'):]
    temp_lst = []
    parser = Parser(TEMP_RULE)
    for match in parser.findall(temp_text):
        temp_lst.append(''.join([_.value for _ in match.tokens]))

    if temp_lst:
        if dict_symp['температура поступления'] is None:
            dict_symp['температура поступления'] = temp_lst[0]
        dict_symp['мах температура'] = max([float(i.replace(',','.')) for i in temp_lst])

    # Rule for detecting Sex
    sex_lst = []
    SEX_RULE = or_(rule(normalized('женский')),
                     rule(normalized('мужской')))

    parser = Parser(SEX_RULE)
    for match in parser.findall(text):
        sex_lst.append(''.join([_.value for _ in match.tokens]))

    if sex_lst:
        dict_symp['пол'] = sex_lst[0]
        dict_symp['пол'] = dict_symp['пол'].lower().replace('женский', '2')
        dict_symp['пол'] = dict_symp['пол'].lower().replace('мужской', '1')
        dict_symp['пол'] = int(dict_symp['пол'])

    # Rule for detecting DISEASES
    DISEASES_RULE = morph_pipeline(diseases[:-1])

    # anamnez contains information about diseases of patient, but family anamnez contains 
    # information about diseases of patient, and we should remove this part
    anamnez = text[text.find('Анамнез'): text.find('Анамнез')+text[text.find('Анамнез')+1:].rfind('Анамнез')]
    family = anamnez[anamnez.find('Семейный'):anamnez.find('Семейный')+60]
    if family:
        anamnez = anamnez.replace(family,' ')
    anamnez = anamnez[:anamnez.rfind('Диагноз')]
    dis_lst = []
    parser = Parser(DISEASES_RULE)
    for match in parser.findall(anamnez):
        dis_lst.append(' '.join([_.value for _ in match.tokens]))

    # Special rule for описторхоз
    OP_RULE = or_(rule(normalized('описторхоз'), not_(normalized('не'))))
    parser = Parser(OP_RULE)
    op_lst = []
    for match in parser.findall(anamnez):#text
        op_lst.append((match.span, [_.value for _ in match.tokens]))
    if op_lst:
        dis_lst.append(' описторхоз')

    # Special rule for туберкулез
    TUB_RULE = rule(normalized('туберкулез'), not_(normalized('отрицает')))
    parser = Parser(TUB_RULE)
    tub_lst = []
    for match in parser.findall(anamnez):#text
        tub_lst.append((match.span, [_.value for _ in match.tokens]))
    if tub_lst:
        dis_lst.append(' туберкулез')
    
    if dis_lst:
        dis_lst = list(set(dis_lst))
        dict_symp['др заболевания в анамнезе'] = ', '.join(dis_lst)
        dict_symp['др заболевания в анамнезе'] = morph.parse(dict_symp['др заболевания в анамнезе'])[0].normal_form
        
    # Rule for allergy
    ALLERG_RULE = or_(rule(normalized('Аллергическая'),normalized('реакция'), normalized('на')),
                      rule(normalized('не'),normalized('переносит')))

    all_lst = []
    parser = Parser(ALLERG_RULE)
    for match in parser.findall(text):
        all_lst.append((list(match.span), [_.value for _ in match.tokens]))
    if all_lst:
        index = all_lst[0][0][1]
        dict_symp['аллергическая реакция'] = text[index:text[index:].find('.')+index]

    # Rules for different symptoms
    symptoms = [['озноб', 'познабливание'], 'слабость', ['вялость', 'разбитость'],'головная боль', 'нарушение сна', 
                'нарушение аппетита', 'ломота','тошнота', 'нарушение сознания','Судороги', 'Парестезии', ['эритема', 
                'эритематозная', 'эритематозно'], ['с четкими границами', 'границами четкими', 'четкими неровными краями',
                'с четкими краями', 'краями четкими' , 'четкими неровными краями', 'четкими контурами', 'языков пламени'], 
                ['валик', 'вал'], 'боль',['Гиперемия', 'гиперемирована'], 'Отек', 'Лимфангит', ['рана', "раневые ворота", 
                "входные ворота"],['клещ', "присасывание"], 'интоксикация', 'острое начало']
                
    for i in symptoms:
        sym_lst = []
        if isinstance(i, str):
            SYM_RULE = morph_pipeline([i])
            parser = Parser(SYM_RULE)
            for match in parser.findall(text):
                sym_lst.append(' '.join([_.value for _ in match.tokens]))
            if sym_lst:
                dict_symp[i] = 1
            else:
                dict_symp[i] = 0
        else:
            SYM_RULE = morph_pipeline(i)
            parser = Parser(SYM_RULE)
            for match in parser.findall(text):
                sym_lst.append(' '.join([_.value for _ in match.tokens]))
            if sym_lst:
                dict_symp[i[0]] = 1
            else:
                dict_symp[i[0]] = 0

    #This fuction used for features which have the same rule
    def find_feature(feature, RULE, RULE2, space=[40,40]):
        parser = Parser(RULE)
        lst = []
        for match in parser.findall(text):
            lst.append((match.span, [_.value for _ in match.tokens]))
        if lst:
            add_text = text[list(match.span)[1]-space[0]:list(match.span)[1]+space[1]]
            parser = Parser(RULE2)
            lst = []
            for match in parser.findall(add_text):
                lst.append((match.span, [_.value for _ in match.tokens]))
            if lst:
                dict_symp[feature] = 1
            else:
                dict_symp[feature] = 0
    
    GEO_RULE = morph_pipeline(['географический', 'выезжал'])
    GEO_RULE2 = rule(not_(normalized('не')),normalized('выезжал'))
    geo_space = [40,40]
    
    COND_RULE = morph_pipeline(['бытовые'])
    COND_RULE2 = rule(not_(normalized('не')),normalized('удовлетворительные'))
    cond_space = [0,60]
    SEC_COND_RULE = morph_pipeline(['Социально-бытовые'])
    sec_cond_space = [0,60]
    
    WORK_COND_RULE = morph_pipeline(['условия труда'])
    work_cond_space = [20,20]
    
    CONTACT_RULE = morph_pipeline(['контакт'])
    CONTACT_RULE2 = morph_pipeline(['да'])
    contact_space = [0,40]
    
    WATER_RULE = morph_pipeline(['сырой воды'])
    WATER_RULE2 = morph_pipeline(['не было', 'отрицает', 'нет'])
    water_space = [80,80]

    features = ['географический анамнез', 'бытовые условия', 'бытовые условия',
               'условия труда','контакт с зараженными','пищевой анамнез']
    rules = [GEO_RULE, COND_RULE, SEC_COND_RULE, WORK_COND_RULE,
            CONTACT_RULE, WATER_RULE]
    sec_rules = [GEO_RULE2, COND_RULE2, COND_RULE2, COND_RULE2,
            CONTACT_RULE2, WATER_RULE2]
    spaces = [geo_space, cond_space, sec_cond_space, work_cond_space,
             contact_space, water_space]
    
    for i in range(len(features)):
        find_feature(features[i],rules[i],sec_rules[i],spaces[i])

    # Rules for bad habbits
    HAB_RULE = morph_pipeline(['вредные привычки', 'алкоголь'])
    parser = Parser(HAB_RULE)
    hab_lst = []
    for match in parser.findall(text):
        hab_lst.append((match.span, [_.value for _ in match.tokens]))
    if hab_lst:
        text_hab = text[list(match.span)[1]-80:list(match.span)[1]+80]
        HAB_RULE = morph_pipeline(['не было', 'отрицает', 'нет', 'не употребляет'])
        parser = Parser(HAB_RULE)
        hab_lst = []
        for match in parser.findall(text_hab):
            hab_lst.append((match.span, [_.value for _ in match.tokens]))
        if hab_lst:
            dict_symp['вредные привычки'] = 0
        else:
            dict_symp['вредные привычки'] = 1

    SMOKE_RULE = or_(rule(not_(normalized('не')),normalized('курит')),
                     rule(not_(normalized('не')),normalized('употребляет')))
    parser = Parser(SMOKE_RULE)
    hab_lst = []
    for match in parser.findall(text):
        hab_lst.append((match.span, [_.value for _ in match.tokens]))
    if hab_lst:
        dict_symp['вредные привычки'] = 1
    
    # Rules for work
    work_lst = []
    WORK_RULE = morph_pipeline(['работает'])
    parser = Parser(WORK_RULE)
    for match in parser.findall(text):
        work_lst.append((match.span, [_.value for _ in match.tokens]))
    if work_lst:
        dict_symp['соц категория'] = 0

    WORK_RULE = rule(not_(normalized('не')),normalized('работает'))
    parser = Parser(WORK_RULE)
    work_lst = []
    for match in parser.findall(text):
        work_lst.append((match.span, [_.value for _ in match.tokens]))
    if work_lst:
        dict_symp['соц категория'] = 1
    
    # If patient has условия труда probably he has a job
    if dict_symp['условия труда'] is not None:
        dict_symp['соц категория'] = 1
            
    # Rule for fish
    FISH_RULE = morph_pipeline(['рыба'])
    parser = Parser(FISH_RULE)
    fish_lst = []
    for match in parser.findall(text):
        fish_lst.append((match.span, [_.value for _ in match.tokens]))
    if fish_lst:
        dict_symp['речная рыба'] = 0
        text_fish = text[list(match.span)[1]-40:list(match.span)[1]+40]
        FISH_RULE = morph_pipeline(['да', 'постоянно'])
        parser = Parser(FISH_RULE)
        fish_lst = []
        for match in parser.findall(text_fish):
            fish_lst.append((match.span, [_.value for _ in match.tokens]))
        if fish_lst:
            dict_symp['речная рыба'] = 1
        FISH_RULE = rule(not_(normalized('не')),normalized('употребляет'))
        parser = Parser(FISH_RULE)
        fish_lst = []
        for match in parser.findall(text_fish):
            fish_lst.append((match.span, [_.value for _ in match.tokens]))
        if fish_lst:
            dict_symp['речная рыба'] = 1

    # Rule for home
    home = None
    home_span = None
    home_types = [['бездомный'],
                   ['дом благоустроенный', 'частный дом'],
                   ['дом не благоустроенный','дом неблагоустроенный'],
                   ['квартира не благоустроенная', 'квартира неблагоустроенная'],
                   ['квартира благоустроенная', 'благоустроенная квартира'],]

    for i in range(len(home_types)):
        home_lst = []
        HOME_RULE = morph_pipeline(home_types[i])
        parser = Parser(HOME_RULE)
        for match in parser.findall(text):
            home_lst.append((match.span, [_.value for _ in match.tokens]))
        if home_lst:
            home = i
            home_span = match.span

    dict_symp['квартира, дом'] = home

    pets = []
    pets_span = []
    pet_types = [['кошка'],
                 ['собака'],
                 ['корова','коза']]


    # Rules for different factors
    factors = []
    factors_span = []
    factor_types = [['ссадины',"царапины", "раны", "расчесы", "уколы", "потертости", "трещины", 'вскрытие', 'поцарапал', "рассечен"],
                   ['ушибы'],
                   ['переохлаждение','перегревание','смена температуры',"охлаждение"],
                   ['инсоляция'],
                   ['лучевая терапия'],
                   ['стресс', "стрессовая ситуация"],
                   ['переутомление', 'тяжело работал']]

    def find_factors(factor_types, text=text, left=0, right=len(factor_types)):
        for i in range(len(factor_types[left:right])):
            factor_lst = []
            FACT_RULE = morph_pipeline(factor_types[i+left])
            parser = Parser(FACT_RULE)
            for match in parser.findall(text):
                factor_lst.append(' '.join([_.value for _ in match.tokens]))
                factors_span.append(match.span)
            if factor_lst:
                factors.append(i+1+left)

    find_factors(factor_types)
    detect_lst = []
    parser = Parser(morph_pipeline(['трещин - не обнаружено']))
    for match in parser.findall(text):
        detect_lst.append(' '.join([_.value for _ in match.tokens]))
    if detect_lst:
        factors.remove(1)
        
    if factors:
        dict_symp['провоцирущие факторы'] = factors
            
    factors = []
    factor_types = [['микоз',"диабет", "ожирение", "варикоз", "недостаточность", "лимфостаз", "экзема", "варикозная болезнь"],
                   ['тонзилит',"отит", "синусит", "кариес", "пародонтоз", "остеомиелит", "тромбофлебит", "трофические язвы"],
                   ['резиновая обувь','загрязнения кожных'],
                   ['соматические заболевания']]
    
    if dict_symp['др заболевания в анамнезе']:
        find_factors(factor_types, text=dict_symp['др заболевания в анамнезе'], right=2)
    find_factors(factor_types, left=2)
    if factors:
        dict_symp['предрасполагающие факторы'] = factors

    # Rule for detecting the second diagnosis
    DIAGNOZ_RULE = or_(rule(normalized('сопутствующий'), not_(or_(gram('NOUN')))),
                       rule(normalized('сопутствующий'),normalized('диагноз')),
                       rule(normalized('диагноз'),normalized('сопутствующий')),)

    parser = Parser(DIAGNOZ_RULE)
    diag_lst = []
    for match in parser.findall(text):
        diag_lst.append((match.span, [_.value for _ in match.tokens]))
    if diag_lst:
        dict_symp['сопутствующий диагноз'] = text[list(match.span)[1]+2:list(match.span)[1]+text[list(match.span)[1]:].find(' \n  \n')]
        dict_symp['кол-во сопут заболеваний'] = dict_symp['сопутствующий диагноз'].count('\n')
        if dict_symp['кол-во сопут заболеваний']==0: dict_symp['кол-во сопут заболеваний']=1

    # Rule for detecting the first diagnosis
    DIAGNOZ_RULE = or_(rule(normalized('диагноз'),normalized('при'),normalized('поступлении')),
                       rule(normalized('клинический'),normalized('диагноз')),
                       rule(normalized('диагноз'),normalized('клинический')),
                       rule(normalized('основной'),normalized('диагноз')),
                       rule(normalized('диагноз'),normalized('основной')),
                       rule(normalized('Ds')),
                       rule(normalized('Ds:')),
                       rule(not_(or_(gram('ADJF'),gram('NOUN'))),normalized('диагноз'),not_(or_(gram('ADJF'),gram('PREP')))))

    diag_lst = []
    parser = Parser(DIAGNOZ_RULE)
    for match in parser.findall(text):
        diag_lst.append((match.span, [_.value for _ in match.tokens]))
    last = list(match.span)[1]+text[list(match.span)[1]:].find(' \n  \n')
    if last == list(match.span)[1]-1:
        last = len(text)-1
    dict_symp['основной диагноз'] = text[list(match.span)[1]+1:last]
        
    return dict_symp
