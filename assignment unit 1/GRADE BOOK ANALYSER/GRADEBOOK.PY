import csv
import statistics

def show_menu():
    print("\n===== GRADEBOOK ANALYZER =====")
    print("1. Enter student marks manually")
    print("2. Load marks from CSV file")
    print("3. Exit")
    
    choice = input("Enter your choice (1/2/3): ")
    return choice


def manual_entry():
    marks = {}
    n = int(input("How many students? "))
    for i in range(n):
        name = input(f"Enter name of student {i+1}: ")
        mark = float(input(f"Enter marks of {name}: "))
        marks[name] = mark
    return marks


def load_from_csv():
    marks = {}
    file_name = input("Enter CSV file name (with .csv extension): ")
    try:
        with open(file_name, mode='r') as file:
            reader = csv.DictReader1
            (file)
            for row in reader:
                name = row['Name']
                mark = float(row['Marks'])
                marks[name] = mark
        print(f"✅ Loaded data from {file_name} successfully!")
    except FileNotFoundError:
        print("⚠️ File not found. Please check the file name.")
    return marks


def calculate_average(marks_dict):
    return sum(marks_dict.values()) / len(marks_dict)

def calculate_median(marks_dict):
    return statistics.median(marks_dict.values())

def find_max_score(marks_dict):
    return max(marks_dict.values())

def find_min_score(marks_dict):
    return min(marks_dict.values())


def assign_grades(marks_dict):
    grades = {}
    for name, mark in marks_dict.items():
        if mark >= 90:
            grade = 'A'
        elif mark >= 80:
            grade = 'B'
        elif mark >= 70:
            grade = 'C'
        elif mark >= 60:
            grade = 'D'
        else:
            grade = 'F'
        grades[name] = grade
    return grades


def grade_distribution(grades_dict):
    distribution = {'A':0, 'B':0, 'C':0, 'D':0, 'F':0}
    for grade in grades_dict.values():
        if grade in distribution:
            distribution[grade] += 1
    return distribution



def pass_fail_lists(marks_dict):
    passed_students = [name for name, mark in marks_dict.items() if mark >= 40]
    failed_students = [name for name, mark in marks_dict.items() if mark < 40]
    return passed_students, failed_students


def display_results(marks_dict, grades_dict):
    print("\n===== FINAL RESULTS =====")
    print(f"{'Name':<15}{'Marks':<10}{'Grade':<5}")
    print("-" * 30)
    for name, mark in marks_dict.items():
        print(f"{name:<15}{mark:<10}{grades_dict[name]:<5}")


def save_to_csv(marks_dict, grades_dict):
    file_name = "final_gradebook.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Marks', 'Grade'])
        for name, mark in marks_dict.items():
            writer.writerow([name, mark, grades_dict[name]])
    print(f"📁 Results saved to {file_name}")


def main():
    print("Welcome to GradeBook Analyzer!")
    while True:
        choice = show_menu()

        if choice == '1':
            marks = manual_entry()
        elif choice == '2':
            marks = load_from_csv()
        elif choice == '3':
            print("👋 Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            continue

        if not marks:
            print("⚠️ No data available for analysis.")
            continue

        
        avg = calculate_average(marks)
        median = calculate_median(marks)
        max_score = find_max_score(marks)
        min_score = find_min_score(marks)
        grades = assign_grades(marks)
        dist = grade_distribution(grades)
        passed, failed = pass_fail_lists(marks)

        
        display_results(marks, grades)
        print("\n===== STATISTICS =====")
        print(f"Average Marks : {avg:.2f}")
        print(f"Median Marks  : {median}")
        print(f"Highest Score : {max_score}")
        print(f"Lowest Score  : {min_score}")

        print("\n===== GRADE DISTRIBUTION =====")
        for grade, count in dist.items():
            print(f"{grade}: {count} student(s)")

        print("\n===== PASS / FAIL =====")
        print(f"Passed ({len(passed)}): {', '.join(passed)}")
        print(f"Failed ({len(failed)}): {', '.join(failed)}")

        
        save = input("\nDo you want to save results to CSV? (y/n): ").lower()
        if save == 'y':
            save_to_csv(marks, grades)

        again = input("\nDo you want to analyze again? (y/n): ").lower()
        if again != 'y':
            print("✅ Thank you for using GradeBook Analyzer!")
            break


if __name__ == "__main__":
    main()
