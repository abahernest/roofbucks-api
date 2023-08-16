from django.urls import path
from .views import (NewPropertyAPIView, StayPeriodAPIView,
                    PropertyListView, PropertyDetailView, 
                    UpdatePropertyAPIView, RemoveMediaView, SimilarPropertyView,
                    ShoppingCartAPIView, CreateAndListSiteVisitAPIView, PropertyTopdealsViewset,
                    AcceptAndRejectInspectionAPIView, PropertyListingViewset,PropertyMarketplaceViewset,
                    CancelSiteVisitAPIView, AgentPropertyInspectionsAPIView
                    )

urlpatterns = [
    path(
        '', PropertyListView.as_view({'get': 'list'}), name='all_properties'),
    path(
        'listings/', PropertyListingViewset.as_view({'get': 'list'}), name='property_listing'),
    path(
        'topdeals/', PropertyTopdealsViewset.as_view({'get': 'list'}), name='property_topdeals'),
    path(
        'marketplace/', PropertyMarketplaceViewset.as_view({'get': 'list'}), name='property_marketplace'),
    path('new/', NewPropertyAPIView.as_view(), name='new_property'),
    path('stay-periods/<property_id>/',
         StayPeriodAPIView.as_view(), name='add_stay_periods'),
    path('stay-periods/<property_id>/<index_of_stay_period>/',
         StayPeriodAPIView.as_view(), name='delete_stay_periods'),
    path('single/<property_id>/', PropertyDetailView.as_view(), name='single_property'),
    path('update/<property_id>/', UpdatePropertyAPIView.as_view(), name='update_property'),
    path('media/<media_type>/<property_id>/<media_id>/',
         RemoveMediaView.as_view(), name='property_media'),
    path('similar_properties/<property_id>/',
         SimilarPropertyView.as_view(), name='similar_property'),
    path('shopping_cart/',
         ShoppingCartAPIView.as_view(), name='shopping_cart'),
    path('site_visit/',
         CreateAndListSiteVisitAPIView.as_view(), name='schedule_site_visit'),
    path('agent_site_visit/',
         AgentPropertyInspectionsAPIView.as_view(), name='agent_property_inspections'),
    path('agent_site_visit/<visitation_id>/<agent_action>/',
         AcceptAndRejectInspectionAPIView.as_view(), name='accept_and_reject_inspection'),
    path('site_visit/<visitation_id>/cancel/',
         CancelSiteVisitAPIView.as_view(), name='cancel_site_inspection')
]
