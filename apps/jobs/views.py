"""
Job and Opportunity exploration, search, and faceted filtering views for CareerHunt.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Job, Category, Skill
from apps.companies.models import Company


class JobListView(ListView):
    """
    Search and faceted filter discovery page for opportunities.
    """
    model = Job
    template_name = "jobs/job_list.html"
    context_object_name = "jobs"
    paginate_by = 9

    def get_queryset(self):
        queryset = Job.objects.select_related("company", "source", "category").prefetch_related("job_skills__skill").active()

        # 1. Search Query (q)
        q = self.request.GET.get("q", "").strip()
        if q:
            keywords = q.split()
            query_filter = Q()
            for kw in keywords:
                query_filter &= (
                    Q(title__icontains=kw) |
                    Q(company__name__icontains=kw) |
                    Q(description__icontains=kw) |
                    Q(location_name__icontains=kw) |
                    Q(skills__name__icontains=kw)
                )
            queryset = queryset.filter(query_filter).distinct()

        # 2. Opportunity Type
        opp_type = self.request.GET.get("type", "").strip()
        if opp_type:
            queryset = queryset.filter(opportunity_type=opp_type)

        # 3. Experience Level
        exp = self.request.GET.get("exp", "").strip()
        if exp:
            queryset = queryset.filter(experience_level=exp)

        # 4. Remote Mode
        mode = self.request.GET.get("mode", "").strip()
        if mode:
            queryset = queryset.filter(remote_type=mode)

        # 5. Location
        location = self.request.GET.get("location", "").strip()
        if location:
            queryset = queryset.filter(location_name__icontains=location)

        # 6. Category
        category_slug = self.request.GET.get("category", "").strip()
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # 7. Skill
        skill_id = self.request.GET.get("skill", "").strip()
        if skill_id:
            queryset = queryset.filter(skills__id=skill_id)

        # 8. Deadline Window
        deadline = self.request.GET.get("deadline", "").strip()
        now = timezone.now()
        if deadline == "today":
            end_of_day = now + timedelta(days=1)
            queryset = queryset.filter(application_deadline__gte=now, application_deadline__lte=end_of_day)
        elif deadline == "this_week":
            end_of_week = now + timedelta(days=7)
            queryset = queryset.filter(application_deadline__gte=now, application_deadline__lte=end_of_week)
        elif deadline == "this_month":
            end_of_month = now + timedelta(days=30)
            queryset = queryset.filter(application_deadline__gte=now, application_deadline__lte=end_of_month)

        # 9. Sorting
        sort = self.request.GET.get("sort", "newest")
        if sort == "deadline_asc":
            queryset = queryset.order_by("application_deadline")
        elif sort == "title":
            queryset = queryset.order_by("title")
        else:
            queryset = queryset.order_by("-posted_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["popular_skills"] = Skill.objects.all()[:15]
        context["current_q"] = self.request.GET.get("q", "")
        context["current_type"] = self.request.GET.get("type", "")
        context["current_exp"] = self.request.GET.get("exp", "")
        context["current_mode"] = self.request.GET.get("mode", "")
        context["current_location"] = self.request.GET.get("location", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_skill"] = self.request.GET.get("skill", "")
        context["current_deadline"] = self.request.GET.get("deadline", "")
        context["current_sort"] = self.request.GET.get("sort", "newest")
        context["total_results"] = context["paginator"].count
        return context


class InternshipListView(JobListView):
    """
    Dedicated view for exploring student internships only.
    """
    def get_queryset(self):
        return super().get_queryset().filter(opportunity_type="internship")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_heading"] = "Student & Fresher Internships"
        context["page_subheading"] = "Verified internship opportunities offering real-world experience from authentic employers."
        return context


class UpcomingListView(ListView):
    """
    Dedicated view displaying opportunities with future opening dates.
    """
    model = Job
    template_name = "jobs/upcoming_list.html"
    context_object_name = "upcoming_jobs"
    paginate_by = 12

    def get_queryset(self):
        return Job.objects.select_related("company", "source", "category").prefetch_related("job_skills__skill").upcoming().order_by("application_open_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_heading"] = "Upcoming Opportunities"
        context["page_subheading"] = "Get ahead by preparing for campus and corporate programs before application windows officially open."
        return context


class JobDetailView(DetailView):
    """
    Detailed opportunity view with complete source provenance and direct application links.
    """
    model = Job
    template_name = "jobs/job_detail.html"
    context_object_name = "job"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Job.objects.select_related("company", "source", "category").prefetch_related("job_skills__skill")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Related opportunities from same company or category
        context["related_jobs"] = Job.objects.select_related("company", "source").filter(
            category=self.object.category
        ).exclude(pk=self.object.pk)[:3]
        if self.request.user.is_authenticated:
            from .models import SavedJob
            context["is_saved"] = SavedJob.objects.filter(user=self.request.user, job=self.object).exists()
        return context


class ToggleSaveJobView(ListView):
    """
    Toggles bookmarking a job for authenticated candidate.
    """
    def post(self, request, slug):
        if not request.user.is_authenticated:
            from django.contrib import messages
            messages.warning(request, "Please sign in to save opportunities.")
            from django.shortcuts import redirect
            return redirect("accounts:login")

        from django.http import JsonResponse
        from django.shortcuts import redirect
        from django.contrib import messages
        from .models import SavedJob

        job = get_object_or_404(Job, slug=slug)
        saved_obj = SavedJob.objects.filter(user=request.user, job=job).first()
        if saved_obj:
            saved_obj.delete()
            saved = False
            messages.info(request, f"Removed '{job.title}' from your saved opportunities.")
        else:
            SavedJob.objects.create(user=request.user, job=job)
            saved = True
            messages.success(request, f"Saved '{job.title}' to your profile!")

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"saved": saved, "job_id": job.id})
        
        referer = request.META.get("HTTP_REFERER")
        return redirect(referer or "jobs:job_list")


class SavedJobListView(ListView):
    """
    Lists opportunities bookmarked by the candidate.
    """
    model = Job
    template_name = "jobs/saved_jobs.html"
    context_object_name = "saved_jobs"
    paginate_by = 12

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Job.objects.none()
        from .models import SavedJob
        return Job.objects.filter(
            saved_by_users__user=self.request.user
        ).select_related("company", "source").prefetch_related("job_skills__skill").order_by("-saved_by_users__created_at")
