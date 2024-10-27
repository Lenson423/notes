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

import logging

logger = logging.getLogger(__name__)

authenticated_message = 'You are not authenticated to perform this action'


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
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


def render_to_pdf(template_src, context_dict={}):
    '''
        Helper function to generate pdf from html
    '''
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("Error Rendering PDF", status=400)


def generate_pdf(request, slug):
    logger.info(f"Generating PDF for note with slug: {slug}")
    note = get_object_or_404(Note, slug=slug)
    if note.user != request.user:
        logger.warning("User attempted to access a note they don't own.")
        messages.error(request, authenticated_message)
        return redirect('notes')
    # notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
    # add_note_form = AddNoteForm()
    context = {
        'note_detail': note,
    }
    pdf = render_to_pdf('note_as_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "{}.pdf".format(note.slug)
        # content = "inline; filename={}".format(filename)
        content = "attachment; filename={}".format(filename)
        response['Content-Disposition'] = content
        return response
    logger.error("Error rendering PDF.")
    return HttpResponse("Not found")


def home(request):
    if request.user.is_authenticated:
        logger.debug(f"Authenticated user {request.user} accessing home.")
        notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
        all_notes = Note.objects.filter(user=request.user).order_by('-updated_at')

        if request.method == 'POST':
            form = AddNoteForm(request.POST)
            if form.is_valid():
                form_data = form.save(commit=False)
                form_data.user = request.user
                form_data.save()
                # Without this next line the tags won't be saved.
                form.save_m2m()
                # form = AddNoteForm()
                messages.success(request, 'Note added successfully!')
                logger.info(f"Note added successfully by user {request.user}.")
                return redirect('notes')
            else:
                logger.warning("Form submission failed; invalid data provided.")
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
        logger.info("Unauthenticated user accessing the home page.")
        return render(request, 'index.html')


def get_note_details(request, slug):
    note = get_object_or_404(Note, slug=slug)
    if note.user != request.user:
        messages.error(request, authenticated_message)
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


def edit_note_details(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if note.user != request.user:
        messages.error(request, authenticated_message)
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


def confirm_delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if note.user != request.user:
        logger.warning("Unauthorized delete attempt by user.")
        messages.error(request, authenticated_message)
        return redirect('notes')
    note.delete()
    context = {
        'note_detail': note,
    }
    logger.info(f"Note with ID {pk} deleted by user {request.user}.")
    return render(request, 'modals/delete_note_modal.html', context)


def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if note.user != request.user:
        messages.error(request, authenticated_message)
        return redirect('notes')
    note.delete()
    messages.success(request, 'Note deleted successfully!')
    return redirect('notes')


def search_note(request):
    if request.is_ajax():
        logger.debug("Processing AJAX request for note search.")
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
        logger.info("Search results generated.")
    else:
        logger.debug("Non-AJAX request for note search.")
        data = json.dumps({'slug': None, 'label': None, 'value': None})
    return HttpResponse(data)


def get_shareable_link(request, signed_pk):
    try:
        pk = Note.signer.unsign(signed_pk)
        note = Note.objects.get(pk=pk)
        context = {
            'note_detail': note
        }
        return render(request, 'shared_note.html', context)
    except (BadSignature, Note.DoesNotExist):
        raise Http404('No Order matches the given query.')


def get_all_notes_tags(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    all_notes = Note.objects.filter(tags=tag, user=request.user)
    notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
    add_note_form = AddNoteForm()
    context = {
        'tag': tag,
        'all_notes': all_notes,
        'notes': notes,
        'add_note_form': add_note_form
    }
    return render(request, 'tags.html', context)
