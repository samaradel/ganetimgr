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

from django.conf.urls import patterns, url
from ganeti import views

urlpatterns = patterns(
    '',
    # this view lives in jobs.py
    url(r'^jobdetails/?$', views.job_details, name="jobdets-popup"),
    url(r'^popup/?', views.instance_popup, name="instance-popup"),
    url(r'^nodes/$', views.get_clusternodes, name="cluster-nodes"),
    url(r'^nodes/pjax/$', views.get_clusternodes_pjax, name="cluster-nodes-pjax"),
    url(r'^jnodes/(?P<cluster>[0-9]+)/$', views.clusternodes_json, name="cluster-nodes-json"),
    url(r'^jnodes/$', views.clusternodes_json, name="cluster-nodes-json"),
    url(r'^instance/destreinst/(?P<application_hash>\w+)/(?P<action_id>\d+)/$', views.reinstalldestreview, name='reinstall-destroy-review'),
    url(r'^detail/$', views.clusterdetails, name="clusterdetails"),
    url(r'^detail/json/$', views.clusterdetails_json, name="clusterdetails_json"),

)
