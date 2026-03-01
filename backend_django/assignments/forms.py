from django import forms


class SubmissionForm(forms.Form):
    text = forms.CharField(required=False, strip=True)
    link = forms.URLField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        text = (cleaned_data.get("text") or "").strip()
        link = (cleaned_data.get("link") or "").strip()

        if not text and not link:
            raise forms.ValidationError("Заполните текст решения или укажите ссылку.")

        return cleaned_data
