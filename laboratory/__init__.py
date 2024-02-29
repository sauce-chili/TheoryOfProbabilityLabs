from functools import partial
from laboratory.lab1.task_1 import Task1 as lab_1_Task_1
from laboratory.lab1.task_2 import Task2 as lab_1_Task_2

labs = {
    1: [
        partial(lab_1_Task_1, 1),
        partial(lab_1_Task_2, 2)
    ]
}

lab_names = {
    1: "Элементы комбинаторики. Классическое определение вероятности",
}
