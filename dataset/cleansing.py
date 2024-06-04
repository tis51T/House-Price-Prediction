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
    price = page[5]
    
    if len(price) > 0:
        price_extraction = extract_numbers(price)
        try:
            price = price_extraction[0]
        except:
            price = "Thoả thuận"
    else:
        price = "Thoả thuận"

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
            house_direction = data.split(': ')[1]
        elif tag == "Hướng ban công":
            baclony_direction = data.split(': ')[1]
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

    dataset_path = './dataset/data'
    data_paths = []
    for folder in os.listdir(dataset_path):
        file_path = dataset_path + '/' + folder
        data_paths.append(file_path)

    for data_path in data_paths:
        with open(data_path, 'r', encoding='utf8') as json_file:
            pages = json.load(json_file)
            
        for page in pages.values():
            url, title, content, post_code, post_date, district, house_type, price, square, bedroom, bathroom, house_direction, baclony_direction, furniture, legal_info  = extract_data_from_page(page)
            
            urls.append(url); titles.append(title); contents.append(content); post_codes.append(post_code); post_dates.append(post_date)
            districts.append(district); types.append(house_type); prices.append(price); squares.append(square); bedrooms.append(bedroom); bathrooms.append(bathroom)
            house_directions.append(house_direction); baclony_directions.append(baclony_direction); furnitures.append(furniture); legal_infos.append(legal_info)
                        
    final_data['url'] = urls; final_data['title'] = titles; final_data['content'] = contents ;final_data['post_code'] = post_codes; final_data['post_date'] = post_dates
    final_data['district'] = districts; final_data['type'] = types; final_data['price'] = prices; final_data['square'] = squares; final_data['bedroom'] = bedrooms; final_data['bathroom'] = bathrooms
    final_data['house_direction'] = house_directions; final_data['baclony_direction'] = baclony_directions; final_data['furniture'] = furnitures; final_data['legal_info'] = legal_infos
        
    return final_data

def extract_extra_info(texts):
    house_type = []; price = []; square = []; bedrooms = []; bathrooms = []; 
    balcony = []; house_direction = []; legal_info = []; furniture = []

    for text in texts:
        text = text.lower()
        # Extracting type of house
        type_pattern = r'Loại nhà: (nhà riêng|nhà mặt phố|nhà cổ|luxury home)'
        type_match = re.search(type_pattern, text)
        house_type.append(type_match.group(1) if type_match else None)

        price_pattern = r'(\d+(\.\d+)?|\d+(\,\d+)?)(tỷ|TỶ|.x tỷ|.X TỶ| tỷ| TỶ)'
        price_match = re.search(price_pattern, text)
        if price_match:
            prices = price_match.group(1).replace(',', '.')  # Replace comma with dot
            price.append(float(prices))
        else:
            price.append(None)

        # Extracting square
        square_pattern = r'(\d+(\.\d+)?|\d+(\,\d+)?)(m2| M2| m2|M2)'
        square_match = re.search(square_pattern, text)
        if square_match:
            squares = square_match.group(1).replace(',', '.')  # Replace comma with dot
            square.append(float(squares))
        else:
            square.append(None)


        # Extracting number of bedrooms
        bedroom_pattern = r'(\d+)(PN| PN)'
        bedroom_match = re.search(bedroom_pattern, text)
        bedrooms.append(int(bedroom_match.group(1)) if bedroom_match else None)

        # Extracting number of bathrooms (wc)
        bathroom_pattern = r'(\d+)(WC| WC)'
        bathroom_match = re.search(bathroom_pattern, text)
        bathrooms.append(int(bathroom_match.group(1)) if bathroom_match else None)

        # Extracting balcony information
        balcony_pattern = r'ban công'
        balcony.append(bool(re.search(balcony_pattern, text)))

        # Extracting house direction if present
        direction_pattern = r'(Đông|Tây|Nam|Bắc|Đông Bắc|Tây Bắc|Tây Nam|Đông Nam)'
        house_direction_match = re.search(direction_pattern, text)
        house_direction.append(house_direction_match.group(1) if house_direction_match else None)

        # Extracting legal information
        legal_pattern = r'(sổ|giấy|Sổ|Giấy|pháp lý|Pháp lý|Sổ hồng|Sổ đỏ|sổ đỏ|sổ hồng)'
        legal_info.append(bool(re.search(legal_pattern, text)))

        # Extracting furniture
        furniture_pattern = r'nội thất'
        furniture.append(bool(re.search(furniture_pattern, text)))

    extra_info ={
        'type': house_type,
        'price': price,
        'square': square,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'balcony': balcony,
        'house_direction': house_direction,
        'legal_info': legal_info,
        'furniture': furniture
    }

    return extra_info

def export_csv(data):
    main_data = pd.DataFrame(data)
    main_data.reset_index(drop=True, inplace=True)

    content_copy = main_data['content'].copy()
    extra_info = extract_extra_info(content_copy)
    content_data = pd.DataFrame(extra_info)
    content_data.columns = ['c_type', 'c_price', 'c_square', 'c_bedrooms', 'c_bathrooms', 'c_balcony', 'c_house_direction', 'c_legal_info', 'c_furniture']
    

    title_copy = main_data['title'].copy()
    title_info = extract_extra_info(title_copy)
    title_data = pd.DataFrame(title_info)
    title_data.columns = ['t_type', 't_price', 't_square', 't_bedrooms', 't_bathrooms', 't_balcony', 't_house_direction', 't_legal_info', 't_furniture']

    final_data = pd.concat([main_data, content_data, title_data], axis=1)


    final_data.to_csv("./dataset/initial_data.csv", encoding='utf-8-sig', index=False)
    return



if __name__ == '__main__':
    data = concat_data()
    export_csv(data)
    print('Done!')
    


