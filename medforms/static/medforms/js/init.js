let by_values = [
    'Дата рождения', 'Дата осмотра', 'Дата заболевания', 'Возраст',
    'Время поступления', 'Время заболевания', 'рост', 'вес', 'IMT',
    'давление диаст', 'давление сист', 'температура поступления',
    'мах температура', 'аллергическая реакция',
]

let others = [
    'др заболевания в анамнезе',
    'предрасполагающие факторы',
    'провоцирущие факторы'
]

let by_keys = [
    'озноб', 'слабость', 'вялость', 'головная боль',
    'нарушение сна', 'нарушение аппетита', 'ломота', 'тошнота', 'нарушение сознания',
    'Судороги', 'Парестезии', 'эритема', 'с четкими границами', 'валик', 'боль', 'Гиперемия',
    'Отек', 'Лимфаденит', 'Лимфангит', 'речная рыба',
    'сопутствующий диагноз', 'основной диагноз'
]


// document.getElementById("toMark").addEventListener("div", function() {
//     for (let key in features) {
//         if (!value) {
//             if (by_keys.includes(key)) {
//                 med_text.replace(key, '<mark>${key}</mark>')
//             } else if (by_values.includes(key)) {
//                 const value = features[key]
//                 med_text.replace(value, '<mark>${value}</mark>')
//             }
//         }
//     }
// }, false);


document.getElementById("toMark").textContent(function () {
        for (let key in features) {
            if (!value) {
                if (by_keys.includes(key)) {
                    med_text.replace(key, '<mark>${key}</mark>')
                } else if (by_values.includes(key)) {
                    const value = features[key]
                    med_text.replace(value, '<mark>${value}</mark>')
                }
            }
        }
    }
)