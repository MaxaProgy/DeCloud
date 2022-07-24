from clients_manager import DispatcherClientsManager, app

dispatcher = DispatcherClientsManager(wsgi=True)
dispatcher.start()

if __name__ == '__main__':
    app.run(port=5001)