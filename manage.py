from flask_script import Manager
from app import create_app
from flask_migrate import MigrateCommand

APP = create_app('TESTING')
MANAGER = Manager(APP)
MANAGER.add_command('db', MigrateCommand)

if __name__ == '__main__':
    MANAGER.run()