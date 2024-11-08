from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.db.models import Count
from django.db.models import Q
from django.views import View

from .forms import CommentForm,ResultForm,CBCForm
from .models import BlogModel,Patient,Test,ResultModel,CBCModel
from django import forms

#for PDF
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML


def generate_pdfresult(request, idBarcode):
    result = ResultModel.objects.filter(blog=idBarcode).exclude(test__testSingle =1 )
    pt = Patient.objects.get(idBarcode=idBarcode)
    template = get_template('core/pdfresult.html')
    html = template.render({'result': result, 'pt': pt})
    pdf = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    #response['Content-Disposition'] = f'attachment; filename="CBC{idBarcode}.pdf"'
    response['Content-Disposition'] = f'filename="CBC{idBarcode}.pdf"'
    return response

def generate_pdfcbc(request, idBarcode):
    cbc_result = CBCModel.objects.filter(idBarcode=idBarcode).last()
    pt = Patient.objects.get(idBarcode=idBarcode)
    template = get_template('core/pdfcbc.html')
    html = template.render({'cbc_result': cbc_result, 'pt': pt})
    pdf = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    #response['Content-Disposition'] = f'attachment; filename="CBC{idBarcode}.pdf"'
    response['Content-Disposition'] = f'filename="CBC{idBarcode}.pdf"'
    return response

class LoginView(auth_views.LoginView):
    template_name = 'core/form.html'    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        context['form_title'] = 'Login'
        context['form_btn'] = 'Login'
        return context
    

class RegisterView(View):
    template_name = 'core/form.html'

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form, 'form_title': 'Register', 'form_btn': 'Register', 'title': 'Register'})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        return render(request, self.template_name, {'form': form, 'form_title': 'Register', 'form_btn': 'Register', 'title': 'Register'})


class HomePageView(ListView):
    model = Patient
    template_name = 'core/index.html'
    context_object_name = 'blogs'
    ordering = ['-created_at']
    paginate_by = 10

    def get_queryset(self):
        search_query = self.request.GET.get('search')
        sorted_by = self.request.GET.get('sorted_by')

        # Start with the default queryset
        queryset = Patient.objects.all()

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(created_at__icontains=search_query) |
                Q(idBarcode__icontains=search_query) 
            )

        # Set the blog order
        ordering = ['-created_at', '-views']
        if sorted_by == 'views':
            ordering = ['-views']
        elif sorted_by == 'likes':
            queryset = queryset.annotate(likes_count=Count('likemodel')).order_by('-likes_count', '-views')

        # Apply the final ordering to the queryset
        if not sorted_by == 'likes':
            queryset = queryset.order_by(*ordering)

        return queryset


class BlogDetailView(DetailView):
    model = Patient
    template_name = 'core/blog_detail.html'
    context_object_name = 'blog'

    def get(self, request, *args, **kwargs):
        # Get the blog object
        blog = self.get_object()

        # Increment the views count by 1
        blog.views += 1
        blog.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = self.get_object().name
        context['comment_form'] = ResultForm()
        context['tests'] = Test.objects.filter(active =1)
        #context['reqtestID'] = Test.objects.filter(active =1, id__in = ResultModel.objects.filter(blog=self.object.idBarcode).values_list('test', flat=True))
        #reqtestID = ResultModel.objects.filter(blog=self.object.idBarcode).values_list('test', flat=True)
        return context


class BlogCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Patient
    template_name = 'core/form.html'
    fields = ['name', 'age', 'uage', 'sex', 'drname']
    success_message = 'The blog post was successfully posted.'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = 'Make Blog'
        context['form_name'] = 'Make Blog'
        context['form_btn'] = 'Post'
        context['with_media'] = True
        return context
    

class BlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Patient
    template_name = 'core/form.html'
    fields = ['name', 'age', 'uage','sex']
    success_message = 'The blog post was successfully updated.'

    def test_func(self):
        # Check if the authenticated user is the author of the blog
        return self.get_object().author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = 'Update Blog'
        context['form_name'] = 'Update Blog'
        context['form_btn'] = 'Update'
        context['with_media'] = True
        return context
    

class TestUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = ResultModel
    template_name = 'core/formtest.html'
    fields = ['test', 'result']
    success_message = 'The Test post was successfully updated.'

    def get_form(self, *args, **kwargs):
        form = super(TestUpdateView, self).get_form(*args, **kwargs)
        # Change the ForeignKey field (test) to a TextInput widget
        # print('-----------',self.get_object().test.apprvname)
        form.fields['test'].widget = forms.TextInput(attrs={'value': self.get_object().test}) 
        #self.fields['test'].widget.attrs['readonly'] = True
        return form
    
    def form_valid(self, form):
        # Here, you can update specific fields before saving
        resultmodel = form.save(commit=False)  # Don't save to the database yet
        # Update specific fields (e.g., setting a new status)
        resultmodel.autherresult = self.request.user.username 
        # Now save the object
        resultmodel.save()
        return super().form_valid(form)

    def get_success_url(self):
        # Access the pk of the related parent object
        parent_pk = self.object.blog.pk  # Assuming 'parent' is the related field
        #print('-----------',self.request.user)
        return reverse_lazy('blog_detail', kwargs={'pk': parent_pk})
    
    def test_func(self):
        # Check if the authenticated user is the author of the blog
        #return self.get_object().author == self.request.user
        #print( '-----------',self.get_object().test.fullname)
        return self.get_object().test
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['result'] = 'Update result'
        context['tests'] = Test.objects.all()
        return context
    


def CBCView(request, idBarcode):
    # Use get_or_create to either fetch or create the product by barcode
    if request.POST:
        cbc, created = CBCModel.objects.get_or_create(
            idBarcode=idBarcode,  # The field to check against
            WBC =request.POST['WBC'],
            GRN =request.POST['GRN'],
            LYM =request.POST['LYM'],
            MID =request.POST['MID'],
            GRN_per =request.POST['GRN_per'],
            LYM_per =request.POST['LYM_per'],
            MID_per =request.POST['MID_per'],
            RBC =request.POST['RBC'],
            HGB =request.POST['HGB'],
            HCT =request.POST['HCT'],
            MCV =request.POST['MCV'],
            MCH =request.POST['MCH'],
            MCHC =request.POST['MCHC'],
            PLT =request.POST['PLT'],
            MPV =request.POST['MPV'],
            user= request.user 
        )
        if created:
            print(f"Created new idBarcode with barcode {idBarcode}")
        else:
            print(f"Found existing idBarcode with barcode {idBarcode}")
    else:
        cbc = CBCModel.objects.filter(idBarcode=idBarcode).last()
    return render(request, "core/cbc.html" ,{'cbc': cbc})


class BlogDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Patient
    template_name = 'core/blog_delete.html'
    success_url = reverse_lazy('home')  # Redirect to the home page after deletion
    context_object_name = 'blog'
    success_message = 'The blog post was successfully deleted.'
    
    def test_func(self):
        # Check if the authenticated user is the author of the blog
        return self.get_object().author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = 'Delete Blog'
        return context
    

class TestDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = ResultModel
    template_name = 'core/test_delete.html'
    #success_url = reverse_lazy('blog_detail', kwargs={'pk': 5})  # Redirect to the home page after deletion
    context_object_name = 'blog'
    success_message = 'The Test Selected was successfully deleted.'
    
    def get_success_url(self):
        # Access the pk of the related parent object
        parent_pk = self.object.blog.pk  # Assuming 'parent' is the related field
        return reverse_lazy('blog_detail', kwargs={'pk': parent_pk})
    def test_func(self):
        # Check if the authenticated user is the author of the blog
        #return self.get_object().test == self.request.user
        return self.get_object().test

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = 'Delete Blog'
        return context
    


