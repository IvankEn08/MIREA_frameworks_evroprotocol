from django.db import models


class Accident(models.Model):
    STATUS_NEW = "new"
    STATUS_PROCESSING = "processing"
    STATUS_CLOSED = "closed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_NEW, "Новое"),
        (STATUS_PROCESSING, "В обработке"),
        (STATUS_CLOSED, "Закрыто"),
        (STATUS_CANCELLED, "Отменено"),
    ]

    id = models.AutoField(primary_key=True)
    location = models.CharField("Место происшествия", max_length=255)
    occurred_at = models.DateTimeField("Дата и время")
    has_injured = models.BooleanField("Есть пострадавшие", default=False)
    has_fire = models.BooleanField("Есть возгорание", default=False)
    status = models.CharField(
        "Состояние обработки", max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW
    )

    class Meta:
        db_table = "accidents"
        managed = False
        verbose_name = "ДТП"
        verbose_name_plural = "ДТП"
        ordering = ["-occurred_at", "-id"]

    @property
    def emergency_required(self):
        return self.has_injured or self.has_fire

    @property
    def category(self):
        return "Повышенная опасность" if self.emergency_required else "Без пострадавших"

    def __str__(self):
        return f"ДТП №{self.pk}: {self.location}"


class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    plate_number = models.CharField("Государственный номер", max_length=20, unique=True)
    brand = models.CharField("Марка", max_length=80)
    model = models.CharField("Модель", max_length=80)

    class Meta:
        db_table = "vehicles"
        managed = False
        verbose_name = "Транспортное средство"
        verbose_name_plural = "Транспортные средства"
        ordering = ["brand", "model"]

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"


class Participant(models.Model):
    id = models.AutoField(primary_key=True)
    accident = models.ForeignKey(
        Accident,
        on_delete=models.CASCADE,
        db_column="accident_id",
        related_name="participants",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        db_column="vehicle_id",
        related_name="participants",
    )
    full_name = models.CharField("ФИО", max_length=160)
    phone = models.CharField("Телефон", max_length=30)

    class Meta:
        db_table = "participants"
        managed = False
        verbose_name = "Участник ДТП"
        verbose_name_plural = "Участники ДТП"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} — ДТП №{self.accident_id}"


class EmergencyMessage(models.Model):
    id = models.AutoField(primary_key=True)
    accident = models.ForeignKey(
        Accident,
        on_delete=models.CASCADE,
        db_column="accident_id",
        related_name="messages",
    )
    service_name = models.CharField("Служба", max_length=100)
    sent_at = models.DateTimeField("Время отправки")
    status = models.CharField("Состояние доставки", max_length=30)

    class Meta:
        db_table = "emergency_messages"
        managed = False
        verbose_name = "Оповещение службы"
        verbose_name_plural = "Оповещения служб"
        ordering = ["sent_at", "id"]

    def __str__(self):
        return f"{self.service_name} — ДТП №{self.accident_id}"


class AccidentPhoto(models.Model):
    accident = models.ForeignKey(
        Accident, on_delete=models.CASCADE, related_name="photos", verbose_name="ДТП"
    )
    image = models.ImageField(
        "Фотография места ДТП", upload_to="accidents/%Y/%m/", blank=True
    )
    caption = models.CharField("Описание", max_length=160, blank=True)
    uploaded_at = models.DateTimeField("Загружено", auto_now_add=True)

    class Meta:
        verbose_name = "Фотография ДТП"
        verbose_name_plural = "Фотографии ДТП"
        ordering = ["uploaded_at", "id"]

    def __str__(self):
        return self.caption or f"Фотография ДТП №{self.accident_id}"
