import os, json, re
from datetime import datetime
import pandas as pd

def extract_date_times(string):
        # Define the regex pattern for date and time in HH:MM DD/MM/YYYY format
    datetime_pattern = r'\b\d{2}:\d{2} \d{2}/\d{2}/\d{4}\b'
    datetimes = re.findall(datetime_pattern, string)
    # Convert the extracted datetime strings to datetime objects
    converted_datetimes = [datetime.strptime(dt, '%H:%M %d/%m/%Y') for dt in datetimes]
    return converted_datetimes

def extract_numbers(string):
    # Use regex to find all occurrences of integers or floating-point numbers in the string
    numbers = re.findall(r'\d+\.\d+|\d+', string)
    # Convert the list of strings to a list of integers and floats
    converted_numbers = [float(num) if '.' in num else int(num) for num in numbers]
    return converted_numbers

def concat_data():
    final_data = dict()

    urls = []
    titles = []
    news_codes = []
    post_dates = []
    districts = []
    prices = []
    squares = []
    bedrooms = []
    bathrooms = []


    dataset_path = './dataset/data'
    data_paths = []
    for folder in os.listdir(dataset_path):
        file_path = dataset_path + '/' + folder
        data_paths.append(file_path)

    for data_path in data_paths:
        with open(data_path, 'r', encoding='utf8') as json_file:
            pages = json.load(json_file)
        for page in pages.values():
            
            urls.append(page[0])
            titles.append(page[1])
            districts.append(page[2])
        
            

            estate_data = page[-1]
            # Khỏi tạo giá trị mặc định
            price = None
            square = None
            bedroom = None
            bathroom = None

            # Kiểm tra các thông tin có hợp lệ vì có thể thiếu hoặc dư thông tin
            for data in estate_data:
                unit = data.split(' ')[-1]
                if unit == 'tỷ':
                    price = extract_numbers(data)[0]
                elif unit == 'm2':
                    square = extract_numbers(data)[0]
                elif unit == 'PN':
                    bedroom = extract_numbers(data)[0]
                elif unit == 'WC':
                    bathroom = extract_numbers(data)[0]
                    
            squares.append(square)
            prices.append(price)
            bedrooms.append(bedroom)
            bathrooms.append(bathroom)

            # Lấy thông tin mã tin và ngày đăng
            post_data = page[-2]
            news_codes.append(extract_numbers(post_data[0]))
            post_dates.append(extract_date_times(post_data[1]))

            final_data['url'] = urls
            final_data['title'] = titles
            
            final_data['news_code'] = news_codes
            final_data['post_date'] = post_dates
                    
            final_data['district'] = districts
            
            final_data['price'] = prices
            final_data['square'] = squares
            final_data['bedroom'] = bedrooms
            final_data['bathroom'] = bathrooms

        return final_data

def export_csv(data):
    final_csv = pd.DataFrame(data)
    final_csv.reset_index(drop=True, inplace=True)
    final_csv.to_csv("final_data.csv")
        

if __name__ == '__main__':
    data = concat_data()
    export_csv(data)
    print('Done!')
    


