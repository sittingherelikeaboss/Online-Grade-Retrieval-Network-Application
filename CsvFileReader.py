import csv
import hashlib

def csv_file_reader(filename):
    mark_database = []
    with open(filename, newline = '') as csvfile:
        spamreader = csv.reader(csvfile, delimiter = ',', quotechar = '|')
        for row in spamreader:
            #print(','.join(row))
            mark_database.append(row)
    return mark_database

def find_student(hash_info, mark_database):
    found = False
    for row in range(1, len(mark_database)):
        hash_info2 = hash_word(mark_database[row][0], mark_database[row][1])
        if hash_info == hash_info2:
            found = True
            break
    return found

def hash_word(input_id, input_pw):
    m = hashlib.sha256()
    m.update(input_id.encode('utf-8'))
    m.update(input_pw.encode('utf-8'))
    return m.digest()
    
def main():
    filename = 'course_grades_v01.csv'
    mark_database = csv_file_reader(filename)
    input_id = input("Student ID: ")
    input_pw = input("Student PW: ")
    hash_info = hash_word(input_id, input_pw)
    found = find_student(hash_info, mark_database)
    if found:
        print("Correct password, record found")
    else:
        print("Record not found or password failure")

if __name__ == '__main__':
    main()
