from flask import Flask, render_template,request,flash,redirect,url_for
import mysql.connector as myconn
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
app = Flask(__name__, static_folder="static", static_url_path="/")
# config = configparser.ConfigParser()    # 注意大小寫
app.secret_key = os.urandom(20)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message = '請先登入'


dbConn = myconn.connect(
    host = 'localhost',
    user = 'hj',
    password = 'test1234',
    database = 'testdb'
)
my_cursor = dbConn.cursor(buffered=True)
my_cursor.execute("select id from `student`;")
users=my_cursor.fetchall()
users=[i[0] for i in users]

id=""

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(student):
    if student not in users:
        return

    user = User()
    user.id = student
    return user

@login_manager.request_loader
def request_loader(request):
    student = request.form.get('user_id')
    if student not in users:
        return

    user = User()
    user.id = student
    my_cursor.execute(f"select name from `student` where id='{student}';")
    password = my_cursor.fetchone()
    user.is_authenticated = request.form['password'] == password[0]

    return user

@app.route("/")
@app.route('/login', methods=['GET', 'POST'])
def login():
    global id
    if request.method == 'GET':
        return render_template("login.html")
    
    student = request.form['user_id']

    my_cursor.execute(f"select name from `student` where id='{student}';")
    password = my_cursor.fetchone()
    if (student in users) and (request.form['password'] == password[0]):
        user = User()
        user.id = student
        login_user(user)
        flash(f'{student}！歡迎加入草泥馬訓練家的行列！')
        id = user.id
        return render_template("homepage.html",nn=id)

    flash('登入失敗了...')
    return render_template('login.html')

@app.route('/logout')
def logout():
    student = current_user.get_id()
    logout_user()
    flash(f'{student}！歡迎下次再來！')
    return render_template('login.html')


@app.route("/homepage")
@login_required
def homepage():
    return render_template("homepage.html")




@app.route("/personal")
@login_required
def per_information():
    global id
    column, row = 14,8
    course = [[" " for i in range(row)] for i in range(column)]
    for i in range(1,15):
        course[i-1][0]=i
    my_cursor.execute(f'select * from `selection_courses` where id={id}')
    cour=my_cursor.fetchall()
    for i in cour:
        c=0
        n=i[6]-1
        while c!=i[3]:
            course[n][i[5]]=i[2]
            n+=1
            c+=1

    my_cursor.execute(f'select * from `student` where id={id}')
    result = my_cursor.fetchall()

    my_cursor.execute(f'select sum(credits) from `selection_courses` where id={id}')
    sum=my_cursor.fetchall()
    

    return render_template("per_information.html",per=result[0],credits=sum[0][0],course=course)

@app.route("/add_drop", methods=['GET', 'POST'])
@login_required
def add_drop():
    global id
    p=10
    if request.method == 'GET':
        return render_template("add_drop.html",p=p)
    column, row = 14,8
    course = [[" " for i in range(row)] for i in range(column)]
    for i in range(1,15):
        course[i-1][0]=i
    my_cursor.execute(f'select * from `selection_courses` where id={id}')
    cour=my_cursor.fetchall()
    for i in cour:
        c=0
        n=i[6]-1
        while c!=i[3]:
            course[n][i[5]]=i[2]
            n+=1
            c+=1
    course_id = request.form['course_id']
    play=request.form['play']
    my_cursor.execute(f'select course_id,course_name,credits,course_category,week_day,start_time,end_time,max_students,cur_students	 from `courses` where course_id={course_id}')
    result = my_cursor.fetchall()
    my_cursor.execute(f'select sum(credits) from `selection_courses` where id={id}')
    sum=my_cursor.fetchall()
    if result == []:
        p=0 #查無資料
        return render_template("add_drop.html",p=p)
    else:
        max_students=result[0][7]
        cur_students=result[0][8]
        credits=result[0][2]
        if play == '1':
            my_cursor.execute(f'select * from `selection_courses` where course_id={course_id} and id={id}')
            sele=my_cursor.fetchall()
            if sele != []:
                p=1 #已存在課表中
                return render_template("add_drop.html",p=p)
            if int(sum[0][0])+credits >25:
                p=2 #超過25學分，無法加選
                return render_template("add_drop.html",p=p)
            if cur_students==max_students:
                    p=3 #人數已滿
                    return render_template("add_drop.html",p=p)
            
            for i in range(result[0][5],result[0][6]+1):
                if course[i-1][result[0][4]] != " ":
                    p=4 #撞課
                    return render_template("add_drop.html",p=p)


            my_cursor.execute(f"INSERT INTO selection_courses(ID,course_id,course_name,credits,course_category,week_day,start_time,end_time) VALUES ({id},{result[0][0]},'{result[0][1]}',{result[0][2]},'{result[0][3]}',{result[0][4]},{result[0][5]},{result[0][6]})")
            my_cursor.execute(f"UPDATE `courses` SET cur_students={cur_students+1} WHERE course_id={course_id};")
            dbConn.commit()
            p=5 #成功加選
            return render_template("add_drop.html",p=p)
        
        elif play == '0':
            my_cursor.execute(f"select * from `selection_courses` where course_id={course_id} and id={id}")
            drop=my_cursor.fetchall()
            
            if drop !=[]:
                if result[0][3] =="必修":
                    p=6 #必修無法退選
                    return render_template("add_drop.html",p=p)
                if int(sum[0][0])-credits<9:
                    p=7 #學分數必須大於9
                    return render_template("add_drop.html",p=p)
                p=8 #成功退選
                print(p)
                my_cursor.execute(f"DELETE FROM `selection_courses` where course_id={course_id} and id={id}")
                my_cursor.execute(f"UPDATE `courses` SET cur_students={cur_students-1} WHERE course_id={course_id};")
                dbConn.commit()
                return render_template("add_drop.html",p=p)
            
            else:
                p=9 # 已選課表無此資料
                print(p)
                return render_template("add_drop.html",p=p)
           
    return render_template("add_drop.html",p=p)
    
@app.route("/optional")
@login_required
def opt():
    global id
    column, row = 7, 11
    course = [[" " for i in range(row)] for i in range(column)]
    if course:
        my_cursor.execute(f'select * from `courses` where  course_id not in (select course_id from `selection_courses` where id={id})')
        result = my_cursor.fetchall()
    return render_template("optional.html",li=result)


if __name__ == '__main__':
    app.run()




# my_cursor.execute("select id,name from `student`;")
# result=my_cursor.fetchall()

# sql = '''insert into `user` (account,password) values(%s,%s)'''
# my_cursor.executemany(sql,result)
# dbConn.commit()