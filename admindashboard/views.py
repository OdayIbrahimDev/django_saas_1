from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Or admin_required if you have such a decorator

# For now, basic login_required.
# Consider creating a custom decorator like @superadmin_required
# that checks request.user.is_superuser and request.user.is_staff
# and potentially if the user belongs to a specific 'Super Admin' group.
@login_required 
def dashboard_home(request):
    # Add a basic check for superuser or staff status for enhanced security
    if not request.user.is_superuser and not request.user.is_staff:
        # Or redirect to a more appropriate 'permission denied' page or login
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to access this page.")
        
    context = {
        'title': 'Super Admin Dashboard'
    }
    return render(request, 'admindashboard/dashboard_home.html', context)
