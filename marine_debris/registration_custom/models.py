import random
import re
import sha

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from registration.models import RegistrationManager, RegistrationProfile

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class OdfwRegistrationManager(RegistrationManager):
    def create_inactive_user(self, username, password, email,
                             send_email=True, profile_callback=None):
        """
        Create a new, inactive ``User``, generates a
        ``RegistrationProfile`` and email its activation key to the
        ``User``, returning the new ``User``.
        
        To disable the email, call with ``send_email=False``.
        
        To enable creation of a custom user profile along with the
        ``User`` (e.g., the model specified in the
        ``AUTH_PROFILE_MODULE`` setting), define a function which
        knows how to create and save an instance of that model with
        appropriate default values, and pass it as the keyword
        argument ``profile_callback``. This function should accept one
        keyword argument:

        ``user``
            The ``User`` to relate the profile to.
        
        """
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()
        
        registration_profile = self.create_profile(new_user)
        
        if profile_callback is not None:
            profile_callback(user=new_user)
        
        if send_email:
            from django.core.mail import send_mail
            current_site = Site.objects.get_current()
            
            subject = render_to_string('registration/activation_email_subject.txt',
                                       { 'site': current_site })
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            message = render_to_string('registration/activation_email.txt',
                                       { 'username': username,
                                         'password': password,
                                         'activation_key': registration_profile.activation_key,
                                         'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                         'site': current_site })
            
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [new_user.email])
        return new_user

'''
Subclass RegistrationProfile in order to define a custom profile manager
'''     
class OdfwRegistrationProfile(models.Model):
    """
    *Replaces the default RegistrationProfile class in order to override
    *the manager it uses with our custom one.  Tried just subclassing
    *RegistrationProfile and changing the manager but it wasn't working
    *properly, causing strange errors on save.
     ***   
    A simple profile which stores an activation key for use during
    user account registration.
    
    Generally, you will not want to interact directly with instances
    of this model; the provided manager includes methods
    for creating and activating new accounts, as well as for cleaning
    out accounts which have never been activated.
    
    While it is possible to use this model as the value of the
    ``AUTH_PROFILE_MODULE`` setting, it's not recommended that you do
    so. This model's sole purpose is to store data temporarily during
    account registration and activation, and a mechanism for
    automatically creating an instance of a site-specific profile
    model is provided via the ``create_inactive_user`` on
    ``RegistrationManager``.
    
    """
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    activation_key = models.CharField(_('activation key'), max_length=40)
    
    objects = OdfwRegistrationManager()
    
    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')
        db_table = u'registration_registrationprofile' #Match the default name
    
    def __unicode__(self):
        return u"Registration information for %s" % self.user
    
    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.
        
        Key expiration is determined by a two-step process:
        
        1. If the user has already activated, the key will have been
           reset to the string ``ALREADY_ACTIVATED``. Re-activating is
           not permitted, and so this method returns ``True`` in this
           case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.
        
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == "ALREADY_ACTIVATED" or \
               (self.user.date_joined + expiration_date <= datetime.datetime.now())
    activation_key_expired.boolean = True                
