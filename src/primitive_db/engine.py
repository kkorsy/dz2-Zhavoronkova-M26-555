import prompt


def welcome():
    print("first attempt run project\n")
    show_help()
    while True:
        cmd = prompt.string("Введите команду: ").strip()
        match cmd:
            case "help":
                show_help()
            case "exit":
                return
            case _:
                print("Неизвестная команда")

def show_help():
    print(
        "<command> exit - выйти из программы\n"
        "<command> help - справочная информация"
    )
