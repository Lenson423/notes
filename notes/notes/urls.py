"""notekeeper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

# from drf_yasg import openapi
# from drf_yasg.views import get_schema_view

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Your API",
#         default_version="v1",
#         description="Description of your API",
#         terms_of_service="https://www.example.com/terms/",
#         contact=openapi.Contact(email="contact@example.com"),
#         license=openapi.License(name="BSD License"),
#     ),
#     public=True,
# )

urlpatterns = [
    path('notes/', login_required(views.home), name='notes'),
    path('notes/search/', views.search_note, name='search_note'),
    path('notes/<slug:slug>/', login_required(views.get_note_details), name='note_detail'),
    path('notes/<int:pk>/delete/', login_required(views.delete_note), name='delete_single_note'),
    path('notes/<int:pk>/delete/confirm/', login_required(views.confirm_delete_note), name='confirm_delete_note'),
    path('notes/<int:pk>/edit/', login_required(views.edit_note_details), name='note_details_edit'),
    path('notes/<slug:slug>/pdf/', login_required(views.generate_pdf), name='note_as_pdf'),
    path('notes/share/<str:signed_pk>/', views.get_shareable_link, name='share_notes'),
    path('tags/<slug:slug>/', views.get_all_notes_tags, name='get_all_notes_tags'),
    path('', views.home, name='home')
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
