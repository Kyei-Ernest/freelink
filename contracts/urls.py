from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContractViewSet, ContractAcceptView, ContractRejectView,
    ContractDisputeView, ContractSubmitWorkView,
    UserContractsView, MilestoneViewSet,
)

router = DefaultRouter()
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'contracts/(?P<contract_id>[^/.]+)/milestones', MilestoneViewSet, basename='milestone')
#router.register(r'contracts/(?P<contract_id>[^/.]+)/documents', ContractDocumentViewSet, basename='contract-document')

urlpatterns = [
    path('', include(router.urls)),
    path('contracts/<uuid:pk>/accept/', ContractAcceptView.as_view(), name='contract-accept'),
    path('contracts/<uuid:pk>/reject/', ContractRejectView.as_view(), name='contract-reject'),
    #path('contracts/<uuid:pk>/cancel/', ContractCancelView.as_view(), name='contract-cancel'),
    #path('contracts/<uuid:pk>/mark-complete/', ContractMarkCompleteView.as_view(), name='contract-mark-complete'),
    path('contracts/<uuid:pk>/dispute/', ContractDisputeView.as_view(), name='contract-dispute'),
    path('contracts/<uuid:pk>/submit-work/', ContractSubmitWorkView.as_view(), name='contract-submit-work'),
    path('contracts/user/<int:user_id>/', UserContractsView.as_view(), name='user-contracts'),
]
