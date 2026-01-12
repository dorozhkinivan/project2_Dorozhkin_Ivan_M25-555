import prompt


def welcome():
    """Запускает игровой цикл и обрабатывает команды пользователя."""
    print("DB project is running!")

    while True:
        # prompt.string автоматически повторяет запрос, если ввод пустой
        command = prompt.string("Введите команду: ")

        if command == "exit":
            break
        elif command == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            # Пока просто игнорируем неизвестные команды или можно вывести сообщение
            pass