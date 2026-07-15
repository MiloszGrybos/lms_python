import argparse
import os
from dotenv import load_dotenv
from database import DB
from readers import JSONReader
from exporters import JSONExporter, XMLExporter

load_dotenv()

def parse_arguments():
    #different flags depending on which export format we need, also flags with paths to the files
    parser = argparse.ArgumentParser(description="Dorms management app.")
    parser.add_argument('--students', type=str, required=True, help="Students file path")
    parser.add_argument('--rooms', type=str, required=True, help="Rooms file path")
    parser.add_argument('--format', type=str, required=True, choices=['json', 'xml'], help="Export format: 'json'/'xml'")
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME', 'Dorms')

    reader = JSONReader()
    rooms_data = reader.read(args.rooms)
    students_data = reader.read(args.students)

    if len(rooms_data) == 0 or len(students_data) == 0:
        print("At least one of files is empty")
        return

    #launching db with parameters from .env    
    with DB(host=db_host, user=db_user, password=db_password, database=db_name) as db:
        db.createTables()    
        
        #inserting data into tables
        db.insertRooms(rooms_data)
        db.insertStudents(students_data)
        
        if args.format == 'json':
            exporter = JSONExporter()
        else:
            exporter = XMLExporter()
            
        result_count = db.roomsStudentCount()
        exporter.export(result_count, f"roomCount.{args.format}")

        result_avg_age = db.smallestAvgAge()
        exporter.export(result_avg_age, f"smallestAvgAge.{args.format}")

        result_diff_age = db.maxAgeDiff()
        exporter.export(result_diff_age, f"maxAgeDiff.{args.format}")

        result_sex = db.differentSex()
        exporter.export(result_sex, f"differentSex.{args.format}")

if __name__ == '__main__':
    main()