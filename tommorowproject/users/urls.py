from django.urls import path
from . import views
from django.conf.urls import handler404



urlpatterns = [
    path('' ,views.index, name='index'),
    #path('404/' ,views.error_page, name='error_page'),
    path("invite/<uuid:token>/", views.magic_login, name="invite"),
    path('api/invite/create/',views.CreateMagicLinkAPIView.as_view(), name='create-magic-link'),

    path('analyse-contrat/' ,views.analyse_contrat, name='analyse_contrat'),
    path('approbation-contrat/' ,views.approbation_contrat, name='approbation_contrat'),
    path('contract-archiving/' ,views.contract_archiving, name='contract_archiving'),
    path('contract-management-automation/' ,views.contract_management_automation, name='contract_management_automation'),
    path('contract-negotiation/' ,views.contract_negotiation, name='contract_negotiation'),
    path('contract-signature/' ,views.contract_signature, name='contract_signature'),
    path('dynamic-contract-template/' ,views.dynamic_contract_template, name='dynamic_contract_template'),
    path('ebooks/' ,views.ebooks, name='ebooks'),
    path('generation-contract/' ,views.generation_contract, name='generation_contract'),
    path('internal-collaboration/' ,views.internal_collaboration, name='internal_collaboration'),
    path('oro-AI/' ,views.oro_AI, name='oro_AI'),
    path('partners/' ,views.partners, name='partners'),
    path('pricing/' ,views.pricing, name='pricing'),
    path('suivi-contrat/' ,views.suivi_contrat, name='suivi_contrat'),
    path('templates-clauses/' ,views.templates_clauses, name='templates_clauses'),
    path('login/' ,views.login, name='login'),
    path('profile/' ,views.profile, name='profile'),
    path("logout/", views.user_logout, name="logout"),

    #API urls
    path("api/users/create/", views.UserCreateView.as_view(), name="user-create"),
    path("api/users/<int:pk>/update/", views.UserUpdateView.as_view(), name="user-update"),
    path("api/users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user-delete"),
    path("api/users/<int:pk>/reset_password/", views.ResetPasswordAPIView.as_view()),

    #get
    path("api/users/", views.UserListView.as_view(), name="user-list"),                  # все пользователи
    path("api/workers/", views.UserListViewWorkers.as_view(), name="workers-list"),                  # все пользователи
    path("api/users/<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),     # конкретный пользователь
    path("api/users/created-by-me/", views.UserCreatedByMeListView.as_view(), name="user-created-by-me"),  # только мои
    path("api/user-stats/", views.UserStatsView.as_view(), name="user-stats"),


    path("api/login/", views.LoginAPIView.as_view(), name="login-api"),
    path('api/profile/', views.ProfileView.as_view(), name='api-profile'),

    #link
    path('api/link/info', views.LinkInfo.as_view(), name='api-link-info'),
    path('api/link/delete', views.LinkDelete.as_view(), name='api-link-delete'),
    path('api/link/create', views.LinkCreate.as_view(), name='api-link-create'),



    path('api/mode/carantin/create', views.CarantinOn.as_view(), name='carantin_on'),
    path('api/mode/carantin/delete', views.CarantinOf.as_view(), name='carantin_of'),

    path('api/mode/503/create', views.ErrorOn.as_view(), name='Error_on'),
    path('api/mode/503/delete', views.ErrorOf.as_view(), name='Error_of'),

    path('api/mode/white-list/create', views.WhitelistOn.as_view(), name='whiteip_on'),
    path('api/mode/white-list/delete', views.WhitelistOf.as_view(), name='whiteip_of'),

    path('api/mode/states/', views.SystemStatesView.as_view(), name='system_states'),
    path('api/white-list/ip/add', views.AddIPToWhitelist.as_view(), name='add_ip'),
    path('api/white-list/ip/delete', views.DeleteIPToWhitelist.as_view(), name='delete_ip'),

    path('api/mode/logs/', views.ModeLogList.as_view(), name='mode_logs'),
]

handler404 = 'users.views.error_page'