# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# Copyright (C) 2010-2014 GRNET S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from cStringIO import StringIO
from django import forms
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.sites.models import Site
from django.contrib import messages
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.core.mail import send_mail, mail_managers
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string, get_template
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.http import (
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponse
)

from ganeti.models import (
    Network,
    Cluster,
)


from apply.forms import InstanceApplicationForm, InstanceApplicationReviewForm
from apply.decorators import any_permission_required
from apply.models import (
    InstanceApplication,
    STATUS_APPROVED,
    STATUS_PENDING,
    STATUS_REFUSED,
    PENDING_CODES
)

# import views files
from user import *


@login_required
def apply(request):
    user_groups = request.user.groups.all()
    user_networks = Network.objects.filter(groups__in=user_groups).distinct()
    if user_networks:
        InstanceApplicationForm.base_fields["network"] = \
            forms.ModelChoiceField(
                queryset=user_networks, required=False,
                label=_("Network"),
                help_text=_(
                    "Optionally, select a network to connect the virtual"
                    "machine to if you have a special requirement"
                )
        )
    else:
        try:
            del InstanceApplicationForm.base_fields["network"]
        except KeyError:
            pass

    if request.method == "GET":
        form = InstanceApplicationForm()
        return render(
            request,
            'apply/apply.html',
            {'form': form},
        )
    else:
        form = InstanceApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.operating_system = form.cleaned_data['operating_system']
            application.applicant = request.user
            application.status = STATUS_PENDING

            net = request.POST.get('network', '')
            if net:
                network = Network.objects.get(pk=net)
                application.instance_params = {
                    "cluster": network.cluster.slug,
                    "network": network.link,
                    "mode": network.mode
                }
            application.save()
            fqdn = Site.objects.get_current().domain
            admin_url = "https://%s%s" % (
                fqdn,
                reverse(
                    'application-review',
                    kwargs={"application_id": application.pk}
                )
            )
            mail_body = render_to_string(
                'apply/emails/apply_mail.txt',
                {
                    "application": application,
                    "user": request.user,
                    "url": admin_url
                }
            )
            mail_managers(
                "New instance request by %s: %s" % (
                    request.user, application.hostname
                ),
                mail_body
            )
            messages.add_message(
                request,
                messages.INFO,
                _(
                    "Your request has been filed with id #%d and"
                    " will be processed shortly."
                ) % application.id
            )
            if request.user.is_superuser:
                return HttpResponseRedirect(reverse(
                    'application-review',
                    kwargs={'application_id': application.id}
                ))
            return HttpResponseRedirect(reverse("user-instances"))
        else:
            return render(
                request,
                'apply/apply.html',
                {'form': form}
            )


@any_permission_required(
    "apply.change_instanceapplication",
    "apply.view_applications"
)
def application_list(request):
    applications = InstanceApplication.objects.all()
    pending = applications.filter(status__in=PENDING_CODES)
    completed = applications.exclude(status__in=PENDING_CODES)

    return render(
        request,
        'apply/application_list.html',
        {
            'applications': applications,
            'pending': pending,
            'completed': completed
        }
    )


@permission_required("apply.change_instanceapplication")
def review_application(request, application_id):
    applications = InstanceApplication.objects.filter(status__in=PENDING_CODES)
    app = get_object_or_404(InstanceApplication, pk=application_id)
    fast_clusters = Cluster.objects.filter(fast_create=True).exclude(
        disable_instance_creation=True
    ).order_by('description')

    if request.method == "GET":
        form = InstanceApplicationReviewForm(
            instance=app,
            initial={
                'operating_system': app.operating_system
            }
        )
        if app.instance_params and 'cluster' in app.instance_params.keys():
            form = InstanceApplicationReviewForm(
                instance=app,
                initial={
                    "cluster": Cluster.objects.get(
                        slug=app.instance_params['cluster']
                    ).pk,
                    'operating_system': app.operating_system
                })
        return render(
            request,
            'apply/review.html',
            {
                'application': app,
                'applications': applications,
                'appform': form,
                'fast_clusters': fast_clusters
            }
        )
    else:
        nodegroup = request.POST.get('node_group', '')
        form_ngs = (('', ''),)
        if nodegroup:
            form_ngs = ((nodegroup, nodegroup),)

        netw = request.POST.get('netw', '')
        form_netw = (('', ''),)
        if netw:
            form_netw = ((netw, netw),)

        vgs = request.POST.get('vgs', '')
        form_vgs = (('', ''),)
        if vgs:
            form_vgs = ((vgs, vgs),)

        dt = request.POST.get('disk_template', '')
        form_dt = (('', ''),)
        if dt:
            form_dt = ((dt, dt),)
        form = InstanceApplicationReviewForm(request.POST, instance=app)
        form.fields['node_group'] = forms.ChoiceField(choices=form_ngs)
        form.fields['netw'] = forms.ChoiceField(choices=form_netw)
        form.fields['vgs'] = forms.ChoiceField(choices=form_vgs)
        form.fields['disk_template'] = forms.ChoiceField(choices=form_dt)
        if form.is_valid():
            application = form.save(commit=False)
            application.operating_system = form.cleaned_data['operating_system']
            if "reject" in request.POST:
                application.status = STATUS_REFUSED
                application.save()
                mail_body = render_to_string("apply/emails/application_rejected_mail.txt",
                                             {"application": application})
                send_mail(
                    settings.EMAIL_SUBJECT_PREFIX + "Application for %s rejected" % (
                        application.hostname
                    ),
                    mail_body,
                    settings.SERVER_EMAIL,
                    [application.applicant.email]
                )
                messages.add_message(request, messages.INFO,
                                     "Application #%d rejected, user %s has"
                                     " been notified" % (app.pk, request.user))
            else:
                application.status = STATUS_APPROVED
                application.instance_params = {
                    'cluster': Cluster.objects.get(
                        pk=form.cleaned_data['cluster']
                    ).slug,
                    'network': form.cleaned_data['netw'].split("::")[0],
                    'mode': form.cleaned_data['netw'].split("::")[1],
                    'node_group': form.cleaned_data['node_group'],
                    'vgs': form.cleaned_data['vgs'],
                    'disk_template': form.cleaned_data['disk_template'],
                }
                application.save()
                application.submit()
                messages.add_message(request, messages.INFO,
                                     "Application #%d accepted and submitted"
                                     " to %s" % (app.pk, application.cluster))
            cache.delete('pendingapplications')
            return HttpResponseRedirect(reverse("application-list"))
        else:
            return render(
                request,
                'apply/review.html',
                {
                    'application': app,
                    'applications': applications,
                    'appform': form,
                    'fast_clusters': fast_clusters
                }
            )


def instance_ssh_keys(request, application_id, cookie):
    app = get_object_or_404(InstanceApplication, pk=application_id)
    if cookie != app.cookie:
        t = get_template("403.html")
        return HttpResponseForbidden(content=t.render(RequestContext(request)))

    output = StringIO()
    output.writelines([k.key_line() for k in
                       app.applicant.sshpublickey_set.all()])
    return HttpResponse(output.getvalue(), mimetype="text/plain")


