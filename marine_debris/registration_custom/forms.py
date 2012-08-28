from django import forms
from registration.forms import RegistrationFormUniqueEmail
from django.utils.translation import ugettext_lazy as _
from registration_custom.models import OdfwRegistrationProfile

# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = { 'class': 'required' }

class RegistrationFormFull(RegistrationFormUniqueEmail):

    username = forms.RegexField(regex=r'^\w+$',
        max_length=30,
        widget=forms.TextInput(attrs=attrs_dict),
        label=_(u'username'),
        error_messages= {
            'invalid': _(u'Username cannot contain spaces or special characters.'),
        }
    )    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_(u'password'),
        error_messages= {
            'required': _(u'Please enter a password.'),
        }
    )
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_(u'password (again)'),
        error_messages= {
            'required': _(u'Please confirm your password.'),
        }
    )

    def clean(self):
        
        data = self.cleaned_data
        if data.has_key('password1'):
            pwd1 = self.cleaned_data['password1']
        else:
            pwd1 = None
        if data.has_key('password2'):
            pwd2 = self.cleaned_data['password2']
        else:
            pwd2 = None
        
        if pwd1 and pwd2 and pwd1 != pwd2:
            msg = u"Passwords must be the same, including capitalization."
            self._errors['password1'] = forms.util.ErrorList([msg])
            
            # These fields are no longer valid. Remove them from the cleaned data
            del self.cleaned_data['password1']
            del self.cleaned_data['password2']
            
        return data
    
    def save(self, profile_callback=None):
        """
        Create the new ``User``, ``RegistrationProfile``, 
        ``UserProfile`` and returns the ``User``.
        
        This is essentially a light wrapper around
        ``RegistrationProfile.objects.create_inactive_user()``,
        feeding it the form data and a profile callback (see the
        documentation on ``create_inactive_user()`` for details) if
        supplied.
        
        This overrides the default RegistrationForm.save and adds
        the additional info we collected including their first and
        last name and also their profile information   
        """        
        new_user = OdfwRegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'],
                                                                    profile_callback=profile_callback)
        new_user.save()        
        return new_user