from django import forms
from django.utils import timezone

from .models import Accident, AccidentPhoto, Vehicle


class AccidentFilterForm(forms.Form):
    SEVERITY_CHOICES = [
        ("", "Все происшествия"),
        ("emergency", "Повышенная опасность"),
        ("regular", "Без пострадавших и возгорания"),
        ("injured", "Есть пострадавшие"),
        ("fire", "Есть возгорание"),
    ]

    severity = forms.ChoiceField(
        label="Категория",
        choices=SEVERITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    location = forms.CharField(
        label="Адрес или ориентир",
        required=False,
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Например, улица"}
        ),
    )
    status = forms.ChoiceField(
        label="Состояние обработки",
        required=False,
        choices=[("", "Любое состояние"), *Accident.STATUS_CHOICES],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean_location(self):
        return self.cleaned_data["location"].strip()


class AccidentForm(forms.ModelForm):
    class Meta:
        model = Accident
        fields = ["location", "occurred_at", "has_injured", "has_fire"]
        labels = {
            "location": "Адрес или точное место происшествия",
            "occurred_at": "Дата и время ДТП",
            "has_injured": "Есть пострадавшие",
            "has_fire": "Есть возгорание",
        }
        help_texts = {"location": "Укажите населённый пункт, улицу и ориентир."}
        widgets = {
            "location": forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "street-address"}
            ),
            "occurred_at": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "has_injured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "has_fire": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_occurred_at(self):
        occurred_at = self.cleaned_data["occurred_at"]
        if occurred_at > timezone.localtime():
            raise forms.ValidationError(
                "Дата и время происшествия не могут быть в будущем."
            )
        return occurred_at

    def clean_location(self):
        location = " ".join(self.cleaned_data["location"].split())
        if len(location) < 5:
            raise forms.ValidationError("Уточните место происшествия.")
        return location


class ParticipantEntryForm(forms.Form):
    full_name = forms.CharField(
        label="ФИО участника", max_length=160,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "name"}),
    )
    phone = forms.CharField(
        label="Телефон", max_length=30,
        widget=forms.TextInput(
            attrs={"class": "form-control", "type": "tel", "autocomplete": "tel"}
        ),
    )
    plate_number = forms.CharField(
        label="Государственный номер", max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "А123АА 77"}
        ),
    )
    brand = forms.CharField(
        label="Марка", max_length=80,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    vehicle_model = forms.CharField(
        label="Модель автомобиля", max_length=80,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean_full_name(self):
        return " ".join(self.cleaned_data["full_name"].split())

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = "".join(character for character in phone if character.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError("Укажите телефон не менее чем из 10 цифр.")
        return phone

    def clean_plate_number(self):
        return " ".join(self.cleaned_data["plate_number"].upper().split())

    def clean(self):
        cleaned_data = super().clean()
        plate_number = cleaned_data.get("plate_number")
        brand = cleaned_data.get("brand")
        vehicle_model = cleaned_data.get("vehicle_model")
        if plate_number and brand and vehicle_model:
            existing = Vehicle.objects.filter(plate_number__iexact=plate_number).first()
            if existing and (existing.brand.lower(), existing.model.lower()) != (
                brand.strip().lower(), vehicle_model.strip().lower()
            ):
                raise forms.ValidationError(
                    "Для указанного государственного номера уже зарегистрировано "
                    "другое ТС."
                )
        return cleaned_data


class AccidentPhotoForm(forms.ModelForm):
    class Meta:
        model = AccidentPhoto
        fields = ["image", "caption"]
        widgets = {
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "caption": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and image.size > 8 * 1024 * 1024:
            raise forms.ValidationError("Размер изображения не должен превышать 8 МБ.")
        return image
