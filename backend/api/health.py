from django.http import JsonResponse, HttpResponse
from django.db import connection

def health_check(request):
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "healthy", "database": "connected"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=503)

def root_view(request):
    return HttpResponse("Welcome to MeaningBy API. Go to /admin/ for the dashboard or /health/ for status.")
