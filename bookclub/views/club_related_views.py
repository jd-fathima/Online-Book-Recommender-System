"""Club related views."""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from bookclub.templates import *
from bookclub.forms import ApplicantForm, ApplicationForm, ScheduleMeetingForm, EditClubForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse
from django.views.generic import ListView
from bookclub.models import Meeting, User, Club, Application
from bookclub.views import club_views
from django.views.generic.edit import View, UpdateView
from django.core.paginator import Paginator


class ApplicationsView(LoginRequiredMixin, View):
    """View that handles club applications."""

    def get(self, request):
        """Display application template"""
        return self.render()

    def render(self):
        current_user = self.request.user
        """Render all applications of this user's owned clubs"""
        applicants = []

        owned_clubs = Club.objects.filter(owner=current_user)

        for a in Application.objects.all():
            if a.club in owned_clubs:
                applicants.append(a)

        paginator = Paginator(applicants, settings.APPLICATIONS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(self.request, 'applications.html', {'applicants': applicants, 'page_obj': page_obj})


class MyApplicationsView(LoginRequiredMixin, View):
    """View that handles the currently logged in user's applications (as opposed to applications of their own clubs"""

    http_method_names = ['get']

    def get(self, request):
        """Display application template"""
        return self.render()

    def render(self):
        current_user = self.request.user
        """Render all applications of this user's owned clubs"""
        clubs = []
        my_applications = []
        for c in Club.objects.all():
            if c.owner is not current_user:
                clubs.append(c)

        for a in Application.objects.all():
            if a.club in clubs and a.applicant == current_user:
                my_applications.append(a)

        paginator = Paginator(my_applications, settings.APPLICATIONS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(self.request, 'my_applications.html', {'applications': my_applications, 'page_obj': page_obj})

class ClubMemberListView(LoginRequiredMixin, ListView):
    """Gets the members of each club"""

    model = Club
    template_name = "club_members.html"
    paginate_by = settings.USERS_PER_PAGE
    pk_url_kwarg = 'club_id'
    context_object_name = 'club'
    ordering = ['-name']

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to book_list if book_id invalid."""
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('home')

    def get_queryset(self):
        return Club.objects.get(id = self.kwargs['club_id']).get_all_users()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        current_user = self.request.user
        current_user_is_owner = False
        current_club_id = self.kwargs['club_id']
        current_club = Club.objects.get(id = current_club_id)
        paginator = Paginator(current_club.get_all_users(), settings.USERS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        for each in page_obj:
            u_id = each.pk
            if current_club.user_level(each) == "Member":
                user_level = "Member"
            elif current_club.user_level(each) == "Organiser":
                user_level = "Organiser"
            else:
                user_level = "Owner"
                if each == current_user:
                    current_user_is_owner = True

        context['club'] = current_club
        context['page_obj'] = page_obj
        context['user_level'] = user_level
        context['c_pk'] = current_club_id
        context['u_pk'] = u_id
        context['is_owner'] = current_user_is_owner

        return context

class ClubMeetingsListView(LoginRequiredMixin, ListView):
    """Gets the meetings history of each club"""
    """Adapted from ClubMembersListView"""

    model = Club
    template_name = "club_meetings.html"
    paginate_by = settings.USERS_PER_PAGE
    pk_url_kwarg = 'club_id'
    context_object_name = 'club'
    ordering = ['-meeting.date']

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to clubs list if club_id invalid."""
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('home')

    def get_queryset(self):
        return Club.objects.get(id = self.kwargs['club_id']).get_meetings()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        current_club_id = self.kwargs['club_id']
        current_club = Club.objects.get(id = current_club_id)
        paginator = Paginator(current_club.get_meetings(), settings.USERS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['club'] = current_club
        context['page_obj'] = page_obj
        return context

def app_accept(request, pk):
    """Accept application"""
    app = Application.objects.all().get(pk=pk)
    app.club.make_member(app.applicant)
    app.delete()
    messages.add_message(request, messages.SUCCESS, "User accepted!")
    club_views.club_util(request)
    return redirect('applications')


def app_remove(request, pk):
    """Reject application"""
    app = Application.objects.all().get(pk=pk)
    app.delete()
    messages.add_message(request, messages.SUCCESS, "User rejected!")
    return redirect('applications')

@login_required
def new_application(request, club_id):
    """ Create A New Application """

    club_applied_to = Club.objects.get(pk=club_id)
    application_is_possible = True

    if request.method == 'POST':
        current_members = club_applied_to.get_all_users()
        if request.user in current_members:
            application_is_possible = False

        current_applications = Application.objects.filter(applicant=request.user, club=club_applied_to).count()
        if current_applications:
            application_is_possible = False

        if application_is_possible:
            Application.objects.create(
                applicant=request.user,
                club=club_applied_to
            )
            messages.add_message(request, messages.SUCCESS,
                                 f"Application to {Club.objects.get(pk=club_id).name} was successfully submitted!")

        else:
            messages.add_message(request, messages.ERROR,
                                 f"Could not apply to the following club: {Club.objects.get(pk=club_id).name}. You have "
                                 f"already applied.")


    return redirect('my_applications')

@login_required
def meetings_list(request, club_id):
    club = Club.objects.get(id=club_id)
    meetings = club.get_meetings()
    paginator = Paginator(meetings, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'club_meetings.html', {'club': club, 'page_obj': page_obj})



class MeetingScheduler(LoginRequiredMixin, View):
    """View that handles meeting scheduling."""

    http_method_names = ['get', 'post']

    def get(self, request, pk):
        """Display meeting scheduler template"""
        return self.render(pk)

    def post(self, request, pk):
        """Handle scheduling attempt."""

        current_club=Club.objects.get(pk=pk)
        form = ScheduleMeetingForm(club=current_club, data=request.POST)
        if form.is_valid():
            meeting = form.save(club=current_club)
            messages.add_message(request, messages.SUCCESS, "The meeting was scheduled!")
            return redirect('home')
        messages.add_message(request, messages.ERROR, "The meeting was unable to be scheduled!")
        return self.render(pk)

    def render(self, pk):
        """Render meeting scheduler form"""
        current_club=Club.objects.get(pk=pk)
        form = ScheduleMeetingForm(club=current_club)
        return render(self.request, 'schedule_meeting.html', {'form': form, 'pk':pk})


def promote_member_to_organiser(request, c_pk, u_pk):
    """Promote member to organiser"""
    club = Club.objects.all().get(pk = c_pk)
    new_organiser = User.objects.all().get(pk=u_pk)
    club.make_organiser(new_organiser)
    messages.add_message(request, messages.SUCCESS, "User promoted!")
    return redirect('club_members', club_id=c_pk)

def demote_organiser_to_member(request, c_pk, u_pk):
    """Demote organiser to member"""
    club = Club.objects.all().get(pk = c_pk)
    new_member = User.objects.all().get(pk=u_pk)
    club.demote_organiser(new_member)
    messages.add_message(request, messages.SUCCESS, "User demoted!")
    return redirect('club_members', club_id=c_pk)

class ClubUpdateView(LoginRequiredMixin, UpdateView):
    """View to update club profile."""

    model = EditClubForm
    template_name = "edit_club.html"
    form_class = EditClubForm

    def get_object(self, c_pk):
        """Return the object (user) to be updated."""
        club_to_edit = Club.objects.all().get(pk=c_pk)
        return club_to_edit

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Club updated!")
        return reverse('club_selector')

    def post(self, request, c_pk, *args, **kwargs):
        club_to_edit = Club.objects.all().get(pk=c_pk)
        form = self.form_class(instance=club_to_edit, data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return render(request, 'edit_club.html', {"form": form})

    def get(self, request, c_pk, *args, **kwargs):
        club_to_edit = Club.objects.all().get(pk=c_pk)
        form = self.form_class(instance=club_to_edit)
        return render(request, 'edit_club.html', {"form": form})