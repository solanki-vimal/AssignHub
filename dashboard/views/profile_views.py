from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from academic.models import Batch, Department
from ..forms import UserProfileForm

@login_required
def profile_view(request):
    user = request.user
    
    profile_form = UserProfileForm(instance=user)
    
    if request.method == 'POST':
        # Check if it's a profile update or password update
        if 'first_name' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('dashboard:profile')
            else:
                messages.error(request, "Please correct the errors below.")
        
        # Handle password change (separate form-like logic)
        elif 'current_password' in request.POST:
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
                    update_session_auth_hash(request, user)
                    messages.success(request, "Password updated successfully.")
                    return redirect('dashboard:profile')
        
    batches = Batch.objects.filter(is_archived=False).order_by('name')

    # Self-healing: sync User.batch (and semester) if missing but M2M has data
    if user.role == 'student' and not user.batch:
        first_enrolled = user.enrolled_batches.first()
        if first_enrolled:
            user.batch = first_enrolled.name
            if first_enrolled.semester and not user.semester:
                user.semester = first_enrolled.semester
            user.save(update_fields=['batch', 'semester'])
    
    if user.role == 'student':
        layout_name = 'layouts/base_student.html'
    elif user.role == 'faculty':
        layout_name = 'layouts/base_faculty.html'
    else:
        layout_name = 'layouts/base_admin.html'
    
    # Fetch related files
    user_files = []
    if user.role == 'student':
        from assignments.models import SubmissionFile
        user_files = SubmissionFile.objects.filter(submission__student=user).select_related('submission__assignment').order_by('-uploaded_at')[:10]
    elif user.role == 'faculty':
        from assignments.models import AssignmentAttachment
        user_files = AssignmentAttachment.objects.filter(assignment__created_by=user).select_related('assignment').order_by('-uploaded_at')[:10]

    context = {
        'profile_form': profile_form,
        'departments': Department.objects.all(),
        'batches': batches,
        'user_files': user_files,
        'layout_name': layout_name,
    }
    return render(request, 'dashboard/profile.html', context)
