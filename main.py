from Tello import Tello

def main():
    instance = Tello()
    instance.send_commands()

if __name__ == '__main__':
    main()