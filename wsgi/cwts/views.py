from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.generic.list import ListView
from django.views.generic import DetailView


#from .models import 
from .forms import TicketForm, CloseTicketForm, SplitTicketForm, CommentForm
from .utils import is_admin


class cwtListView(ListView):
    pass