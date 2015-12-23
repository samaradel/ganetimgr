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

from django.contrib.auth import logout
import ipaddress
from django.contrib import messages
from django.utils.translation import ugettext as _
from accounts.utils import get_client_ip


class ForceLogoutMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            if (
                request.user.userprofile.force_logout_date and
                (
                    'LAST_LOGIN_DATE' not in request.session or
                    request.session['LAST_LOGIN_DATE'] < request.user.userprofile.force_logout_date
                )
            ):
                messages.add_message(
                    request,
                    messages.ERROR,
                    _('You have exceeded login date.')
                )
                logout(request)
            # in case user is not on one of his selected networks
            user_networks = request.user.userprofile.usernetwork_set.all()
            if user_networks:
                valid_network = False
                for network in user_networks:
                    try:
                        if (ipaddress.ip_address(get_client_ip(request)) in ipaddress.ip_network(network, strict=False)):
                            valid_network = True
                    except:
                        messages.add_message(
                            request,
                            messages.ERROR,
                            _(
                                'Network (%s) is not a valid network' % network
                            )
                        )
                if not valid_network:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        _(
                            'Your Ip (%s) is not on your networks.'
                            ' Logging you out!' % get_client_ip(request)
                        )
                    )
                    logout(request)
