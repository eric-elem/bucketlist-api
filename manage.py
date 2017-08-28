from flask_script import Manager
from app import create_app, db
from flask_migrate import MigrateCommand

APP = create_app('DEVELOPMENT')
MANAGER = Manager(APP)
MANAGER.add_command('db', MigrateCommand)

@manager.command
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

if __name__ == '__main__':
    MANAGER.run()
