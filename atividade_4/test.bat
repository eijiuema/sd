start "Processo 0" py atividade4.py --id 0 --neighbours 2 4 6 8 9
start "Processo 1" py atividade4.py --id 1 --neighbours 3 5 7 9
start "Processo 2" py atividade4.py --id 2 --neighbours 0 4 6 8
start "Processo 3" py atividade4.py --id 3 --neighbours 1 5 7 9
start "Processo 4" py atividade4.py --id 4 --neighbours 0 2 6 8 5 --election
start "Processo 5" py atividade4.py --id 5 --neighbours 1 3 7 9 4
start "Processo 6" py atividade4.py --id 6 --neighbours 0 2 4 8
start "Processo 7" py atividade4.py --id 7 --neighbours 1 3 5 9
start "Processo 8" py atividade4.py --id 8 --neighbours 0 2 4 6
start "Processo 9" py atividade4.py --id 9 --neighbours 1 3 5 7 0