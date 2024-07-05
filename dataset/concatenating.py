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

def extract_data_from_page(page):
    url = page[0]
    title = page[1]
    content = page[2]
    house_type = page[3].split('Bán ')[-1]
    
    district = page[4]
    if page[5] == 'Thỏa thuận':
        price = None
    else:
        price = page[5]

    estate_data = page[-1]
    # Khỏi tạo giá trị mặc định
    square = None
    bedroom = None
    bathroom = None
    house_direction = None
    baclony_direction = None
    furniture = None
    legal_info = None

    # Kiểm tra các thông tin có hợp lệ vì có thể thiếu hoặc dư thông tin
    for data in estate_data:
        tag = data.split(':')[0]
        if tag == 'Diện tích':
            square = extract_numbers(data)[0]
        elif tag == 'Phòng ngủ':
            bedroom = extract_numbers(data)[0]
        elif tag == 'Phòng WC':
            bathroom = extract_numbers(data)[0]
        elif tag == "Hướng nhà":
            house_direction = data.split(': ')[1] if data.split(': ')[1] else None
        elif tag == "Hướng ban công":
            baclony_direction = "Yes" if data.split(': ')[1] else "No"
        elif tag == "Nội thất":
            furniture = "Yes" if data.split(': ')[1] else "No"
        elif tag == "Pháp lý":
            legal_info = "Yes" if data.split(': ')[1] else "No"
        
        # Lấy thông tin mã tin và ngày đăng
    post_data = page[-2]
    post_code = extract_numbers(post_data[0])[0]
    post_date = extract_date_times(post_data[1])

    return url, title, content, post_code, post_date, district, house_type, price, square, bedroom, bathroom, house_direction, baclony_direction, furniture, legal_info

def concat_data():
    final_data = dict()
    urls = []; titles = []; contents = []; post_codes = []; post_dates = []
    districts = []; types = []; prices = []; squares = []; bedrooms = []; bathrooms = []; 
    house_directions = []; baclony_directions = []; furnitures = []; legal_infos = []

    dataset_path = './dataset/json_data'
    data_paths = []
    for folder in os.listdir(dataset_path):
        file_path = dataset_path + '/' + folder
        data_paths.append(file_path)

    for data_path in data_paths:
        with open(data_path, 'r', encoding='utf-8-sig') as json_file:
            pages = json.load(json_file)
            
        for page in pages.values():
            url, title, content, post_code, post_date, district, house_type, price, square, bedroom, bathroom, house_direction, baclony_direction, furniture, legal_info  = extract_data_from_page(page)
            
            urls.append(url); titles.append(title); contents.append(content); post_codes.append(post_code); post_dates.append(post_date)
            districts.append(district); types.append(house_type); prices.append(price); squares.append(square); bedrooms.append(bedroom); bathrooms.append(bathroom)
            house_directions.append(house_direction); baclony_directions.append(baclony_direction); furnitures.append(furniture); legal_infos.append(legal_info)
                        
    final_data['url'] = urls; final_data['title'] = titles; final_data['content'] = contents ;final_data['post_code'] = post_codes; final_data['post_date'] = post_dates
    final_data['district'] = districts; final_data['type'] = types; final_data['price'] = prices; final_data['square'] = squares; final_data['bedroom'] = bedrooms; final_data['bathroom'] = bathrooms
    final_data['house_direction'] = house_directions; final_data['balcony'] = baclony_directions; final_data['furniture'] = furnitures; final_data['legal_info'] = legal_infos
        
    return final_data

