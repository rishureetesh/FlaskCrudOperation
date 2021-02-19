from flask import Flask, render_template, url_for, redirect, flash
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, DataRequired
from wtforms import StringField, IntegerField, SubmitField, DecimalField, SelectField
from flaskext.mysql import MySQL
from datetime import datetime
from decimal import Decimal
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'system'
app.config['MYSQL_DATABASE_DB'] = 'data'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


class getDetails(FlaskForm):
    ambassdor_id = IntegerField(validators=[InputRequired("Ambassdor Id Required"),
                                            DataRequired("Ambassdor Id Required, Must be Integer")],
                                render_kw={"placeholder": "Amb Id"})

    queue_id = IntegerField(validators=[InputRequired("Queue Id Required"),
                                        DataRequired("Queue Id Required, Must be Integer")],
                            render_kw={"placeholder": "Queue Id"})

    amount = IntegerField(validators=[InputRequired("Amount Is Required"),
                                      DataRequired("Amount Is Required, Must be Integer")],
                          render_kw={"placeholder": "Amount"})

    task_count = DecimalField(validators=[InputRequired("Task Count is Required"),
                                          DataRequired("Task Count is Required, , Must be Decimal value")],
                              render_kw={"placeholder": "Task Count"})

    state = SelectField(coerce=int, validators=[InputRequired("State ID is Required"),
                                     DataRequired("State Id is Required")],
                         render_kw={"placeholder": "State"})

    reason = StringField(validators=[InputRequired("Reason Must be Specified"),
                                     DataRequired("Reason Must be Specified")],
                         render_kw={"placeholder": "Reason"})


class addDetails(getDetails):
    submit = SubmitField("Submit")


class editDetails(getDetails):
    submit = SubmitField("Update")


@app.route("/", methods=["POST", "GET"])
def home():
    conn = mysql.connect()
    cursor = conn.cursor()
    form = addDetails()
    choices = [
        (200, 200),
        (410, 410),
        (802, 802)
    ]
    form.state.choices = choices
    now = datetime.now()
    timeStamp = str(now.strftime("%d-%m-%Y %H:%M:%S"))
    if form.validate_on_submit():
        cursor.execute("INSERT INTO queue_data (Date,Amb_id,Queue_id,State,Amount,Reason,Task_Count) VALUES(%s,%s,%s,%s,%s,%s,%s)", (
            timeStamp,
            form.ambassdor_id.data,
            form.queue_id.data,
            form.state.data,
            form.amount.data,
            form.reason.data,
            form.task_count.data
        ))
        conn.commit()
        flash("{}".format("Data Inserted"), "success")
        return redirect(url_for('home'))

    if form.errors:
        flash("{}".format(form.errors), "danger")
    return render_template("index.html", form=form)


@app.route("/showQueue")
def showQueueData():
    conn = mysql.connect()
    cursor = conn.cursor()
    data = cursor.execute("select * from queue_data")
    dataset = cursor.fetchall()
    print(data)
    forms = []
    for row in dataset:
        form = {
            "id" : row[0],
            "Date" : row[1],
            "Ambassdor_id" : row[2],
            "Queue_id" : row[3],
            "State" : row[4],
            "Amount" : row[5],
            "Reason" : row[6],
            "Task_Count" : row[7]
        }
        forms.append(form)
    return render_template("queueList.html", form=forms)


@app.route("/update/<int:id>/edit", methods=["POST", "GET"])
def updateQueueData(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    data = cursor.execute("select * from queue_data where id ={}".format(id))
    row = cursor.fetchone()
    form = editDetails()
    choices = [
        (200, 200),
        (410, 410),
        (802, 802)
    ]
    form.state.choices = choices
    dataset = {
        "id": row[0],
        "Date": row[1],
        "Ambassdor_id": row[2],
        "Queue_id": row[3],
        "State": row[4],
        "Amount": row[5],
        "Reason": row[6],
        "Task_Count": row[7]
    }
    if form.validate_on_submit():
        cursor.execute("UPDATE queue_data SET State='"+str(form.state.data)+"',Amount='"+str(form.amount.data)+"',Reason='"+str(form.reason.data)+"',Task_Count='"+str(form.task_count.data)+"' where id={}".format(id))
        conn.commit()
        flash("{}".format("Data Updated"), "success")
        return redirect(url_for('showQueueData'))
    return render_template("editQueue.html", form=form, data=dataset)


@app.route("/delete/<int:id>")
def deleteQueueData(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    data = cursor.execute("delete from queue_data where id ={}".format(id))
    conn.commit()
    return showQueueData()
