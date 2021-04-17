# P13-Part'Âge

A collaborative web platform of services between people, to connect elders with youngers.

The platform is integrating a game system by implementing missions, rewards, experiences points and a shop.

Made with python Django framework.

Todo :
- Avatar creation and modification system to create a character representing the user

## Requirements

- Python 3.7
- Pip
- PostgreSQL

## Installation

Clone project then, in a terminal, place yourself in the project directory, create a virtual env and activate it.

Run the following command :
- Virtualenv
```
    pip install -r requirement.txt
```

- Pipenv
```
    pipenv install
```

Create a new database in PostgreSQL that will be the DB for the app.

Configure access to the database by modifying the DATABASES variable in partAgePlatform/settings/\__init\__.py then run the following commands to create app's tables in the DB and create a new admin user :
```
    python3 manage.py migrate
    python3 manage.py update_refs all
    python3 manage.py createsuperuser
```

## Custom commands

Most of the apps have their own custom command that can be directly called with manage.py command :

- user          =   update_refs_user
- messaging     =   update_refs_messaging
- mission       =   update_refs_mission

The main app partAgePlatform contain a special custom commands that allow to give an app name as arguments to call the corresponding custom command. Use the command as following :
```
python3 manage.py update_refs <appName>
```

Those commands can be used to apply changes in settings refs datas to DB.

## Usage

In a terminal, place yourself in the programm directory and activate the virtual env, make sure your PostgreSQL server is running then execute this command :

    python3 manage.py runserver

Open your browser and navigate to the url specified in the output.