def extract_extra_info(texts):
    hurried = []; rent = []; price = []; square = []; bedrooms = []; bathrooms = []; 
    balcony = []; house_direction = []; legal_info = []; furniture = []; floors = []; basements = []
    for text in texts:
        text = text.lower()

        is_rent = False
        check_rent = bool(re.search(r'(thuê)', text))
        if check_rent:
            check_sale = bool(re.search(r'(bán)', text))
            if not check_sale:
                is_rent = True     
        
        rent.append(is_rent)

        price_pattern = r'giá\s*(?:bán)?\s*:?\s*(\d+(\.\d+)?|\d+(\,\d+)?|\d+((tỷ|triệu|tỉ|tr| tỷ | triệu | tỉ | tr)\d+)?)(tỷ|.x tỷ| tỷ|triệu| triệu| tỉ|tỉ)'
        price_match = re.search(price_pattern, text)
        if price_match:
            price.append(price_match.group(0))  # Append the original text
        else:
            price.append(None)

        # Extracting square
        square_pattern = r'(\d+(\.\d+)?|\d+(\,\d+)?)(m2| m2|m vuông)'
        square_match = re.search(square_pattern, text)
        if square_match:
            squares = square_match.group(1).replace(',', '.')  # Replace comma with dot
            square.append(float(squares))
        else:
            square.append(None)

        # Extracting number of bedrooms
        bedroom_pattern = r'(\d+)(pn| pn)'
        bedroom_match = re.search(bedroom_pattern, text)
        bedrooms.append(int(bedroom_match.group(1)) if bedroom_match else None)

        # Extracting number of bathrooms (wc)
        bathroom_pattern = r'(\d+)(wc| wc)'
        bathroom_match = re.search(bathroom_pattern, text)
        bathrooms.append(int(bathroom_match.group(1)) if bathroom_match else None)

        # Extracting balcony information
        balcony_pattern = r'ban công'
        balcony.append(bool(re.search(balcony_pattern, text)))

        # Extracting house direction if present
        direction_pattern = r'(đông|tây|nam|bắc|đông bắc|tây bắc|tây nam|đông nam)'
        house_direction_match = re.search(direction_pattern, text)
        house_direction.append(house_direction_match.group(1) if house_direction_match else None)

        # Extracting legal information
        legal_pattern = r'(sổ|giấy|pháp lý|sổ đỏ|sổ hồng)'
        legal_info.append(bool(re.search(legal_pattern, text)))

        # Extracting furniture
        furniture_pattern = r'nội thất'
        furniture.append(bool(re.search(furniture_pattern, text)))

        # Kiểm tra có bán gấp hay không
        hurried_pattern = r'(bán gấp|bán nhanh|gấp)'
        is_hurried = bool(re.search(hurried_pattern, text))
        hurried.append(is_hurried)

        # Lấy số tầng
        floor_match = re.search(r'(\d+) (tầng|lầu)', text)
        floor = int(floor_match.group(1)) if floor_match else 0
        sub_floor_match = re.search(r'lửng', text)
        sub_floor = 1 if sub_floor_match else 0
        ground_match = re.search(r'trệt', text)
        ground = 1 if ground_match else 0
        rooftop_match =  re.search(r'(sân thượng|tầng thượng)', text)
        rooftop = 1 if rooftop_match else 0

        floor_count = floor + ground + sub_floor + rooftop        
        floors.append(floor_count)

        # Kiểm tra có hầm hay không
        basement_pattern = r'hầm'
        basements.append(bool(re.search(basement_pattern, text)))

    extra_info ={
        'rent': rent,
        'price': price,
        'square': square,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'balcony': balcony,
        'house_direction': house_direction,
        'legal_info': legal_info,
        'furniture': furniture,
        'hurried': hurried,
        'floors': floors,
        'basement': basements
    }

    return extra_info

def export_csv(data):
    post_data = pd.DataFrame(data)
    post_data.reset_index(drop=True, inplace=True)

    content_copy = post_data['content'].copy()
    content_info = extract_extra_info(content_copy)
    content_data = pd.DataFrame(content_info)
    

    title_copy = post_data['title'].copy()
    title_info = extract_extra_info(title_copy)
    title_data = pd.DataFrame(title_info)
    
    post_data.to_csv("./dataset/csv_data/post_data.csv", encoding='utf-8-sig', index=False)
    content_data.to_csv("./dataset/csv_data/content_data.csv", encoding='utf-8-sig', index=False)
    title_data.to_csv("./dataset/csv_data/title_data.csv", encoding='utf-8-sig', index=False)

    return



if __name__ == '__main__':
    data = concat_data()
    export_csv(data)
    print('Done!')
    


