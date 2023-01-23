"""litreview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
import bookreview.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login', bookreview.views.LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('signup', bookreview.views.SignupView.as_view(), name='signup'),
    path('', bookreview.views.FluxView.as_view(), name='flux'),
    path('follow', bookreview.views.FollowView.as_view(), name='follow'),
    path('unfollow/<int:pk>', bookreview.views.UnFollowView.as_view(), name='unfollow'),
    path('ticket/create', bookreview.views.TicketCreateView.as_view(), name='ticket_create'),
    path('ticket/update/<int:pk>', bookreview.views.TicketUpdateView.as_view(), name='ticket_update'),
    path('ticket/review/<int:pk>', bookreview.views.ReviewExistingTicketCreate.as_view(), name='review_ticket'),
    path('ticket/review/create', bookreview.views.TicketAndReviewCreate.as_view(), name='ticket_and_review_create'),
    path('review/update/<int:pk>', bookreview.views.ReviewUpdate.as_view(), name='review_update'),
    path('posts', bookreview.views.PostsView.as_view(), name='posts'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
