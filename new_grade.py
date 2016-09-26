#/usr/bin/env python

import sqlite3 as lite
import sys
import os 

def create_db(tbl_name):
    '''
    Creates a new data base file if it does not exist and a new table
    '''
    con = lite.connect(sql_file)
    cur = con.cursor()
    try: 
       cur.execute("""CREATE TABLE {tn}
                       (ID INT PRIMARY KEY, 
                       LastName TEXT,
                       FirstName Text,
                       GID INT)""".format(tn=tbl_name))
    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

def import_from_roster(roster_file,tbl_name):
    '''
    Imports names of students from the roster file
    '''
    names =[]
    with open(roster_file,"r") as inf:
        for i,line in enumerate(inf):
            ln = line.split(",")[0]
            fn = line.split(",")[1]
            names.append((i+1,ln,fn,0))

    con = lite.connect(sql_file)
    try: 
        cur= con.cursor()
        cur.executemany('INSERT INTO {tn} '
                        'VALUES(?, ?, ?, ?)'.format(tn=tbl_name),names)
        con.commit()

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)
        con.rollback()

def last_assigned_gid(tbl_name):
    '''
    Returns the last assigned groud ID
    '''
    con = lite.connect(sql_file)
    cur = con.cursor()
    try:
        cur.execute("SELECT max(GID) from {tn}".format(tn=tbl_name))
        rows = cur.fetchone()
    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)
    max_id = rows[0]
    return max_id


# Implement: Check if student has already been assigned a group and confirm
# before reassigning a new group 
def group_students(tbl_name):
    '''
    Group students 
    '''
    print "You are here to group students"
    max_id = last_assigned_gid(tbl_name)
    print "Last group number that was assigned was {0}".format(max_id)
    new_gid = max_id + 1
    group_loop = True
    while group_loop:
        name_input = raw_input('Type a partial string to search for a '
                               'student to add to group {0}:  '.format(new_gid))
        con = lite.connect(sql_file)
        cur = con.cursor()
        try:
            cur.execute('SELECT * from {tn} WHERE '
                        'LastName LIKE ? or '
                        'FirstName LIKE ?'.format(tn=tbl_name),
                        (name_input+'%', name_input+'%'))
            rows = cur.fetchall()
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)

        if len(rows) == 0:
            print "No record found"

        elif len(rows) == 1:
            print "Only one record found"
            print rows[0][0],rows[0][1],rows[0][2]
            usr_input = raw_input('Shall I assign {0} {1} to group {2}: '
                                  'Y or N ? '.format(rows[0][2],
                                                     rows[0][1],
                                                     new_gid))
            if usr_input == 'y' or usr_input == 'Y':
                try:
                    cur.execute('UPDATE {tn} '
                                'SET GID={gid} '
                                'WHERE id={sid}'.format(tn=tbl_name, 
                                                       gid=new_gid,
                                                       sid=rows[0][0]))
                    con.commit()
                except lite.Error, e:
                    print "Error %s:" % e.args[0]
                    sys.exit(1)

        elif len(rows) > 1:
            print "Found multiple students with the search string:"
            for row in rows:
                print row[0],row[1],row[2]
            id_input = raw_input('Choose the correct ID that you '
                                 'want to assign to the group:  ')
            try:
                cur.execute('UPDATE {tn} '
                            'SET GID={gid} '
                            'WHERE id={sid}'.format(tn=tbl_name, 
                                                   gid=new_gid, 
                                                   sid=id_input))
                con.commit()
            except lite.Error, e:
                print "Error %s:" % e.args[0]
                sys.exit(1)


        grp_loop_input = raw_input('Do you want to add another student '
                                   'to group {0}: Y or N ?  '.format(new_gid))
        if grp_loop_input == 'y' or grp_loop_input == 'Y' :
            group_loop = True
        else:
            group_loop = False

