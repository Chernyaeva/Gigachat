import subprocess

PROCESSES = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   'целое число - запустить сервер и n клиентов, '
                   'x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif  ACTION.isnumeric():
        PROCESSES.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(int(ACTION)):
            PROCESSES.append(subprocess.Popen(f'python client.py -n test{i}', creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESSES:
            VICTIM = PROCESSES.pop()
            VICTIM.kill()