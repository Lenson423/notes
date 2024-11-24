import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import Note, AddNoteForm
from django.contrib import messages
import json, os
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from io import BytesIO
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.signing import BadSignature
from taggit.models import Tag

# Setup logger
logger = logging.getLogger(__name__)


def link_callback(uri, rel):
    try:
        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
        return path
    except Exception as e:
        logger.error(f"Error in link_callback: {str(e)}")
        raise e


def render_to_pdf(template_src, context_dict={}):
    try:
        template = get_template(template_src)
        html = template.render(context_dict)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        else:
            logger.error("Error rendering PDF.")
            return HttpResponse("Error Rendering PDF", status=400)
    except Exception as e:
        logger.error(f"Error in render_to_pdf: {str(e)}")
        return HttpResponse("Error Rendering PDF", status=400)


def generate_pdf(request, slug):
    try:
        note = get_object_or_404(Note, slug=slug)
        if note.user != request.user:
            messages.error(request, 'You are not authenticated to perform this action')
            return redirect('notes')

        notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
        add_note_form = AddNoteForm()
        context = {'note_detail': note}
        pdf = render_to_pdf('note_as_pdf.html', context)

        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "{}.pdf".format(note.slug)
            content = "inline; filename={}".format(filename)
            content = "attachment; filename={}".format(filename)
            response['Content-Disposition'] = content
            return response
        else:
            logger.warning(f"PDF for note {slug} not found.")
            return HttpResponse("Not found")
    except Exception as e:
        logger.error(f"Error generating PDF for note {slug}: {str(e)}")
        return HttpResponse("Error generating PDF", status=500)


def home(request):
    try:
        if request.user.is_authenticated:
            notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
            all_notes = Note.objects.filter(user=request.user).order_by('-updated_at')

            if request.method == 'POST':
                form = AddNoteForm(request.POST)
                if form.is_valid():
                    form_data = form.save(commit=False)
                    form_data.user = request.user
                    form_data.save()
                    form.save_m2m()
                    form = AddNoteForm()
                    messages.success(request, 'Note added successfully!')
                    return redirect('notes')
            else:
                form = AddNoteForm()

            context = {
                'notes': notes,
                'all_notes': all_notes,
                'add_note_form': form,
                'script_name': request.META['SCRIPT_NAME'],
            }
            return render(request, 'notes.html', context)
        else:
            logger.info("User is not authenticated, showing index page.")
            return render(request, 'index.html')
    except Exception as e:
        logger.error(f"Error in home view: {str(e)}")
        return HttpResponse("An error occurred", status=500)


def get_note_details(request, slug):
    try:
        note = get_object_or_404(Note, slug=slug)
        if note.user != request.user:
            messages.error(request, 'You are not authenticated to perform this action')
            return redirect('notes')

        notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
        add_note_form = AddNoteForm()
        absolute_url = request.build_absolute_uri(note.get_absolute_url())

        context = {
            'notes': notes,
            'note_detail': note,
            'add_note_form': add_note_form,
            'absolute_url': absolute_url
        }
        return render(request, 'note_details.html', context)
    except Exception as e:
        logger.error(f"Error in get_note_details for slug {slug}: {str(e)}")
        return HttpResponse("Error retrieving note details", status=500)


def edit_note_details(request, pk):
    try:
        note = get_object_or_404(Note, pk=pk)
        if note.user != request.user:
            messages.error(request, 'You are not authenticated to perform this action')
            return redirect('notes')

        if request.method == 'POST':
            form = AddNoteForm(request.POST, instance=note)
            if form.is_valid():
                form_data = form.save(commit=False)
                form_data.user = request.user
                form_data.save()
                form.save_m2m()
                return redirect('note_detail', slug=note.slug)
        else:
            form = AddNoteForm(initial={
                'note_title': note.note_title,
                'note_content': note.note_content,
                'tags': ','.join([i.slug for i in note.tags.all()]),
            }, instance=note)
            return render(request, 'modals/edit_note_modal.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in edit_note_details for pk {pk}: {str(e)}")
        return HttpResponse("Error editing note details", status=500)


def confirm_delete_note(request, pk):
    try:
        note = get_object_or_404(Note, pk=pk)
        if note.user != request.user:
            messages.error(request, 'You are not authenticated to perform this action')
            return redirect('notes')

        context = {
            'note_detail': note,
        }
        return render(request, 'modals/delete_note_modal.html', context)
    except Exception as e:
        logger.error(f"Error in confirm_delete_note for pk {pk}: {str(e)}")
        return HttpResponse("Error confirming deletion", status=500)


def delete_note(request, pk):
    try:
        note = get_object_or_404(Note, pk=pk)
        if note.user != request.user:
            messages.error(request, 'You are not authenticated to perform this action')
            return redirect('notes')
        note.delete()
        messages.success(request, 'Note deleted successfully!')
        return redirect('notes')
    except Exception as e:
        logger.error(f"Error in delete_note for pk {pk}: {str(e)}")
        return HttpResponse("Error deleting note", status=500)


def search_note(request):
    try:
        if request.is_ajax():
            q = request.GET.get('term')
            notes = Note.objects.filter(
                note_title__icontains=q,
                user=request.user
            )[:10]
            results = []
            for note in notes:
                note_json = {}
                note_json['slug'] = note.slug
                note_json['label'] = note.note_title
                note_json['value'] = note.note_title
                results.append(note_json)
            data = json.dumps(results)
        else:
            note_json = {}
            note_json['slug'] = None
            note_json['label'] = None
            note_json['value'] = None
            data = json.dumps(note_json)
        return HttpResponse(data)
    except Exception as e:
        logger.error(f"Error in search_note: {str(e)}")
        return HttpResponse("Error searching notes", status=500)


def get_shareable_link(request, signed_pk):
    try:
        pk = Note.signer.unsign(signed_pk)
        note = Note.objects.get(pk=pk)
        context = {'note_detail': note}
        return render(request, 'shared_note.html', context)
    except (BadSignature, Note.DoesNotExist) as e:
        logger.warning(f"Error in get_shareable_link for signed_pk {signed_pk}: {str(e)}")
        raise Http404('No Order matches the given query.')


def get_all_notes_tags(request, slug):
    try:
        tag = get_object_or_404(Tag, slug=slug)
        all_notes = Note.objects.filter(tags=tag, user=request.user)
        notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
        add_note_form = AddNoteForm()
        context = {
            'tag': tag,
            'all_notes': all_notes,
            'notes': notes,
            'add_note_form': add_note_form,
        }
        return render(request, 'notes.html', context)
    except Exception as e:
        logger.error(f"Error in get_all_notes_tags for slug {slug}: {str(e)}")
        return HttpResponse("Error retrieving notes by tag", status=500)
