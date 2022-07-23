#from clients_manager import DispatcherClientsManager, app
from aa import app
if __name__ == '__main__':
    app.run()
    #dispatcher = DispatcherClientsManager(wsgi=True)
    #dispatcher.start()
    #dispatcher.join()