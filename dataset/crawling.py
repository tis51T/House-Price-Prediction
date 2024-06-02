from bs4 import BeautifulSoup
import requests, json, time
import pandas as pd

# urls = []
# titles = []
# districts = []
# prices = []
# square = []
# bedrooms = []
# bathrooms = []
# ids = []
# dates = []




def compute_time_run(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Time taken to run the function '{func.__name__}': {end_time - start_time} seconds")
        return result
    return wrapper


def get_last_page(url) -> int:
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    pagination = soup.find('ul', class_='uk-pagination')  # tìm container chứa các trang
    pages = pagination.find_all('a')  # tìm các trang
    return int(pages[-1]['data-ci-pagination-page'])  # lấy trang cuối cùng

def crawl_information(url) -> list:
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    information = []

    # Container chứa quận huyện
    try:
        district_container = soup.find('ul', class_='uk-breadcrumb')
        li_elements = district_container.find_all('li')
        last_li = li_elements[-1] if li_elements else None
        information.append(last_li.text)
    except:
        information.append('None')

    # Container chứa thông tin giá tiền, diện tích, số phòng ngủ, số phòng tắm
    information_container = soup.find('div', class_='uk-width-medium-3-5')
    panel = information_container.find_all('div', class_='uk-panel')

    detail_info = []
    # Đưa vào vòng lặp để lấy thông tin cần thiết
    for p in panel:
    # lấy các thông tin còn lại
        params = p.find_all('div', class_='param')
        if params:  # Check if divs is not empty
            
            li_param1 = params[0].find_all('li')
            li_param2 = params[1].find_all('li') if len(params) > 1 else []

            # Nếu thông tin trống thì lưu là None
            for li in li_param1:
                detail_info.append(li.text.strip())

            for li in li_param2:
                detail_info.insert(0, li.text.strip())

    information.append(detail_info)

    return information


@compute_time_run
def crawl_data_from_page(url, file_path) -> None:
    r = requests.get(url)    
    soup = BeautifulSoup(r.content, 'html5lib')
    estate_container = soup.find('div', class_='uk-width-medium-7-10') # tìm container chứa các bài đăng
    items = estate_container.find_all('div', class_='name') # tìm các bài đăng

    pages_data = dict()
    i = 0
    for item in items:
        temp_url = item.a['href'] # url của bài đăng
        title = item.a.text
        information = crawl_information(temp_url)
        information.insert(0, title)
        information.insert(0, temp_url)

        pages_data[i] = information
        i += 1

    # Export to JSON
    
    with open(file_path, 'w', encoding='utf8') as json_file:
        json.dump(pages_data, json_file, ensure_ascii=False)

def crawl_estate(start, end):
    url = 'https://batdongsan.vn/ban-nha-ho-chi-minh'
    for i in range(start - 1, end):
        temp_url = url + f'/p{i+1}'

        file_path = f'./dataset/page{i+1}.json'
        crawl_data_from_page(temp_url, file_path)
        print(f'Page {i+1} is done!')
        print('-------------------------------------------------------------------------------------------------------')
    return
if __name__ == '__main__':
    start_page = 1
    end_page = 2
    crawl_estate(start_page, end_page)
    print('Done!')