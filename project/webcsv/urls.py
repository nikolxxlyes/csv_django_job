from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'webcsv'

urlpatterns = [
    path('', views.SchemasView.as_view(), name='index'),
    path('schemas/', views.SchemasView.as_view(), name='schemas'),
    path('schema/new/', views.new_schema, name='new_schema'),
    path('schema/<int:schema_id>/delete/', views.delete_schema, name='delete_schema'),
    path('schema/<int:schema_id>/edit', views.edit_schema, name='edit_schema'),
    path('schema/<int:schema_id>/', views.SchemaDatasView.as_view(), name='csvs'),
    path('ajax/gen_csv/<int:schema_id>/', views.generate_csv, name='gen_csv'),
    path('ajax/check_csv/<int:schema_id>/', views.check_csv, name='check_csv'),
    path('media/<int:csv_id>/', views.download_csv, name='download_csv'),
]

# Allow download file from media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
