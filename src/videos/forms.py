from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from comments.models import Comment


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            "placeholder": "Your comment or reply."}
        )
    )

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.layout.append(Submit('submit', 'Add comment/Reply'))

    class Meta:
        model = Comment
        fields = ("text",)