def group_add(tbl_name, g_id, s_id):
    '''
    Add a grade to the entire group, but check if the student is still in the
    same group while submitting this homework
    '''
    con = lite.connect(sql_file)
    cur = con.cursor()
    print "\n Group members are "
    cur.execute('SELECT * from {tn} '
                'WHERE GID={gid}'.format(tn=tbl_name,
                                         gid=g_id))
    rows_grp = cur.fetchall()
    for row_gp in rows_grp:
        print row_gp[0],row_gp[1],row_gp[2],row_gp[3]
    
    upd_pref=raw_input('Check whether group has changed. Now,'
                       'Do you want to update score for \n'
                       '1.JUST the student or \n'
                       '2.ENTIRE group?  ')
    score_input = raw_input("Enter grade:  ")
    if int(upd_pref) == 1:
        try:
            cur.execute('UPDATE {tn} '
                        'SET {cn}={grade} '
                        'WHERE ID={sid}'.format(tn=tbl_name,
                                                cn=quiz_input,
                                                grade=score_input,
                                                sid=s_id))
            con.commit()
        except lite.Error, e:
            con.rollback()
            print "Error %s:" % e.args[0]
            sys.exit(1)
            
    elif int(upd_pref) == 2:
        try:
            cur.execute('UPDATE {tn} '
                        'SET {cn}={grade} '
                        'WHERE GID={gid}'.format(tn=tbl_name, 
                                                 cn=quiz_input, 
                                                 grade=score_input, 
                                                 gid=g_id))
            con.commit()
        except lite.Error, e:
            con.rollback()
            print "Error %s:" % e.args[0]
            sys.exit(1)
            
# Implement: If a student already has a grade, confirm before replacing.  
def add_grade(tbl_name, group_choice):
    print "Adding scores to {0}".format(quiz_input)
    grade_loop = True
    while grade_loop:
        name_input = raw_input("Type a partial string to search for a student:  ")
        con = lite.connect(sql_file)
        cur = con.cursor()
        try:
            cur.execute('SELECT * from {tn} '
                        'WHERE LastName LIKE ? or '
                        'FirstName LIKE ?'.format(tn=tbl_name),
                        (name_input+'%',name_input+'%'))
            rows = cur.fetchall()
        except lite.Error, e:
            print "Error here %s:" % e.args[0]
            sys.exit(1)

        if len(rows) == 0:
            print "No record found"
        
        elif len(rows) == 1:
            print "One record found" 
            print rows[0][0],rows[0][1],rows[0][2]
            if group_choice == 1:
                group_add(tbl_name, g_id=rows[0][3], s_id=rows[0][0])
            elif group_choice == 2:
                score_input = raw_input("Enter grade:  ")
                try:
                    cur.execute('UPDATE {tn} '
                                'SET {cn}={grade} '
                                'WHERE ID={sid}'.format(tn=tbl_name,
                                                        cn=quiz_input,
                                                        grade=score_input,
                                                        sid=rows[0][0]))
                    con.commit()
                except lite.Error, e:
                    con.rollback()
                    print "Error %s:" % e.args[0]
                    sys.exit(1)

        elif len(rows) > 1:
            print "Multiple records with the search key found: "
            for row in rows:
                print row[0],row[1],row[2],row[3]

            id_input = raw_input("Choose the correct ID of the student:  ")
            if group_choice == 1:
                cur.execute('SELECT GID from {tn} '
                            'WHERE ID = {sid}'.format(tn=tbl_name, 
                                                      sid=id_input))
                grp = cur.fetchall()
                g_id = grp[0][0]
                group_add(tbl_name, g_id=g_id, sid=id_input)

            elif group_choice == 2:
                score_input = raw_input("Enter grade:  ")
                try:
                    cur.execute('UPDATE {tn} '
                                'SET {cn}={grade} '
                                'WHERE ID={sid}'.format(tn=tbl_name,
                                                        cn=quiz_input,
                                                        grade=score_input,
                                                        sid=rows[0][0]))
                    con.commit()
                except lite.Error, e:
                    con.rollback()
                    print "Error %s:" % e.args[0]
                    sys.exit(1)

        grade_loop_input = raw_input('Do you want to add score for another '
                                     'student for the same quiz {0}: Y or N ? '.
                                     format(quiz_input))
        if grade_loop_input == 'y' or grade_loop_input =="Y":
            grade_loop = True
        else:
            grade_loop = False
            
