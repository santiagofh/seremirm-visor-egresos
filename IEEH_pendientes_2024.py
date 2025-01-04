#%%
import pandas as pd
from datetime import datetime, timedelta

# Load the dataset
data = pd.read_csv('ieeh_2024.csv')

# Define the current date
current_date = datetime(2025, 1, 3)

# Identify the monthly columns in the dataset
monthly_columns = [col for col in data.columns if '-' in col]

# Function to calculate the 10th business day of a given month
def calculate_10th_business_day(year, month):
    """
    Calculate the 10th business day of a given month.
    """
    first_day = datetime(year, month, 1)
    business_days = []
    for day in range(1, 20):  # Look at the first 20 days of the month
        current_day = first_day + timedelta(days=day - 1)
        if current_day.weekday() < 5:  # Weekdays only (Monday to Friday)
            business_days.append(current_day)
        if len(business_days) == 10:
            return business_days[-1]
    return None

# Function to determine if the month should be marked as "Pending"
def should_mark_pending(current_date, column_date):
    """
    Check if a column is past the reporting deadline.
    """
    # Calculate the second month after the column's month
    year, month = column_date.year, column_date.month
    next_month = (month % 12) + 1
    next_year = year + (month // 12)
    second_month = (next_month % 12) + 1
    second_year = next_year + (next_month // 12)

    # Calculate the 10th business day of the second month after column_date
    deadline = calculate_10th_business_day(second_year, second_month)

    # Compare the current date with the deadline
    if deadline and current_date > deadline:
        return True
    return False

# Apply the logic to each monthly column
for col in monthly_columns:
    col_date = datetime.strptime(col, "%Y-%m")
    data[col] = data[col].apply(
        lambda x: 'Pendiente' if pd.isna(x) and should_mark_pending(current_date, col_date) else x
    )

# Save the updated DataFrame to a new CSV file
output_file_path = 'ieeh_pendiente_2024.csv'
data.to_csv(output_file_path, index=False)

print(f"Archivo actualizado guardado en: {output_file_path}")

# %%
