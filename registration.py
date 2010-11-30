#!/usr/bin/env python
#
# Copyright 2010 Eric Entzel <eric@ubermac.net>
#
from google.appengine.ext.webapp import util
from google.appengine.runtime import apiproxy_errors
import os
import google_api
import ecal


class RegistrationHandler(ecal.EcalRequestHandler):
    def authorization_denied(self):
        self.redirect("/")

    def authorization_succeeded(self):
        session_token = google_api.permanent_token_from_temp_token(self.temp_token)
        myuser = ecal.EcalUser(auth_token=session_token.get_token_string())
        try:
            myuser.put()
        except apiproxy_errors.CapabilityDisabledError:
            template_values = {
                'title': 'Unable to create account',
                'error_text': "We couldn't create your account right now because the database is in read-only mode for maintenance.  Please try back in a few minutes."
                }
            self.respond_with_template('error.html', template_values)
            return
        template_values = { 'email_address': myuser.email_address + '@' + os.environ['APPLICATION_ID'] + '.appspotmail.com' }
        self.respond_with_template('success.html', template_values)

    def get(self):
        self.temp_token = google_api.temp_token_from_url(self.request.uri)
        if self.temp_token != None:
            self.authorization_succeeded()
        else:
            self.authorization_denied()


def main():
    application = ecal.EcalWSGIApplication([('/register', RegistrationHandler)])
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
