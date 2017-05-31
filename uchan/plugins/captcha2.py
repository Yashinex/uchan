import dateutil.parser
import requests

from uchan import logger
from uchan.lib.exceptions import ArgumentError
from uchan.lib.service import verification_service
from uchan.lib.utils import now

"""
This plugin adds google reCaptcha v2 as a verification method.
Add the site key and secret like this in config.py:
PLUGIN_CONFIG = {
    'captcha2': {
        'sitekey': '',
        'secret': ''
    }
}

And add it to the enabled plugins list:
PLUGINS = ['captcha2']
"""


def describe_plugin():
    return {
        'name': 'captcha2',
        'description': 'This plugin adds google reCaptcha v2 as a verification method.',
        'version': 'unstable'
    }


class Recaptcha2Method(verification_service.VerificationMethod):
    def __init__(self, sitekey, secret):
        super().__init__()

        self.sitekey = sitekey
        self.secret = secret

        self.html = """
        <script src="https://www.google.com/recaptcha/api.js" async defer></script>
        <div class="g-recaptcha" data-sitekey="__sitekey__"></div>
        <noscript>
          <div>
            <div style="width: 302px; height: 422px; position: relative;">
              <div style="width: 302px; height: 422px; position: absolute;">
                <iframe src="https://www.google.com/recaptcha/api/fallback?k=__sitekey__"
                        frameborder="0" scrolling="no"
                        style="width: 302px; height:422px; border-style: none;">
                </iframe>
              </div>
            </div>
            <div style="width: 300px; height: 60px; border-style: none;
                           bottom: 12px; left: 25px; margin: 0px; padding: 0px; right: 25px;
                           background: #f9f9f9; border: 1px solid #c1c1c1; border-radius: 3px;">
              <textarea id="g-recaptcha-response" name="g-recaptcha-response"
                           class="g-recaptcha-response"
                           style="width: 250px; height: 40px; border: 1px solid #c1c1c1;
                                  margin: 10px 25px; padding: 0px; resize: none;" >
              </textarea>
            </div>
          </div>
        </noscript>
        """.replace('__sitekey__', self.sitekey)

    def get_html(self):
        return self.html

    def verification_in_request(self, request):
        return 'g-recaptcha-response' in request.form

    def verify_request(self, request):
        form = request.form

        response = form.get('g-recaptcha-response', None)
        if not response:
            raise ArgumentError('Please fill in the captcha')

        try:
            valid = self.verify(response)
        except Exception:
            logger.exception('Verify exception')
            raise ArgumentError('Error contacting recaptcha service')

        if not valid:
            raise ArgumentError('Captcha invalid')

    def verify(self, response):
        res = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': self.secret,
            'response': response
        })
        res_json = res.json()

        timestamp_iso = 'challenge_ts' in res_json and res_json['challenge_ts']
        if not timestamp_iso:
            return False

        timestamp = dateutil.parser.parse(timestamp_iso)
        time_ago = now() - int(timestamp.timestamp() * 1000)

        if time_ago > 1000 * 60 * 30:
            # Expired
            return False

        if 'success' in res_json and res_json['success'] is True:
            return True

        return False


def on_enable(configuration):
    if not configuration:
        raise RuntimeError('sitekey and secret must be set in the [captcha2] section of config.ini')

    sitekey = configuration.get('sitekey')
    secret = configuration.get('secret')
    if not sitekey or not secret:
        raise RuntimeError('"sitekey" or "secret" empty in the [captcha2] section of config.ini')

    method = Recaptcha2Method(sitekey, secret)
    verification_service.add_method(method)
