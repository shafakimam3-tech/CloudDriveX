import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.files.base import ContentFile

from .models import File
from .encryption import encrypt_file, decrypt_file


# Home Page
def home(request):
    return render(request, "home.html")


# Register
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if username and email and password:
            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            return redirect("login")

    return render(request, "register.html")


# Login
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")

    return render(request, "login.html")


# Logout
def logout_view(request):
    logout(request)
    return redirect("home")


# ✅ Dashboard (25GB STORAGE IN GB FORMAT)
@login_required
def dashboard(request):
    query = request.GET.get('q')

    files = File.objects.filter(user=request.user)

    if query:
        files = files.filter(file__icontains=query)

    # File type
    for f in files:
        name = f.file.name.lower()

        if name.endswith(('.png', '.jpg', '.jpeg')):
            f.file_type = 'image'
        elif name.endswith(('.mp4', '.avi')):
            f.file_type = 'video'
        elif name.endswith('.mp3'):
            f.file_type = 'audio'
        else:
            f.file_type = 'doc'

    # 🔥 STORAGE FIX
    total_size_mb = sum(file.file_size for file in files)

    max_storage_gb = 15
    max_storage_mb = max_storage_gb * 1024

    percent = (total_size_mb / max_storage_mb) * 100 if max_storage_mb > 0 else 0

    total_size_gb = total_size_mb / 1024

    return render(request, "dashboard.html", {
        "files": files,
        "total_size_gb": round(total_size_gb, 2),
        "max_storage": max_storage_gb,
        "percent": round(percent, 2),
        "query": query
    })
# ✅ Upload File (Encrypted)
from django.core.files.base import ContentFile

@login_required
def upload_file(request):

    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]

        file_data = uploaded_file.read()

        # 🔐 Encrypt file
        encrypted_data = encrypt_file(file_data)

        # ✅ FIX: pass name directly
        encrypted_file = ContentFile(
            encrypted_data,
            name=uploaded_file.name
        )

        size = len(encrypted_data) / (1024 * 1024)  # MB

        file_obj = File(
            user=request.user,
            file_size=size
        )

        # ✅ IMPORTANT: use .save() method
        file_obj.file.save(uploaded_file.name, encrypted_file)

        file_obj.save()

        return redirect("dashboard")

    return redirect("dashboard")


# ✅ Delete File
@login_required
def delete_file(request, file_id):
    file = File.objects.get(id=file_id)

    if file.user == request.user:
        file.file.delete()
        file.delete()

    return redirect("dashboard")


# ✅ Shared File
def shared_file(request, token):
    file = File.objects.filter(share_token=token).first()
    return render(request, "shared.html", {"file": file})


# ✅ Download + Decryption
@login_required
def download_file(request, file_id):
    file_obj = File.objects.get(id=file_id)

    if file_obj.user != request.user:
        return HttpResponse("Unauthorized", status=403)

    file_path = file_obj.file.path

    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = decrypt_file(encrypted_data)

    response = HttpResponse(decrypted_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'

    return response