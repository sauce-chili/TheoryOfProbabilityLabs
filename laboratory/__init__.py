from functools import partial

from laboratory.lab1.task_1 import Task1 as lab_1_Task_1
from laboratory.lab1.task_2 import Task2 as lab_1_Task_2
from laboratory.lab2.task_1 import Task1 as lab_2_Task_1
from laboratory.lab2.task_3 import Task3 as lab_2_Task_3
from laboratory.lab2.task_4 import Task4 as lab_2_Task_4
from laboratory.lab3.task_1 import Task1 as lab_3_Task_1

labs = {
    1: [
        partial(lab_1_Task_1, 1),
        partial(lab_1_Task_2, 2)
    ],
    2: [
        partial(lab_2_Task_1, 1),
        partial(lab_2_Task_3, 3),
        partial(lab_2_Task_4, 4),
    ],
    3: [
        partial(lab_3_Task_1, 1)
    ]
}

lab_names = {
    1: "ЭЛЕМЕНТЫ КОМБИНАТОРИКИ.КЛАССИЧЕСКОЕ ОПРЕДЕЛЕНИЕ ВЕРОЯТНОСТИ.",
    2: "ТЕОРЕМЫ СЛОЖЕНИЯ И УМНОЖЕНИЯ ВЕРОЯТНОСТЕЙ. ФОРМУЛЫ ПОЛНОЙ ВЕРОЯТНОСТИ И БАЙЕСА.",
    3: "ФОРМУЛА БЕРНУЛЛИ. ПОЛИНОМИАЛЬНАЯ ФОРМУЛА. ПРЕДЕЛЬНЫЕ ТЕОРЕМЫ В СХЕМЕ БЕРНУЛЛИ."
}
