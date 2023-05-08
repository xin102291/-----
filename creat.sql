CREATE TABLE IF NOT EXISTS Student(
ID CHAR(8) NOT NULL,
Name VARCHAR(255) NOT NULL,
stud_grade INT NOT NULL,
dept_name VARCHAR(255) NOT NULL,
total_credits INT NOT NULL,
PRIMARY KEY(ID)
);


CREATE TABLE IF NOT EXISTS Courses(
course_id CHAR(4) NOT NULL,
course_name VARCHAR(255) NOT NULL,
credits INT NOT NULL,
course_category VARCHAR(255) NOT NULL,
dept_name VARCHAR(255) NOT NULL,
grade VARCHAR(255) NOT NULL,
week_day INT NOT NULL,
start_time INT NOT NULL,
end_time INT NOT NULL,
max_students INT NOT NULL,
cur_students INT NOT NULL,
PRIMARY KEY(course_id)
);

CREATE TABLE IF NOT EXISTS follow_courses(
ID CHAR(8) NOT NULL,
course_id CHAR(4) NOT NULL,
course_name VARCHAR(255) NOT NULL,
week_day INT NOT NULL,
start_time INT NOT NULL,
end_time INT NOT NULL,
cur_students INT NOT NULL,
PRIMARY KEY(ID,course_id),
FOREIGN KEY (course_id) REFERENCES Courses(course_id),
FOREIGN KEY (ID) REFERENCES Student(ID)
);

CREATE TABLE IF NOT EXISTS Selection_courses(
ID CHAR(8) NOT NULL,
course_id CHAR(4) NOT NULL,
course_name VARCHAR(255) NOT NULL,
credits INT NOT NULL,
course_category VARCHAR(255) NOT NULL,
week_day INT NOT NULL,
start_time INT NOT NULL,
end_time INT NOT NULL,
PRIMARY KEY(ID,course_id)
);
CREATE TABLE IF NOT EXISTS `user`(
account VARCHAR(255) NOT NULL,
password CHAR(8) NOT NULL,
PRIMARY KEY(account),
FOREIGN KEY (account) REFERENCES Student(ID)
)