# Welcome to QuickLock Backend!
This repository serves as the backend for our senior design project: QuickLock.

We are 3 senior students from California State University, Northridge. 

## What you need
All you need before being able to follow the guide to run the backend server is Python3 and git. Make sure it is downloaded on your system. You can check by entering one of these lines into your terminal:
```python
python -V
OR
py -V
```
```python
git -v
```
## How to run
### First, clone the repository 
* At https://github.com/albertodsandoval/quicklock-be, click on the *green* "<> Code" button. 
* Copy the Clone URL under the HTTPS tab
* Open a terminal tab at the location you want to save the project
* Run ```git clone {paste Clone URL}```
### Second, create virtual environment
I would recommend creating a virtual environment specifically for this backend server. It avoids issues by running the server with only the necessary requirements. 

To create a virtual environment:
* Open or CD into a terminal within the cloned repository
* Run ```python -m venv {env name}``` to create virtual environment
* **ON WINDOWS:** Run ```{env name}\Scripts\activate``` to activate it
* **ON MAC:** Run ```source {env name}/bin/activate``` to activate it
### Download requirements
Now we are going to use pip (comes with python) to install all the requirements.

* Make sure you are in the directory containing "requirements.txt" 
* Run ```pip install -r requirements.txt```
### Create .env
We need to create a ".env" file to fill out information specific to you.
* Navigate to the main directory
* Create a new file called ".env"
* Paste the contents of ".env.example" into your new ".env" file
* Fill out POSTGRES_USER, POSTGRES_PASSWORD and POSTGRES_HOST
  * Contact me at alberto.sandoval.domingo@gmail.com if you need this info

### Run the server!
Now all we need to do is run the server.
* CD into the "\backend" directory, you should see "manage.py" and other directories
* Run ```py manage.py runserver```

All done!! The server should now be running.