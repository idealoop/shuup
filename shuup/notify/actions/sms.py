# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2020, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.

import logging

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from shuup.admin.forms.widgets import TextEditorWidget
from shuup.notify.base import Action, Binding
from shuup.notify.enums import ConstantUse, TemplateUse
from shuup.notify.typology import Phone, Language, Text


class SendSMS(Action):
    identifier = "send_sms"
    template_use = TemplateUse.MULTILINGUAL
    template_fields = {
        "body": forms.CharField(required=True, label=_("SMS Body"), widget=TextEditorWidget())
    }
    recipient = Binding(_("Recipient"), type=Phone, constant_use=ConstantUse.VARIABLE_OR_CONSTANT, required=True)
    from_phone = Binding(
        _("From phone"),
        type=Phone,
        constant_use=ConstantUse.VARIABLE_OR_CONSTANT,
        required=False,
        help_text=_(
            'Override the default from phone to be used.'
        )
    )
    language = Binding(_("Language"), type=Language, constant_use=ConstantUse.VARIABLE_OR_CONSTANT, required=True)
    fallback_language = Binding(
        _("Fallback language"), type=Language, constant_use=ConstantUse.CONSTANT_ONLY,
        default=settings.PARLER_DEFAULT_LANGUAGE_CODE
    )
    send_identifier = Binding(
        _("Send Identifier"), type=Text, constant_use=ConstantUse.CONSTANT_ONLY, required=False,
        help_text=_(
            "If set, this identifier will be logged into the event's log target. If the identifier has already "
            "been logged, the SMS won't be sent again."
        )
    )

    def execute(self, context):
        """
        :param context: Script Context
        :type context: shuup.notify.script.Context
        """
        recipient = self.get_value(context, "recipient")
        if not recipient:
            context.log(logging.INFO, "%s: Not sending SMS, no recipient", self.identifier)
            return

        send_identifier = self.get_value(context, "send_identifier")
        if send_identifier and context.log_entry_queryset.filter(identifier=send_identifier).exists():
            context.log(
                logging.INFO,
                "%s: Not sending SMS, have sent it already (%r)",
                self.identifier,
                send_identifier
            )
            return

        languages = [language for language in [
            self.get_value(context, "language"),
            self.get_value(context, "fallback_language"),
        ] if language and language in dict(settings.LANGUAGES).keys()]

        if not languages:
            languages = [settings.PARLER_DEFAULT_LANGUAGE_CODE]

        strings = self.get_template_values(context, languages)

        body = strings.get("body")

        if not body:
            context.log(
                logging.INFO,
                "%s: Not sending SMS to %s, body is empty",
                self.identifier,
                recipient
            )
            return

        
        from_phone = self.get_value(context, "from_phone")
        
        
        context.log(logging.INFO, "%s: SMS sent to %s : %s)", self.identifier, recipient, body)

        if send_identifier:
            context.add_log_entry_on_log_target("SMS sent to %s: %s" % (recipient, body), send_identifier)
