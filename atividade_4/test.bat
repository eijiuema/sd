tskill python
start "Processo 0" py atividade4.py --n 10 --id 0 --neighbours 2 4 6 8 9 --capacity 10
start "Processo 1" py atividade4.py --n 10 --id 1 --neighbours 3 5 7 9 --election --capacity 15
start "Processo 2" py atividade4.py --n 10 --id 2 --neighbours 0 4 6 8 --capacity 12
start "Processo 3" py atividade4.py --n 10 --id 3 --neighbours 1 5 7 9 --capacity 19
start "Processo 4" py atividade4.py --n 10 --id 4 --neighbours 0 2 6 8 5 --capacity 5
start "Processo 5" py atividade4.py --n 10 --id 5 --neighbours 1 3 7 9 4 --capacity 27
start "Processo 6" py atividade4.py --n 10 --id 6 --neighbours 0 2 4 8 --capacity 21
start "Processo 7" py atividade4.py --n 10 --id 7 --neighbours 1 3 5 9 --capacity 14
start "Processo 8" py atividade4.py --n 10 --id 8 --neighbours 0 2 4 6 --election --capacity 18
start "Processo 9" py atividade4.py --n 10 --id 9 --neighbours 1 3 5 7 0 --capacity 2

