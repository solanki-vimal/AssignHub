from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academic.models import Batch
from academic.constants import DEPARTMENTS

@login_required
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        contact_no = request.POST.get('contact_no', '').strip()
        
        user.first_name = first_name
        user.last_name = last_name
        user.contact_no = contact_no
        
        if user.role == 'student':
            user.enrollment_no = request.POST.get('enrollment_no', '').strip()
            batch_name = request.POST.get('batch', '').strip()
            if batch_name:
                batch_obj = Batch.objects.filter(name__iexact=batch_name).first()
                if batch_obj:
                    user.batch = batch_obj.name
                    batch_obj.students.add(user)
                    
        elif user.role == 'faculty':
            user.faculty_id = request.POST.get('faculty_id', '').strip()
            user.department = request.POST.get('department', '').strip()
            
        user.save()
        
        # Handle password change
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if current_password and new_password and confirm_password:
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            elif not user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, "Password updated successfully.")
                
        messages.success(request, "Profile updated successfully.")
        return redirect('dashboard:profile')
        
    batches = Batch.objects.filter(is_archived=False).order_by('name')
    
    if user.role == 'student':
        layout_name = 'layouts/base_student.html'
    elif user.role == 'faculty':
        layout_name = 'layouts/base_faculty.html'
    else:
        layout_name = 'layouts/base_admin.html'
    
    context = {
        'departments': DEPARTMENTS,
        'batches': batches,
        'layout_name': layout_name,
    }
    return render(request, 'dashboard/profile.html', context)
