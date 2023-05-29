
# TASK 1
print('------------------------ TASK 1 -----------------------')
words = ['разработка', 'сокет', 'декоратор']
for word in words:
     print(type(word), word)
uwords = ['%u0440%u0430%u0437%u0440%u0430%u0431%u043E%u0442%u043A%u0430'
          , '%u0441%u043E%u043A%u0435%u0442'
          , '%u0434%u0435%u043A%u043E%u0440%u0430%u0442%u043E%u0440']
for uword in uwords:
     print(type(uword), uword)


# TASK 2
print('------------------------ TASK 2 -----------------------')
mybytes = [b'class', b'function', b'method']
for mybyte in mybytes:
     print(type(mybyte), len(mybyte), mybyte)


# TASK 3
print('------------------------ TASK 3 -----------------------')
print('«класс» и «функция» нельзя записать в байтовом формате,') 
print('так как они содержат симовлы кириллического алфавита, ')
print('неподдерживаемые стандартом ASCII')


# TASK 4
print('------------------------ TASK 4 -----------------------')
mystrings = ['разработка', 'администрирование', 'protocol', 'standard']
for mystring in mystrings:
     mybyte = mystring.encode('utf-8')
     print(mybyte)
     print(mybyte.decode('utf-8'))


# TASK 5
print('------------------------ TASK 5 -----------------------')
import subprocess

args1 = ['ping', 'yandex.ru', '-c 2']
args2 = ['ping', 'youtube.com', '-c 2']
subproc_ping = subprocess.Popen(args1, stdout=subprocess.PIPE)
for line in subproc_ping.stdout:
    print(line)
    print(line.decode('utf-8'))
subproc_ping = subprocess.Popen(args2, stdout=subprocess.PIPE)
for line in subproc_ping.stdout:
    print(line)
    print(line.decode('utf-8'))

# TASK 6
print('------------------------ TASK 6 -----------------------')
with open('test_file.txt', 'r', encoding='utf-8') as f_n:
     for el_str in f_n:
             print(el_str)