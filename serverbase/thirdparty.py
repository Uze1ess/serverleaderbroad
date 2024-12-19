import os
import json
import requests
import pandas as pd

def get_first_mark4(username, password):
    login_url = "https://sinhvien1.tlu.edu.vn/education/oauth/token"
    api_url = "https://sinhvien1.tlu.edu.vn/education/api/studentsummarymark/getbystudent"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # Lấy access token
    session = requests.Session()
    login_data = {
        'client_id': 'education_client',
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_secret': 'password',
    }

    try:
        response = session.post(login_url, headers=headers, data=login_data, verify=False)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get('access_token')
        if not access_token:
            return {"message": "Failed to retrieve access token."}
    except Exception as e:
        return {"message": f"Error during login: {e}"}

    # Lấy mark4
    try:
        api_headers = {"Authorization": f"Bearer {access_token}"}
        response = session.get(api_url, headers=api_headers, verify=False)
        response.raise_for_status()
        marks_data = response.json()

        def find_first_mark4(data):
            if isinstance(data, dict):
                if "mark4" in data:
                    return data["mark4"]
                for value in data.values():
                    result = find_first_mark4(value)
                    if result is not None:
                        return result
            elif isinstance(data, list):
                for item in data:
                    result = find_first_mark4(item)
                    if result is not None:
                        return result
            return None


        student = marks_data.get('student', {})
        enrollment_class = student.get('enrollmentClass', {})
        department = enrollment_class.get('department', {})

        return {
            "GPA": find_first_mark4(marks_data),
            "Mã sinh viên": student.get('createdBy'),
            "Họ và tên": student.get('displayName'),
            "Lớp học": enrollment_class.get('classCode'),
            "Khoa": department.get('name'),
            "Năm nhập học": student.get('createDate', [None])[0],
            "Năm bắt đầu học": student.get('modifyDate', [None])[0],
            "Ngày sinh": student.get('birthDateString'),
            "Nơi sinh": student.get('birthPlace'),
            "Giới tính": student.get('gender'),
            "Số điện thoại": student.get('phoneNumber'),
        }
    
    except Exception as e:
        return {"message": f"Error during data fetch: {e}"}

def calculate_ranking_scores(df):
    # Hàm để tính điểm xếp hạng
    def calculate_score(row):
        if row['Điểm project'] == "NULL":
            return float(row['Điểm danh']) * 0.5 + float(row['Phát biểu']) * 0.1
        else:
            return float(row['Điểm danh']) * 0.5 + float(row['Điểm project']) * 0.5 + float(row['Phát biểu']) * 0.1

    # Áp dụng hàm tính điểm cho mỗi hàng
    df['Điểm xếp hạng'] = df.apply(calculate_score, axis=1)

    # Sắp xếp lại DataFrame theo cột 'Điểm xếp hạng' từ lớn nhất đến thấp nhất
    df_sorted = df.sort_values(by='Điểm xếp hạng', ascending=False).reset_index(drop=True)

    return df_sorted

def get_students_info(df):
    # Danh sách để lưu thông tin sinh viên
    students_info = []

    # Lặp qua từng hàng trong DataFrame
    for index, row in df.iterrows():
        student = {
            "Mã sinh viên": row['MSV'] if row['MSV'] is not None else "",
            "Họ": row['Họ'] if row['Họ'] is not None else "",
            "Tên": row['Tên'] if row['Tên'] is not None else "",
            "Cụm trưởng": row['Ghi chú'] == "Cụm trưởng",  # Giả sử Ghi chú có thể là "Cụm trưởng"
            "Điểm danh": str(row['Điểm danh']),
            "Phát biểu": str(row['Phát biểu']),
            "Điểm project": str(row['Điểm project']) if row['Điểm project'] != "NULL" else "0"  # Nếu NULL thì đổi thành 0
        }
        students_info.append(student)
    
    return json.dumps(students_info, ensure_ascii=False)

def get_leader_marks(df):
        # Danh sách để lưu thông tin sinh viên
    students_info = []

    # Lặp qua từng hàng trong DataFrame
    for index, row in df.iterrows():
        student = {
            "Mã sinh viên": row['MSV'] if row['MSV'] is not None else "",
            "Họ": row['Họ'] if row['Họ'] is not None else "",
            "Tên": row['Tên'] if row['Tên'] is not None else "",
            "Điểm xếp hạng": row['Điểm xếp hạng'],
        }
        students_info.append(student)
    
    return json.dumps(students_info, ensure_ascii=False)

def get_total_student_study(df):
    # Lấy các cột từ cột thứ 6 đến cột thứ n-4
    study_columns = df.columns[5:-4]

    # Khởi tạo từ điển để lưu kết quả
    result = {}

    # Lặp qua từng cột ngày học
    for column in study_columns:
        # Đếm số học sinh có giá trị 'x' hoặc 'pb'
        total_students = df[column].isin(['x', 'pb']).sum()
        
        # Thêm vào kết quả
        result[column] = {
            "tổng học sinh đi học": int(total_students)
        }
    
    return json.dumps(result, ensure_ascii=False)

def get_attendance_ratio(row):
    # Lấy các giá trị từ cột thứ 6 đến cột thứ n-4
    study_columns = row[5:-4]  # Từ cột thứ 6 đến cột trừ 4 cột cuối cùng

    # Đếm số lượng cột có giá trị 'x' hoặc 'pb'
    total_attendance_columns = sum(1 for value in study_columns if value in ['x', 'pb'])

    # Đếm số lượng cột có giá trị 'v'
    total_v_columns = sum(1 for value in study_columns if value == 'v')

    # Tính tỷ lệ
    if total_attendance_columns > 0:
        ratio = total_v_columns / total_attendance_columns
    else:
        ratio = 0  # Tránh chia cho 0

    return ratio