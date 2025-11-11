
print("====================================")
print("   Welcome to Daily Calorie Tracker  ")
print("====================================")
print("This tool helps you record your meals, calculate total and average calories,")
print("and compare them with your daily calorie limit.\n")


meals = []
calories = []

num_meals = int(input("How many meals did you have today? "))

for i in range(num_meals):
    print(f"\nMeal {i+1}:")
    meal_name = input("Enter meal name: ")
    cal_amount = float(input("Enter calories for this meal: "))
    meals.append(meal_name)
    calories.append(cal_amount)

total_calories = sum(calories)
average_calories = total_calories / len(calories)
daily_limit = float(input("\nEnter your daily calorie limit: "))


if total_calories > daily_limit:
    status_message = "⚠️ You exceeded your calorie limit!"
else:
    status_message = "✅ You are within your calorie limit."



print("\n========== Daily Calorie Summary ==========\n")
print("Meal Name\tCalories")
print("-------------------------------------------")

for i in range(len(meals)):
    print(f"{meals[i]:<15}\t{calories[i]}")

print("-------------------------------------------")
print(f"Total:\t\t{total_calories}")
print(f"Average:\t{average_calories:.2f}")
print(status_message)



from datetime import datetime

save_option = input("\nDo you want to save this report to a file? (yes/no): ").strip().lower()

if save_option == "yes":
    with open("calorie_log.txt", "w") as file:
        file.write("===== Daily Calorie Tracker Report =====\n")
        file.write(f"Date & Time: {datetime.now()}\n\n")
        file.write("Meal Name\tCalories\n")
        file.write("-------------------------------------------\n")
        for i in range(len(meals)):
            file.write(f"{meals[i]:<15}\t{calories[i]}\n")
        file.write("-------------------------------------------\n")
        file.write(f"Total:\t\t{total_calories}\n")
        file.write(f"Average:\t{average_calories:.2f}\n")
        file.write(f"Status:\t\t{status_message}\n")
    print("✅ Report saved successfully as 'calorie_log.txt'")
else:
    print("Report not saved. Thank you for using Daily Calorie Tracker!")


