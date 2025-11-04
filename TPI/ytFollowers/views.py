from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from ytProfile.models import Follow

def home(request):
    query = request.GET.get('q', '').strip()
    results = []
    mensaje = ''
    seguidos = []
    if request.user.is_authenticated:
        from ytProfile.models import Follow
        seguidos_objs = [f.seguido for f in Follow.objects.filter(seguidor=request.user)]
        # Obtener foto de Google de cada seguido
        from allauth.socialaccount.models import SocialAccount
        seguidos = []
        for seguido in seguidos_objs:
            google_account = SocialAccount.objects.filter(user=seguido, provider='google').first()
            google_photo = None
            if google_account and 'picture' in google_account.extra_data:
                google_photo = google_account.extra_data['picture']
            seguidos.append({
                'username': seguido.username,
                'email': seguido.email,
                'id': seguido.id,
                'google_photo': google_photo,
            })

    if query:
        results_query = User.objects.filter(username__icontains=query)

        # Excluyo al 'admin'
        results_query = results_query.exclude(username='admin')

        # Si el usuario está autenticado se excluye a sí mismo
        if request.user.is_authenticated:
            results_query = results_query.exclude(id=request.user.id)

        results = results_query

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        unfollow_id = request.POST.get('unfollow_id')
        if user_id and request.user.is_authenticated:
            seguido = User.objects.filter(id=user_id).first()
            if seguido and seguido != request.user:
                existe = Follow.objects.filter(seguidor=request.user, seguido=seguido).exists()
                if not existe:
                    Follow.objects.create(seguidor=request.user, seguido=seguido)
                    mensaje = f"Ahora sigues a {seguido.username}."
                    seguidos.append(seguido)
                else:
                    mensaje = f"Ya sigues a {seguido.username}."
            else:
                mensaje = "No puedes seguirte a ti mismo."
        elif unfollow_id and request.user.is_authenticated:
            seguido = User.objects.filter(id=unfollow_id).first()
            if seguido:
                Follow.objects.filter(seguidor=request.user, seguido=seguido).delete()
                mensaje = f"Has dejado de seguir a {seguido.username}."
                seguidos = [f.seguido for f in Follow.objects.filter(seguidor=request.user)]
            else:
                mensaje = "Usuario no encontrado."
    return render(request, 'ytFollowers/home.html', {'query': query, 'results': results, 'mensaje': mensaje, 'seguidos': seguidos})
