from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .controllers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Student
from .serializers import YourModelSerializer
# from .thirdparty import SERVICE_ACCOUNT_FILE, read_google_sheet, read_google_sheet_all, get_first_mark4, get_leader_marks, get_total_student_study
from .thirdparty import calculate_ranking_scores, get_first_mark4, get_students_info, get_leader_marks, get_total_student_study, get_attendance_ratio
from .apps import students_data_leaderbroad
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_exempt
import json



def home(request):
    return HttpResponse('Welcome to server')

# class YourModelListView(APIView):
#     def get(self, request):
#         data = Student.objects.all()
#         serializer = YourModelSerializer(data, many=True)
#         return Response(serializer.data)
    
# @receiver(post_save, sender=Student)
# def push_to_google_sheet(sender, instance, created, **kwargs):
#     if created:  # Chỉ cập nhật khi thêm mới
#         data = [[instance.msv, instance.name]]
#         update_google_sheet(data, range_name="Sheet1!A2")

# @csrf_exempt
# def post_student_data(request):
#     if request.method == "POST":
#         body = json.loads(request.body)
#         info_student = read_google_sheet(body['Mã sinh viên'])
#         info_student = json.loads(info_student)

#         return JsonResponse({"message": "Data processed successfully.", "data": info_student}, status=200)

@csrf_exempt
def get_students_data(request):
    if request.method == "GET":
        info_students = get_students_info(students_data_leaderbroad)
        info_students = json.loads(info_students)
        
        return JsonResponse({"message": "Data processed successfully.", "data": info_students}, status=200)
    
@csrf_exempt
def get_students_leader_marks(request):
    if request.method == "GET":
        info_students = get_leader_marks(students_data_leaderbroad)
        info_students = json.loads(info_students)
        
        return JsonResponse({"message": "Data processed successfully.", "data": info_students}, status=200)
    
@csrf_exempt
def get_marks_data(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            username = body.get('msv')
            password = body.get('password')

            if not username or not password:
                return JsonResponse({"message": "Username and password are required."}, status=400)

            marks_students_dictionary = get_first_mark4(username, password)

            if isinstance(marks_students_dictionary, dict):
                return JsonResponse({"message": "Data processed successfully.", "data": marks_students_dictionary}, status=200)
            else:
                return JsonResponse({"message": "Account not exist."}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"message": f"Error occurred: {e}"}, status=500)
    else:
        return JsonResponse({"message": "Invalid HTTP method."}, status=405)
    
@csrf_exempt
def get_student_daily(request):
    if request.method == "GET":
        student_daily = get_total_student_study(students_data_leaderbroad)
        student_daily = json.loads(student_daily)
        
        return JsonResponse({"message": "Data processed successfully.", "data": student_daily}, status=200)
    
@csrf_exempt
def post_student_data(request):
    global students_data_leaderbroad
    if request.method == "POST":
        print("Nội dung của students_data_leaderbroad:")
        print(students_data_leaderbroad)

        try:
            body = json.loads(request.body)
            username = body.get('msv')
            password = body.get('password')

            if not username or not password:
                return JsonResponse({"message": "Username and password are required."}, status=400)

            marks_students_dictionary = get_first_mark4(username, password)

            student_info_leaderboard = None

            # Duyệt qua từng hàng của DataFrame
            for _, row in students_data_leaderbroad.iterrows():
                if row["MSV"] == marks_students_dictionary["Mã sinh viên"]:
                    student_info_leaderboard = row.to_list()
                    break
            
            if student_info_leaderboard is None:
                return JsonResponse({"message": "Student not found in leaderboard."}, status=404)

            student_info = {
                "Mã sinh viên": student_info_leaderboard[0],
                "Họ và tên": marks_students_dictionary['Họ và tên'],
                "Lớp học": marks_students_dictionary['Lớp học'],
                "Khoa": marks_students_dictionary['Khoa'],
                "Năm nhập học": marks_students_dictionary["Năm nhập học"],
                "Năm bắt đầu học": marks_students_dictionary["Năm bắt đầu học"],
                "Ngày sinh": marks_students_dictionary["Ngày sinh"],
                "Nơi sinh": marks_students_dictionary["Nơi sinh"],
                "Giới tính": marks_students_dictionary['Giới tính'],
                "Số điện thoại": marks_students_dictionary["Số điện thoại"],
                "GPA": marks_students_dictionary['GPA'],
                "Tỷ lệ đi học": get_attendance_ratio(student_info_leaderboard),
                "Điểm project": student_info_leaderboard[-2],
                "Điểm danh": student_info_leaderboard[-4],
                "Phát biểu": student_info_leaderboard[-3],
                "Điểm xếp hạng": student_info_leaderboard[-1],
            }

            return JsonResponse({"message": "Data processed successfully.", "data": student_info}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"message": f"Error occurred: {e}"}, status=500)