from django.apps import AppConfig
import json
# from .thirdparty import read_google_sheet_leaderbroad
from .thirdparty import calculate_ranking_scores
import pandas as pd
import requests
from bs4 import BeautifulSoup

students_data_leaderbroad = None

class ServerbaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'serverbase'
    # def ready(self):
    #     global students_leaderbroad
    #     students_leaderbroad = read_google_sheet_leaderbroad()
    #     students_leaderbroad = json.loads(students_leaderbroad)

    #     students_leaderbroad = pd.DataFrame(students_leaderbroad)

    #     students_leaderbroad = students_leaderbroad.sort_values(by='Điểm xếp hạng', ascending=False).reset_index(drop=True)

    #     students_leaderbroad['Xếp hạng'] = range(1, len(students_leaderbroad) + 1)

    #     print(students_leaderbroad)
    def ready(self):
        global students_data_leaderbroad
        superset_host = 'localhost:8088'
        username = 'admin'
        password = 'admin'

        s = requests.Session()
        login_form = s.post(f"http://{superset_host}/login")

        # Lấy token bảo vệ Cross-Site Request Forgery
        soup = BeautifulSoup(login_form.text, 'html.parser')
        csrf_token = soup.find('input', {'id': 'csrf_token'})['value']
        data = {
            'username': username,
            'password': password,
            'csrf_token': csrf_token
        }

        # Đăng nhập
        s.post(f'http://{superset_host}/login/', data=data)

        dataset_id = 37 

        query_url = f'http://{superset_host}/api/v1/chart/data'
        payload = payload = {
            "custom_cache_timeout": 0,
            "datasource": {
                "id": dataset_id,
                "type": "table"
            },
            "force": True,
            "queries": [
                {
                    "columns": ['MSV' ,'Họ', 'Tên', 'Lớp', 'Ghi chú', '12/11', '15/11', '19/11', '22/11', '26/11', '29/11', '03/12', '06/12', '10/12', '13/12', 'Điểm danh', 'Phát biểu', 'Điểm project'],  # Để trống để lấy tất cả các cộtu
                    "row_limit": 10000,
                }
            ],
            "result_format": "json",
            "result_type": "full"
        }

        response = s.post(query_url, json=payload)
        if response.status_code == 200:
            # data = response.json()['result'][0]['data']
            pass
        else:
            print("Không thể lấy dữ liệu từ dataset:", response.text)

        df = pd.DataFrame(data, columns=['MSV' ,'Họ', 'Tên', 'Lớp', 'Ghi chú', '12/11', '15/11', '19/11', '22/11', '26/11', '29/11', '03/12', '06/12', '10/12', '13/12', 'Điểm danh', 'Phát biểu', 'Điểm project'])

        students_data_leaderbroad = calculate_ranking_scores(df)