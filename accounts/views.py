from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@login_required
@user_passes_test(is_admin)
def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('file_list')
    else:
        form = CustomUserCreationForm()  #
    return render(request, 'accounts/register.html', {'form': form})


from django.shortcuts import render

# Create your views here.
