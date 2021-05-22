from Reminder import app
from Reminder.models import TaskToDo, Users
from flask_apscheduler import APScheduler
from twilio.rest import Client
from dotenv import load_dotenv
from os.path import join, dirname
import datetime, os

scheduler = APScheduler()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Twilio variables
Sid = os.getenv('TWILIO_ACCOUNT_SID')
Api_key = os.getenv('TWILIO_API_KEY')
Number = os.getenv('TWILIO_NUMBER')

client = Client(Sid, Api_key)

def check_tasks(c, number):
    date = datetime.datetime.now()
    TasksToRemind = TaskToDo.query.filter_by(termDate=date.strftime('%Y-%m-%d'),
                                            termTime=date.strftime('%H:%M')).all()
    if len(TasksToRemind) > 0:
        for task in TasksToRemind:
            user = Users.query.filter_by(id=task.user_id).first()
            c.messages.create(to=f'{user.phone_nr}',from_=number, body=f'{task.title} - {task.description}')


                                    

if __name__ == "__main__":
    scheduler.add_job(id='check_tasks', func=check_tasks, trigger='interval', seconds=60, args=(client,Number))
    scheduler.start()
    app.run(debug=True, use_reloader=False)