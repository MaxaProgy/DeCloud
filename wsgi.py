from clients_manager import DispatcherClientsManager

if __name__ == '__main__':
    dispatcher = DispatcherClientsManager()
    dispatcher.start()
    dispatcher.join()