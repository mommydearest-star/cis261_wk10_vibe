"""Student records manager for CIS261.

This script stores student records with exactly three test scores and computes
average and letter grade values. Student records are loaded from and saved to
student_grades.txt.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

DATA_FILE = "student_grades.txt"


@dataclass
class Student:
    student_id: str
    name: str
    test_scores: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    average: float = field(init=False)
    grade: str = field(init=False)

    def __post_init__(self) -> None:
        self.update_average_and_grade()

    def update_average_and_grade(self) -> None:
        self.average = sum(self.test_scores) / len(self.test_scores)
        if self.average >= 90:
            self.grade = "A"
        elif self.average >= 80:
            self.grade = "B"
        elif self.average >= 70:
            self.grade = "C"
        elif self.average >= 60:
            self.grade = "D"
        else:
            self.grade = "F"

    def record_summary(self) -> str:
        return (
            f"ID: {self.student_id} | Name: {self.name} | "
            f"Test1: {self.test_scores[0]:.2f}, Test2: {self.test_scores[1]:.2f}, Test3: {self.test_scores[2]:.2f} | "
            f"Average: {self.average:.2f} | Grade: {self.grade}"
        )


class StudentManager:
    def __init__(self) -> None:
        self.students: Dict[str, Student] = {}

    def add_student(self, student_id: str, name: str, scores: List[float]) -> bool:
        if student_id in self.students:
            return False
        self.students[student_id] = Student(student_id=student_id, name=name, test_scores=scores)
        return True

    def remove_student(self, student_id: str) -> bool:
        return self.students.pop(student_id, None) is not None

    def get_student(self, student_id: str) -> Optional[Student]:
        return self.students.get(student_id)

    def search_by_name(self, query: str) -> List[Student]:
        lowered = query.lower()
        return [student for student in self.students.values() if lowered in student.name.lower()]

    def load_from_file(self, filename: str) -> None:
        if not os.path.exists(filename):
            return
        try:
            with open(filename, mode="r", newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile, delimiter="|")
                for row in reader:
                    if len(row) != 7:
                        continue
                    name, student_id, score1, score2, score3, _, _ = row
                    try:
                        scores = [float(score1), float(score2), float(score3)]
                    except ValueError:
                        continue
                    self.students[student_id] = Student(student_id=student_id, name=name, test_scores=scores)
        except (OSError, csv.Error) as error:
            print(f"Unable to load records from {filename}: {error}")

    def save_to_file(self, filename: str) -> bool:
        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile, delimiter="|")
                for student in self.students.values():
                    writer.writerow([
                        student.name,
                        student.student_id,
                        f"{student.test_scores[0]:.2f}",
                        f"{student.test_scores[1]:.2f}",
                        f"{student.test_scores[2]:.2f}",
                        f"{student.average:.2f}",
                        student.grade,
                    ])
            return True
        except (OSError, csv.Error) as error:
            print(f"Unable to save records to {filename}: {error}")
            return False

    def all_records(self) -> List[Student]:
        return list(self.students.values())

    def class_statistics(self) -> Optional[Tuple[float, float, float]]:
        if not self.students:
            return None
        averages = [student.average for student in self.students.values()]
        return max(averages), min(averages), sum(averages) / len(averages)


def get_float_input(prompt: str, min_value: float = 0.0, max_value: float = 100.0) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        if value < min_value or value > max_value:
            print(f"Value must be between {min_value} and {max_value}.")
            continue
        return value


def get_nonempty_input(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty.")


def get_three_scores() -> List[float]:
    print("Enter three test scores for the student:")
    return [
        get_float_input("  Test 1 score (0-100): "),
        get_float_input("  Test 2 score (0-100): "),
        get_float_input("  Test 3 score (0-100): "),
    ]


def display_menu() -> None:
    print("\nStudent Records Manager")
    print("1. Add student with three test scores")
    print("2. Show all student records")
    print("3. Show student summary")
    print("4. Search student by name")
    print("5. Show class statistics")
    print("6. Remove student")
    print("ESC. Exit")


def add_student_flow(manager: StudentManager) -> None:
    student_id = get_nonempty_input("Enter student ID: ")
    name = get_nonempty_input("Enter student name: ")
    scores = get_three_scores()
    if manager.add_student(student_id, name, scores):
        manager.save_to_file(DATA_FILE)
        print(f"Student {name} added with ID {student_id}.")
    else:
        print(f"A student with ID {student_id} already exists.")


def show_all_records_flow(manager: StudentManager) -> None:
    students = manager.all_records()
    if not students:
        print("No student records available.")
        return
    print("\nAll student records:")
    header = f"{'ID':<10} {'Name':<20} {'Test1':>6} {'Test2':>6} {'Test3':>6} {'Avg':>6} {'Grade':>5}"
    print(header)
    print("-" * len(header))
    for student in students:
        print(
            f"{student.student_id:<10} {student.name:<20} "
            f"{student.test_scores[0]:6.2f} {student.test_scores[1]:6.2f} {student.test_scores[2]:6.2f} "
            f"{student.average:6.2f} {student.grade:>5}"
        )


def show_student_summary_flow(manager: StudentManager) -> None:
    student_id = get_nonempty_input("Enter student ID: ")
    student = manager.get_student(student_id)
    if student is None:
        print(f"No student found with ID {student_id}.")
        return
    print("\nStudent summary:")
    print(student.record_summary())


def search_student_flow(manager: StudentManager) -> None:
    query = get_nonempty_input("Enter student name to search: ")
    matches = manager.search_by_name(query)
    if not matches:
        print(f"No students found matching '{query}'.")
        return
    print(f"\nSearch results for '{query}':")
    header = f"{'ID':<10} {'Name':<20} {'Avg':>6} {'Grade':>5}"
    print(header)
    print("-" * len(header))
    for student in matches:
        print(
            f"{student.student_id:<10} {student.name:<20} "
            f"{student.average:6.2f} {student.grade:>5}"
        )


def show_class_statistics_flow(manager: StudentManager) -> None:
    stats = manager.class_statistics()
    if stats is None:
        print("No students available to compute statistics.")
        return
    highest, lowest, overall = stats
    print("\nClass statistics:")
    print(f"Highest average: {highest:.2f}")
    print(f"Lowest average:  {lowest:.2f}")
    print(f"Class average:   {overall:.2f}")


def remove_student_flow(manager: StudentManager) -> None:
    student_id = get_nonempty_input("Enter student ID to remove: ")
    if manager.remove_student(student_id):
        manager.save_to_file(DATA_FILE)
        print(f"Student {student_id} removed.")
    else:
        print(f"No student found with ID {student_id}.")


def main() -> None:
    manager = StudentManager()
    manager.load_from_file(DATA_FILE)
    while True:
        display_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_student_flow(manager)
        elif choice == "2":
            show_all_records_flow(manager)
        elif choice == "3":
            show_student_summary_flow(manager)
        elif choice == "4":
            search_student_flow(manager)
        elif choice == "5":
            show_class_statistics_flow(manager)
        elif choice == "6":
            remove_student_flow(manager)
        elif choice.upper() == "ESC" or choice == "\x1b":
            print("Goodbye!")
            break
        else:
            print("Please choose a valid option from 1 to 6, or type ESC to exit.")


if __name__ == "__main__":
    main()
