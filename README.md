# UTA-Management-System
Webapp that will allow Hunter CS Department to track clock-in and clock-out for UTAs.

## Project Setup ##
1. Set up a virtual environment for Django. Virtualenv docs: https://virtualenv.pypa.io/en/latest/installation.html
2. Clone this repository using `git clone https://github.com/Proto007/UTA-Management-System`
3. Install the libraries from requirements.txt
```
cd UTA-Management-System
pip install -r requirements.txt
```
4. Make migrations in django
```
cd uta_management_system
python manage.py makemigrations
python manage.py migrate
```
5. Run server while inside uta_management_system directory: `python manage.py runserver`
## Branch naming rules ##
In order to contribute to the main branch, you must create a feature branch and pull request. Pull requests should be approved by atleast one programmer.
Branch names should be names as follows:
1. Branches should be named with initials of the person creating the branch. 
2. The initials would be followed by a '/' and name of the branch. 
3. The name of the branch should briefly describe what the branch is for.


