from django import forms
from django.forms import widgets


class CheckoutForm(forms.Form):

    city = forms.CharField(required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': '1234 Main st'
        }
    ))
    province = forms.CharField(required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Provinsi'
        }
    ))
    address = forms.CharField(required=False, widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'placeholder': 'Jalan Tanjung Barat RT/RW 09/12'
        }
    ))

    zipcode = forms.CharField(required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': '17178'
        }
    ))
    use_default_address = forms.BooleanField(required=False)
    set_default_address = forms.BooleanField(required=False)


class CouponForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Promo Code",
                "aria-label": "Recipient's username",
                "aria-describedby": "basic-addon2",
            }
        )
    )

class RefundForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 4,
            }
        )
    )