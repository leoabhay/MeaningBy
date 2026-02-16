import requests
from .forms import *
from .models import *
from .serializers import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

def supermain(request):
    try:
        # Direct model calls instead of internal API calls to avoid deadlocks
        ApiWordsList = WordSerializer(WordModel.objects.all(), many=True).data
        ApiPostsList = PostSerializer(PostModel.objects.all(), many=True).data
        ApiPostCatesList = PostCategorySerializer(PostCategoryModel.objects.all(), many=True).data
        ApiFootersList = FooterSerializer(FooterModel.objects.all(), many=True).data
        ApiHeadersList = HeaderSerializer(HeaderModel.objects.all(), many=True).data
        ApiPagesList = PageSerializer(PageModel.objects.all(), many=True).data
        ApiBlogsList = BlogSerializer(BlogModel.objects.all(), many=True).data
        ApiFeaturesList = FeatureSerializer(FeatureModel.objects.all(), many=True).data

        # Staff and superuser count from Django model
        staff_count = User.objects.filter(is_staff=True).count()
        superuser_count = User.objects.filter(is_superuser=True).count()

        # Prepare context
        context = {
            "ApiWordsList": ApiWordsList,
            "ApiPostsList": ApiPostsList,
            "ApiPostCatesList": ApiPostCatesList,
            "ApiFootersList": ApiFootersList,
            "ApiHeadersList": ApiHeadersList,
            "ApiPagesList": ApiPagesList,
            "ApiBlogsList": ApiBlogsList,
            "ApiFeaturesList": ApiFeaturesList,
            "StaffCount": staff_count,
            "SuperuserCount": superuser_count,
        }

        # Render the template with the context
        return render(request, "admin/dashboard.html", context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Dashboard Error: {str(e)} <br> <pre>{traceback.format_exc()}</pre>", status=500)


@csrf_exempt
def auth_register(request):
    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if len(password) < 8:
            messages.error(request, "Password should be at least 8 characters long")
            return redirect("auth_register")

        if password != confirm_password:
            messages.error(request, "Password Do not match")
            return redirect("auth_register")

        if User.objects.filter(username=username).exists():
            messages.error(request, f"{username} already Exists")
            return redirect("auth_register")

        if User.objects.filter(email=email).exists():
            messages.error(request, f"{email} already Exists")
            return redirect("auth_register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_staff = True
        user.save()
        messages.success(
            request, f"Admin Account created successfully! You can now log in."
        )
        return redirect("auth_login")

    return render(request, "admin/auth/register.html")


@csrf_exempt
def auth_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_superuser:
                login(request, user)
                messages.success(request, f"Login Successfully Welcome, {username}!")
                return redirect("supermain")
            elif user.is_staff:
                login(request, user)
                messages.success(request, f"Login Successfully Welcome, {username}!")
                return redirect("supermain")
        else:
            messages.error(request, f"Invalid username and Password.")
    return render(request, "admin/auth/login.html")


def auth_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("auth_login")

# User CRUD Operation
def userListApi(request):
    ApiUsersList = UserSerializer(User.objects.all(), many=True).data

    # userform = User(request.POST or None)
    if request.method == "POST" and "user_submit" in request.POST:

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if username and email and password:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username, email=email, password=password
                )
                messages.success(request, "User added successfully!")
                return redirect("apiuser")
            messages.error(request, "User already exists!")
        else:
            messages.error(request, "All fields are required.")

    context = {
        "ApiUsersList": ApiUsersList,
    }
    return render(request, "admin/user.html", context)


def userDelApi(request, id):
    users = get_object_or_404(User, id=id)
    users.delete()
    messages.warning(request, "User Deleted Successfully")
    return redirect("apiuser")


def userUpdateApi(request, id):
    users = get_object_or_404(User, id=id)
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        status = request.POST.get("status")

        if username and email:
            if not User.objects.filter(username=username).exclude(id=id).exists():
                users.username = username
                users.email = email
                
                # Update Status
                if status == "superuser":
                    users.is_superuser = True
                    users.is_staff = True
                elif status == "staff":
                    users.is_superuser = False
                    users.is_staff = True
                else: # user
                    users.is_superuser = False
                    users.is_staff = False
                
                users.save()
                messages.success(request, "User updated successfully!")
                return redirect("apiuser")
            messages.error(request, "Username already exists.")
        else:
            messages.error(request, "All fields are required.")
    return render(request, "admin/user.html", {"users": users})


# WORD CRUD OPERATION
def adminWordListApi(request):
    ApiWordsList = WordSerializer(WordModel.objects.all(), many=True).data
    wordform = WordForm(request.POST or None)

    if (
        request.method == "POST"
        and "word_submit" in request.POST
        and wordform.is_valid()
    ):
        wordform.save()
        messages.success(request, "Word added successfully!")
        return redirect("apiword")
    context = {
        "ApiWordsList": ApiWordsList,
        "wordform": wordform,
    }  # user this for data flow
    return render(request, "admin/admin.html", context)


def adminWordDelApi(request, id):
    word = get_object_or_404(WordModel, id=id)
    word.delete()
    messages.warning(request, "Deleted Successfully")
    return redirect("apiword")


def adminWordUpdateApi(request, id):
    word = get_object_or_404(WordModel, id=id)
    wordform = WordForm(request.POST or None, instance=word)
    if request.method == "POST" and wordform.is_valid():
        wordform.save()
        messages.success(request, "Word updated successfully!")
        return redirect("apiword")

    context = {
        "wordform": wordform,
        "word": word,
    }

    return render(request, "admin/admin.html", context)


# POST CRUD OPERATION
def adminPostListApi(request):
    ApiPostsList = PostSerializer(PostModel.objects.all(), many=True).data
    ApiPostCatList = PostCategorySerializer(PostCategoryModel.objects.all(), many=True).data
    postform = PostForm(request.POST, request.FILES or None)
    # postcateform = PostCatForm(request.POST or None)

    if (
        request.method == "POST"
        and "post_submit" in request.POST
        and postform.is_valid()
    ):
        postform.save()
        messages.success(request, "Post added successfully!")
        return redirect("apipost")
    context = {
        "ApiPostCatList": ApiPostCatList,
        "ApiPostsList": ApiPostsList,
        "postform": postform,
    }  # user this for data flow
    return render(request, "admin/post.html", context)


def adminPostDelApi(request, id):
    post = get_object_or_404(PostModel, id=id)
    post.delete()
    messages.warning(request, "Deleted Successfully")
    return redirect("apipost")


def adminPostUpdateApi(request, id):
    post_instance = get_object_or_404(PostModel, id=id)
    if request.method == "POST":
        pform = PostForm(request.POST, request.FILES, instance=post_instance)
        if pform.is_valid():
            pform.save()
            messages.success(request, "Post updated successfully!")
            return redirect("apipost")
    else:
        pform = PostForm(instance=post_instance)

    return render(
        request, "admin/post.html", {"postform": pform, "post_instance": post_instance}
    )


# POST CATEGORY OPERATION
def adminPostCateListApi(request):
    ApiPostCatList = PostCategorySerializer(PostCategoryModel.objects.all(), many=True).data
    postcateform = PostCatForm(request.POST or None)

    if (
        request.method == "POST"
        and "postCat_submit" in request.POST
        and postcateform.is_valid()
    ):
        postcateform.save()
        messages.success(request, "Post Category added Successfully!")
        return redirect("apipostcat")
    context = {"ApiPostCatList": ApiPostCatList, "postcateform": postcateform}
    return render(request, "admin/postcategory.html", context)


def adminPostCateDelApi(request, id):
    postcate = get_object_or_404(PostCategoryModel, id=id)
    postcate.delete()
    messages.warning(request, "Deleted Successfully")
    return redirect("apipostcat")


def adminPostCateUpdateApi(request, id):
    postcate = get_object_or_404(PostCategoryModel, id=id)
    if request.method == "POST":
        postcateform = PostCatForm(request.POST, instance=postcate)
        if postcateform.is_valid():
            postcateform.save()
            messages.success(request, "Post Category Update Successfully!")
            return redirect("apipostcat")
    else:
        postcateform = PostCatForm(instance=postcate)

    return render(
        request,
        "admin/postcategory.html",
        {"postcateform": postcateform, "postcate": postcate},
    )


# FOOTER CRUD OPERATION
def adminFooterListApi(request):
    ApiFooterList = FooterSerializer(FooterModel.objects.all(), many=True).data
    footerform = FooterForm(request.POST, request.FILES or None)

    if (
        request.method == "POST"
        and "footer_submit" in request.POST
        and footerform.is_valid()
    ):
        footerform.save()
        messages.success(request, "Footer added successfully!")
        return redirect("apifooter")
    context = {
        "ApiFooterList": ApiFooterList,
        "footerform": footerform,
    }  # user this for data flow
    return render(request, "admin/footer.html", context)


def adminFooterDelApi(request, id):
    footer = get_object_or_404(FooterModel, id=id)
    footer.delete()
    messages.warning(request, "Deleted Successfully")
    return redirect("apifooter")


def adminFooterUpdateApi(request, id):
    footer = get_object_or_404(FooterModel, id=id)
    if request.method == "POST":
        footer_form = FooterForm(request.POST, request.FILES, instance=footer)
        if footer_form.is_valid():
            footer_form.save()
            messages.success(request, "Footer updated successfully!")
            return redirect("apifooter")
    else:
        footer_form = FooterForm(instance=footer)

    return render(
        request, "admin/footer.html", {"footerform": footer_form, "footer": footer}
    )


# Header CRUD OPERATION
def adminHeaderListApi(request):
    ApiHeaderList = HeaderSerializer(HeaderModel.objects.all(), many=True).data
    headerform = HeaderForm(request.POST, request.FILES or None)

    if (
        request.method == "POST"
        and "header_submit" in request.POST
        and headerform.is_valid()
    ):
        headerform.save()
        messages.success(request, "Header added successfully!")
        return redirect("apiheader")
    context = {
        "ApiHeaderList": ApiHeaderList,
        "headerform": headerform,
    }  # user this for data flow
    return render(request, "admin/header.html", context)


def adminHeaderDelApi(request, id):
    header = get_object_or_404(HeaderModel, id=id)
    header.delete()
    messages.warning(request, "Deleted Successfully")
    return redirect("apiheader")


def adminHeaderUpdateApi(request, id):
    header = get_object_or_404(HeaderModel, id=id)
    if request.method == "POST":
        head_form = HeaderForm(request.POST, request.FILES, instance=header)
        if head_form.is_valid():
            head_form.save()
            messages.success(request, "Header updated successfully!")
            return redirect("apiheader")
        else:
            messages.error(request, "Error updating header. Please check the form.")
    else:
        head_form = HeaderForm(instance=header)

    return render(
        request, "admin/header.html", {"headerform": head_form, "header": header}
    )


# Page CRUD OPERATION
def adminPageListApi(request):
    ApiPageList = PageSerializer(PageModel.objects.all(), many=True).data
    pageform = PageForm(request.POST or None)

    if (
        request.method == "POST"
        and "page_submit" in request.POST
        and pageform.is_valid()
    ):
        pageform.save()
        messages.success(request, "Page added Successfully!")
        return redirect("apipage")
    context = {"ApiPageList": ApiPageList, "pageform": pageform}

    return render(request, "admin/page.html", context)


def adminPageDelApi(request, id):
    page = get_object_or_404(PageModel, id=id)
    page.delete()
    messages.warning(request, "Deleted Successfully")
    return redirect("apipage")


def adminPageUpdateApi(request, id):
    page = get_object_or_404(PageModel, id=id)
    if request.method == "POST":
        page_form = PageForm(request.POST, instance=page)
        if page_form.is_valid():
            page_form.save()
            messages.success(request, "Page Updated Sucessfully!")
            return redirect("apipage")
        else:
            messages.error(request, "Error updating page. Please check the form.")
    else:
        page_form = PageForm(instance=page)

    return render(request, "admin/page.html", {"pageform": page_form, "page": page})


# Blog CRUD OPERATION
def adminBlogListApi(request):
    ApiBlogList = BlogSerializer(BlogModel.objects.all(), many=True).data
    ApiPostCatList = PostCategorySerializer(PostCategoryModel.objects.all(), many=True).data
    blogform = BlogForm(request.POST, request.FILES or None)

    if (
        request.method == "POST"
        and "blog_submit" in request.POST
        and blogform.is_valid()
    ):
        blogform.save()
        messages.success(request, "Blog added Successfully!")
        return redirect("apiblog")
    context = {"ApiBlogList": ApiBlogList, "ApiPostCatList": ApiPostCatList, "blogform": blogform}

    return render(request, "admin/blog.html", context)


def adminBlogDelApi(request, id):
    blog = get_object_or_404(BlogModel, id=id)
    blog.delete()
    messages.warning(request, "Deleted Successfully")
    return redirect("apiblog")


def adminBlogUpdateApi(request, id):
    blog = get_object_or_404(BlogModel, id=id)
    if request.method == "POST":
        blog_form = BlogForm(request.POST, instance=blog)
        if blog_form.is_valid():
            blog_form.save()
            messages.success(request, "Blog Updated Sucessfully!")
            return redirect("apiblog")
        else:
            messages.error(request, "Error updating blog. Please check the form.")
    else:
        blog_form = BlogForm(instance=blog)

    return render(request, "admin/blog.html", {"blogform": blog_form, "blog": blog})


# Feature CRUD OPERATION
def adminFeatureListApi(request):
    ApiFeatureList = FeatureSerializer(FeatureModel.objects.all(), many=True).data
    featureform = FeatureForm(request.POST, request.FILES or None)

    if (
        request.method == "POST"
        and "feature_submit" in request.POST
        and featureform.is_valid()
    ):
        featureform.save()
        messages.success(request, "Feature added Successfully!")
        return redirect("apifeature")
    context = {"ApiFeatureList": ApiFeatureList, "featureform": featureform}

    return render(request, "admin/feature.html", context)


def adminFeatureDelApi(request, id):
    feature = get_object_or_404(FeatureModel, id=id)
    feature.delete()
    messages.warning(request, "Deleted Successfully")
    return redirect("apifeature")


def adminFeatureUpdateApi(request, id):
    feature = get_object_or_404(FeatureModel, id=id)
    if request.method == "POST":
        feature_form = FeatureForm(request.POST, request.FILES, instance=feature)
        if feature_form.is_valid():
            feature_form.save()
            messages.success(request, "Feature Updated Sucessfully!")
            return redirect("apifeature")
        else:
            messages.error(request, "Error updating feature. Please check the form.")
    else:
        feature_form = FeatureForm(instance=feature)

    return render(
        request, "admin/feature.html", {"featureform": feature_form, "feature": feature}
    )
