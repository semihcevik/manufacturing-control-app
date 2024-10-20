from django.urls import path
from .views import PartManufacturingView, PlaneManufacturingView, PartManufacturerInfoView, PartManufacturerRecycleView, \
    PlaneManufacturerInfoView, PlaneManufacturerRecycle, AssembleHistoryView

urlpatterns = [
    # Team Crud Operations
    # list,create,recycle(delete)

    # part creation teams
    path('part/create', PartManufacturingView.as_view(), name='part-manufacturing'),
    path('part/list', PartManufacturerInfoView.as_view(), name='part-list'),
    path('part/recycle', PartManufacturerRecycleView.as_view(), name='part-recycle'),

    # plane assembly team
    path('plane/create', PlaneManufacturingView.as_view(), name='plane-manufacturing'),
    path('plane/list', PlaneManufacturerInfoView.as_view(), name='plane-list'),
    path('plane/recycle', PlaneManufacturerRecycle.as_view(), name='plane-recycle'),


    path('plane/assemble-history', AssembleHistoryView.as_view() ,name='manufacturing-assemble-history'),
]