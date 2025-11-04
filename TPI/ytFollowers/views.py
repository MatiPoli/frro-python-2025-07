from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from ytProfile.models import Follow
from allauth.socialaccount.models import SocialAccount

def home(request):
    query = request.GET.get('q', '').strip()
    results = []
    mensaje = ''
    
    # --- 1. Obtener datos de seguidos (IDs y datos para la tabla) ---
    seguidos = []
    seguidos_ids = []
    if request.user.is_authenticated:
        seguidos_objs = Follow.objects.filter(seguidor=request.user).select_related('seguido')
        seguidos_ids = [f.seguido.id for f in seguidos_objs]
        
        for f in seguidos_objs:
            seguido_user = f.seguido
            google_account = SocialAccount.objects.filter(user=seguido_user, provider='google').first()
            seguidos.append({
                'id': seguido_user.id,
                'username': seguido_user.username,
                'google_photo': google_account.extra_data.get('picture') if google_account else None
            })

    # --- 2. Lógica de Búsqueda ---
    if query:
        results = User.objects.filter(username__icontains=query).exclude(username='admin')
        if request.user.is_authenticated:
            results = results.exclude(id=request.user.id)

    # --- 3. Lógica de Follow/Unfollow (POST) ---
    if request.method == 'POST' and request.user.is_authenticated:
        user_id_to_follow = request.POST.get('user_id')
        user_id_to_unfollow = request.POST.get('unfollow_id')

        if user_id_to_follow:
            user_to_follow = User.objects.filter(id=user_id_to_follow).first()
            if user_to_follow and user_to_follow != request.user:
                if user_to_follow.id not in seguidos_ids:
                    Follow.objects.create(seguidor=request.user, seguido=user_to_follow)
                    # Es más simple y robusto redirigir para recargar el estado
                    return redirect('ytfollowers_home')
                else:
                    mensaje = f"Ya sigues a {user_to_follow.username}."
            elif user_to_follow == request.user:
                mensaje = "No puedes seguirte a ti mismo."

        elif user_id_to_unfollow:
            user_to_unfollow = User.objects.filter(id=user_id_to_unfollow).first()
            if user_to_unfollow and user_to_unfollow.id in seguidos_ids:
                Follow.objects.filter(seguidor=request.user, seguido=user_to_unfollow).delete()
                return redirect('ytfollowers_home')

    # --- 4. Renderizar la plantilla con el contexto ---
    context = {
        'query': query, 
        'results': results, 
        'mensaje': mensaje, 
        'seguidos': seguidos,
        'seguidos_ids': seguidos_ids
    }
    return render(request, 'ytFollowers/home.html', context)
