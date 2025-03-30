import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.http import JsonResponse
from .models import PointData
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.core import signing
from django.contrib.auth import login


def generate_token(user_email):
    signer = signing.TimestampSigner()
    return signer.sign(user_email)


def home(request):
    return render(request, 'landing_page/index.html')


def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=email, password=password)

        if user is not None:
            auth.login(request, user)

            # Generate and set token in cookie (valid for 5 mins)
            signer = signing.TimestampSigner()
            token = signer.sign(user.email)

            response = redirect('your_home_view')  # Redirect after login
            response.set_cookie('login_token', token, max_age=300)  # 300 seconds = 5 mins
            return response
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')

    return render(request, 'login.html')


def signup(request):
    if request.method == "POST":
        full_name = request.POST['full_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if not any(c.isdigit() for c in password) or not any(c.isupper() for c in password) or not any(
                c.islower() for c in password) or len(password) < 8:
            messages.error(request,
                           "Password must include at least 8 characters, one uppercase, one lowercase, and one number.")
            return redirect('signup')

        user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name,
                                        is_active=False)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        confirmation_link = request.build_absolute_uri(reverse('activate_account', args=[uid, token]))

        email_html = render_to_string('email_templates/confirmation_email.html',
                                      {'full_name': full_name, 'confirmation_link': confirmation_link})
        email_text = strip_tags(email_html)

        email_subject = "Welcome to My Map - Confirm Your Email"
        email_sender = "lvlal2alvl@gmail.com"

        email_message = EmailMultiAlternatives(email_subject, email_text, email_sender, [email])
        email_message.attach_alternative(email_html, "text/html")
        email_message.send()

        messages.success(request, "Check your inbox to confirm your registration.")
        return redirect('login')

    return render(request, "signup/signup.html")


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been activated! You can log in now.")
            return redirect('login')
        else:
            messages.error(request, "Invalid activation link!")
            return redirect('signup')

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid activation link!")
        return redirect('signup')


def map_view(request):
    vehicle_ids = PointData.objects.values_list("vehicle_id", flat=True).distinct()
    return render(request, "map/map.html", {"veh_ids": list(vehicle_ids)})


def scene_view(request):
    vehicle_ids = PointData.objects.values_list("vehicle_id", flat=True).distinct()
    return render(request, "map/scene.html", {"veh_ids": list(vehicle_ids)})


def trips(request):
    vehicle_id = request.GET.get("uid")

    if not vehicle_id:
        return JsonResponse({"error": "Vehicle ID is required"}, status=400)

    try:
        vehicle_id = int(vehicle_id)
    except ValueError:
        return JsonResponse({"error": "Invalid vehicle ID format"}, status=400)

    trip_ids = PointData.objects.filter(vehicle_id=vehicle_id).values_list('trip_id', flat=True).distinct()

    return JsonResponse({"trips": list(trip_ids)}, safe=False)


def geojson_vid(request):
    try:
        veh_id = request.GET.get("vehicle_id")
        trip_id = request.GET.get("trip")  # ← get the trip ID if provided

        if not veh_id:
            return JsonResponse({"error": "Please select a vehicle_id."}, status=400)

        try:
            veh_id = int(veh_id)
        except ValueError:
            return JsonResponse({"error": "Invalid vehicle id format."}, status=400)

        # Start with filtering by vehicle_id
        query = PointData.objects.filter(vehicle_id=veh_id)

        # If trip ID is provided, filter by it too
        if trip_id:
            try:
                trip_id = int(trip_id)
                query = query.filter(trip_id=trip_id)
            except ValueError:
                return JsonResponse({"error": "Invalid trip id format."}, status=400)

        if not query.exists():
            return JsonResponse({"error": "No data found for this vehicle and trip."}, status=404)

        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [record.x, record.y]
                    },
                    "properties": {
                        "gid": record.gid,
                        "direction": record.direction,
                        "velocity": record.velocity,
                        "dt": record.dt,
                        "status": record.status,
                        "vehicle_id": record.vehicle_id,
                        "vehicle_class": record.vehicle_class,
                        "zone_id": record.zone_id,
                        "fid": record.fid,
                        "ts_insert": record.ts_insert
                    }
                }
                for record in query
            ]
        }

        return JsonResponse(geojson_data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



def user_login(request):
    """ Handles user login and email verification. """
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, "Please sign up.")
            return redirect('login')

        user_auth = authenticate(request, username=user.username, password=password)
        if user_auth is None:
            messages.error(request, "Incorrect password.")
            return redirect('login')

        if not user.is_active:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = request.build_absolute_uri(reverse('activate_account', args=[uid, token]))

            email_html = render_to_string('email_templates/confirmation_email.html',
                                          {'full_name': user.first_name, 'confirmation_link': activation_link})
            email_text = strip_tags(email_html)

            email_subject = "Activate Your Account - My Map"
            email_sender = "lvlal2alvl@gmail.com"

            email_message = EmailMultiAlternatives(email_subject, email_text, email_sender, [email])
            email_message.attach_alternative(email_html, "text/html")
            email_message.send()

            messages.warning(request, "Please verify your email.")
            return redirect('login')

        login(request, user_auth)
        return redirect('map')

    return render(request, "login/login.html")


def scene(request):
    """ Renders a placeholder scene page. """
    return render(request, "MAP/scene.html")


def logout_view(request):
    auth.logout(request)
    response = redirect('login')
    response.delete_cookie('login_token')
    return response