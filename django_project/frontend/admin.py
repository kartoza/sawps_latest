"""Admin page for Context Layer models."""
from celery.result import AsyncResult
from core.celery import app
from core.settings.utils import absolute_path
from django.contrib import admin, messages
from django.core.management import call_command
from django.forms import ModelForm
from django.forms.widgets import TextInput
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path
from django.utils.html import format_html
from frontend.models import (
    BoundaryFile,
    BoundarySearchRequest,
    ContextLayer,
    ContextLayerLegend,
    ContextLayerTilingTask,
    DraftSpeciesUpload,
    StatisticalModel,
    StatisticalModelOutput,
)
from frontend.models.spatial import SpatialDataModel, SpatialDataValueModel
from frontend.tasks import (
    clear_older_vector_tiles,
    generate_vector_tiles_task,
    start_plumber_process,
)


def cancel_other_processing_tasks(task_id=None):
    """Cancel any ongoing vector tile tasks."""
    tasks = ContextLayerTilingTask.objects.filter(
        status=ContextLayerTilingTask.TileStatus.PROCESSING
    )
    if task_id:
        tasks = tasks.exclude(id=task_id)
    for tiling_task in tasks:
        if tiling_task.task_id:
            res = AsyncResult(tiling_task.task_id)
            if not res.ready():
                app.control.revoke(
                    tiling_task.task_id,
                    terminate=True
                )
        tiling_task.task_id = None
        tiling_task.status = (
            ContextLayerTilingTask.TileStatus.CANCELLED
        )
        tiling_task.save()


@admin.action(description='Generate Vector Tile')
def generate_vector_tiles(modeladmin, request, queryset):
    cancel_other_processing_tasks()
    for tiling_task in queryset:
        if tiling_task.task_id:
            res = AsyncResult(tiling_task.task_id)
            if not res.ready():
                app.control.revoke(
                    tiling_task.task_id,
                    terminate=True
                )
        task = generate_vector_tiles_task.delay(tiling_task.id, True)
        tiling_task.task_id = task.id
        tiling_task.save()
    modeladmin.message_user(
        request,
        'Vector tile generation will be run in background!',
        messages.SUCCESS
    )


@admin.action(description='Resume Vector Tile Generation')
def resume_generate_vector_tiles(modeladmin, request, queryset):
    cancel_other_processing_tasks()
    for tiling_task in queryset:
        if tiling_task.task_id:
            res = AsyncResult(tiling_task.task_id)
            if not res.ready():
                app.control.revoke(
                    tiling_task.task_id,
                    terminate=True
                )
        task = generate_vector_tiles_task.delay(tiling_task.id, False)
        tiling_task.task_id = task.id
        tiling_task.save()
    modeladmin.message_user(
        request,
        'Vector tile generation will be run in background!',
        messages.SUCCESS
    )


@admin.action(description='Cancel Vector Tile Generation')
def cancel_generate_vector_tiles(modeladmin, request, queryset):
    for tiling_task in queryset:
        if tiling_task.task_id:
            res = AsyncResult(tiling_task.task_id)
            if not res.ready():
                app.control.revoke(
                    tiling_task.task_id,
                    terminate=True
                )
                tiling_task.task_id = None
                tiling_task.status = (
                    ContextLayerTilingTask.TileStatus.CANCELLED
                )
                tiling_task.save()
    modeladmin.message_user(
        request,
        'Vector tile task has been cancelled!',
        messages.SUCCESS
    )


@admin.action(description='Clear Vector Tile Directory')
def clear_vector_tiles(modeladmin, request, queryset):
    clear_older_vector_tiles.delay()
    modeladmin.message_user(
        request,
        'Vector tile directory will be cleared in background!',
        messages.SUCCESS
    )


class TilingTaskAdmin(admin.ModelAdmin):
    list_display = ('status', 'started_at',
                    'finished_at', 'total_size')
    actions = [generate_vector_tiles, resume_generate_vector_tiles,
               cancel_generate_vector_tiles, clear_vector_tiles]


class BoundaryFileAdmin(admin.ModelAdmin):
    list_display = ('meta_id', 'name', 'upload_date', 'session', 'file_type')


class BoundarySearchRequestAdmin(admin.ModelAdmin):
    list_display = ('session', 'type', 'status', 'progress')


class ContextLayerAdmin(admin.ModelAdmin):
    change_list_template = "admin/context_layer.html"
    list_display = ('name', 'is_static')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('reload_fixtures/', self.reload_fixtures),
        ]
        return my_urls + urls

    def reload_fixtures(self, request):
        # delete
        ContextLayer.objects.all().delete()
        # load fixtures from json files
        call_command('loaddata', 'fixtures/context_layer.json',
                     app_label='frontend')
        call_command('loaddata', 'fixtures/context_layer_legend.json',
                     app_label='frontend')
        self.message_user(
            request,
            'Context layer fixtures has been successfully reloaded!',
            messages.SUCCESS
        )
        return HttpResponseRedirect('/admin/frontend/contextlayer/')


class ContextLayerLegendForm(ModelForm):
    class Meta:
        model = ContextLayerLegend
        fields = '__all__'
        widgets = {
            'colour': TextInput(attrs={'type': 'color'}),
        }


class ContextLayerLegendAdmin(admin.ModelAdmin):
    list_display = ('name', 'layer', 'display_color')
    form = ContextLayerLegendForm

    def display_color(self, obj):
        return format_html(
            '<span style="width:10px;height:10px;'
            'display:inline-block;background-color:%s"></span>' % obj.colour
        )
    display_color.short_description = 'Colour'
    display_color.allow_tags = True


class DraftSpeciesUploadAdmin(admin.ModelAdmin):
    list_display = ('name', 'property', 'upload_by', 'taxon', 'year')


@admin.action(description='Restart plumber process')
def restart_plumber_process(modeladmin, request, queryset):
    start_plumber_process.apply_async(queue='plumber')
    modeladmin.message_user(
        request,
        'Plumber process will be started in background!',
        messages.SUCCESS
    )


class StatisticalModelOutputInline(admin.TabularInline):
    model = StatisticalModelOutput
    extra = 1


class StatisticalModelAdmin(admin.ModelAdmin):
    change_form_template = "admin/statistical_model_change_form.html"
    list_display = ('taxon', 'name')
    search_fields = ['taxon', 'name']
    actions = [restart_plumber_process]
    inlines = [StatisticalModelOutputInline]

    def response_change(self, request, obj):
        if '_download-data-template' in request.POST:
            template_file = absolute_path(
                'frontend', 'utils', 'data_sample.csv'
            )
            with open(template_file) as f:
                response = HttpResponse(
                    f.read(), content_type='text/csv'
                )
            response['Content-Disposition'] = (
                'attachment; filename="data_template.csv"'
            )
            return response
        return super().response_change(request, obj)


admin.site.register(ContextLayer, ContextLayerAdmin)
admin.site.register(ContextLayerLegend, ContextLayerLegendAdmin)
admin.site.register(ContextLayerTilingTask, TilingTaskAdmin)
admin.site.register(BoundaryFile, BoundaryFileAdmin)
admin.site.register(BoundarySearchRequest, BoundarySearchRequestAdmin)
admin.site.register(DraftSpeciesUpload, DraftSpeciesUploadAdmin)
admin.site.register(StatisticalModel, StatisticalModelAdmin)
admin.site.register(SpatialDataModel)
admin.site.register(SpatialDataValueModel)