def create_col(tbl_name, quiz_input):
    '''
    Creates a new column for the HW or quiz in the database
    '''
    con = lite.connect(sql_file)
    cur = con.cursor()
    columns = [i[1] for i in cur.execute('PRAGMA table_info({tn})'.
                                         format(tn=tbl_name))]
    if quiz_input not in columns:
        col_choice = raw_input('Column does not exist. Do you want to '
                               'create one ? Y or N :   ')
        if col_choice == 'y' or col_choice == 'Y':
            print "Creating a new column {0} in the database".format(quiz_input)
            try:
                cur.execute('ALTER TABLE {tn} '
                            'ADD COLUMN '
                            '{cn} INT DEFAULT 0'.format(tn=tbl_name,
                                                        cn=quiz_input))
                con.commit()
            except lite.Error, e:
                con.rollback()
                print "Error %s:" % e.args[0]
                sys.exit(1)

if __name__ == '__main__':
    sql_path = os.environ['SQL_DB_PATH']
    sql_file = '{0}/grade.db'.format(sql_path)
    choice = raw_input('1. Create new table\n'
                       '2. Student/Group management\n'
                       '3. Add grades\n'
                       '4. Import grades from a file\n'
                       '5. Export csv file: ')
    tbl_name = raw_input("Enter table name:  ")
    
    if int(choice) == 1: 
        create_db(tbl_name)

    elif int(choice) == 2:
        sub_ch = raw_input('1. Import students from a roster\n'
                           '2. Group students:   ')
        if int(sub_ch) == 1:
            roster_file = raw_input("Roster file name with extension:  ")
            import_from_roster(roster_file,tbl_name)
        elif int(sub_ch) == 2:
            loop_flag = True
            while loop_flag:
                group_students(tbl_name)
                usr_ch = raw_input('Do you want to \n'
                                   '1. Add students to other group or \n'
                                   '2. Finished adding groups:  ')
                if int(usr_ch) == 1:
                    loop_flag = True
                elif int(usr_ch) ==2 :
                    loop_flag = False

    elif int(choice) == 3:
        quiz_input = raw_input("Enter name of quiz/homework:   ")
        create_col(tbl_name, quiz_input)
        
        grade_choice = raw_input('Are you adding grades \n'
                                 '1. groupwise or \n'
                                 '2. individually ?:   ')
        add_grade(tbl_name, int(grade_choice))

    elif int(choice) == 4:
        fn = raw_input('Enter file name to import grades from:  ')
        quiz_input = raw_input("Enter name of quiz/homework:   ")
        create_col(tbl_name, quiz_input)
        con = lite.connect(sql_file)
        cur = con.cursor()
        with open(fn, 'r') as inf:
            fl = inf.readlines()
            for line in fl:
                ln = line.strip().split(',')[0]
                grade = line.strip().split(',')[2]
                try:
                    cur.execute('UPDATE {tn} '
                                'SET {cn}={gr} WHERE '
                                'LastName LIKE ?'.format(tn=tbl_name, 
                                                         cn=quiz_input,
                                                         gr=grade),
                                (ln,))
                    con.commit()
                except lite.Error, e:
                    con.rollback()
                    print "Error %s:" % e.args[0]
                    sys.exit(1)

    elif int(choice) == 5:
        print "Columns found in the table: "
        con = lite.connect(sql_file)
        cur = con.cursor()
        columns = [i[1] for i in cur.execute('PRAGMA table_info({tn})'.
                                             format(tn=tbl_name))]
        print columns[4:]
        quiz_input = raw_input("Which quiz/homework do you want to export?  ")
        fn = raw_input('Enter file name to export grades to:  ')
        nf = open('{0}.csv'.format(fn),'w')

        try:
            cur.execute('SELECT LastName, FirstName, {cn} from {tn} ' 
                        'ORDER BY LastName'.format(tn=tbl_name, 
                                                   cn=quiz_input))
            rows = cur.fetchall()
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)

        for row in rows:
            nf.write("{0},{1},{2}\n".format(row[0],row[1],row[2]))
        
