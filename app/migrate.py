""" APIs main module """

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from views import APP, DB

MIGRATE = Migrate(APP, DB)
MANAGER = Manager(APP)
MANAGER.add_command('db', MigrateCommand)

if __name__ == '__main__':
    MANAGER.run()
