import pandas as pd
import re


def preprocess(data):
    regex = r'(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}\s?[apm]+) -\s*(.*?)(?::\s*(.*))?$'

    # Lists to store extracted data
    datetimes = []
    usernames = []
    messages = []

    # Iterate through each line of the data
    for line in data.split('\n'):
        match = re.match(regex, line.strip())
        if match:
            # Extract datetime
            datetime = match.group(1)

            # If there's a username and message (with ":")
            if match.group(3):
                username = match.group(2)
                message = match.group(3)
            else:
                # If there's no username (message contains no ":")
                username = "Group Notification"
                message = match.group(2)

            # Append extracted data to respective lists
            datetimes.append(datetime)
            usernames.append(username)
            messages.append(message)

    df=pd.DataFrame(data={"date":datetimes,"user_name":usernames,"msg":messages})

    from datetime import datetime
    def convert_to_24hr_format(date_str):
        # Clean the string by removing non-breaking spaces and stripping extra spaces
        date_str = date_str.replace('\u202f', ' ').strip()

        try:
            # Parse the date from 12-hour format to datetime object
            date_obj = datetime.strptime(date_str, "%d/%m/%Y, %I:%M %p")

            # Convert to 24-hour format
            return date_obj.strftime("%d/%m/%Y, %H:%M")
        except ValueError as e:
            # Handle invalid date format
            return None  # Return None or another default value, depending on your needs

    # Apply the conversion to the 'date' column
    df['date'] = df['date'].apply(convert_to_24hr_format)

    # Return the updated DataFrame

    df['date'] = df['date'].replace('\u202f', ' ', regex=True).str.strip()

    # Function to handle the date conversion with both 12-hour and 24-hour formats
    def convert_to_datetime(date_str):
        # Try 12-hour format first
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y, %I:%M %p")
        except ValueError:
            # If 12-hour format fails, try 24-hour format
            date_obj = datetime.strptime(date_str, "%d/%m/%Y, %H:%M")
        return date_obj

    # Convert 'date' column to datetime format with both formats handled
    df['date'] = df['date'].apply(convert_to_datetime)

    # Extract Year, Month, Day, Hour, and Minute from the 'date' column
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['only_date']=df['date'].dt.date
    df['day_name']=df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []

    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period']=period


    return df

    # Output the updated dataframe