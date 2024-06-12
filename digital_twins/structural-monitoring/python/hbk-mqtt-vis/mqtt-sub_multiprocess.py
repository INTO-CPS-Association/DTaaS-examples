from multiprocessing import Process
from time import sleep

def task(name: str):
    sleep(20)
    print(f'complete {name} task')

def select(name):
    print(f'select function called with {name}')
    match name:
        case 'oma':
            task('oma')
        case 'sys_id':
            task('sys_id')
        case _:
            print('no matching task found')

if __name__ == '__main__':
    p = Process(target=select, args=('oma',))
    p.daemon = True
    p.start()
    #p.join()
    print("Hello from the main process")