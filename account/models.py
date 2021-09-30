from blog.models import Category, upload_images
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.html import format_html
from extensions.converter import convert_to_jalali

CONTACT_CHOICES = (
    ('github', 'گیتهاب'),
    ('linkedin', 'لینکدین'),
    ('gmail', 'جیمیل'),
    ('telegram', 'تلگرام'),
    ('instagram', 'اینستاگرام'),
    ('yahoo', 'یاهو'),
    ('other', 'غیره'),
)


def uploaded_images(instance, filename):
    return "user/%s/profile/%s" % (instance.username, filename)


class UserProfile(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="ایمیل")
    profile_pic = models.ImageField(upload_to=uploaded_images, verbose_name="تصویر پروفایل")
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name="شماره تلفن")
    about = models.TextField(max_length=600, verbose_name="درباره")
    short_about = models.CharField(max_length=150, verbose_name="درباره کوتاه")
    is_author = models.BooleanField(default=False, verbose_name="نویسنده")
    can_send_message = models.BooleanField(default=True, verbose_name="توانایی ارسال پیام")

    def get_absolute_url(self):
        return reverse('blog:author', kwargs={'slug': self.username})

    def get_user_contacts(self):
        tl = []
        for i in self.contactsuser_set.all():
            tl.append(i.title + ":" + i.url)
        
        return ", ".join(tl)
    
    def image_tag(self):
        if self.profile_pic:
            return format_html(u"<img src='{}' alt='{}' height='60'>".format(self.profile_pic.url, self.username))
        else:
            return "User does not have any photo"


class ContactsUser(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="کاربر")
    title = models.CharField(max_length=20, choices=CONTACT_CHOICES, verbose_name="عنوان")
    url = models.URLField(max_length=100, verbose_name="آدرس URL")
    date_cr = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ساخت")
    date_up = models.DateTimeField(auto_now=True, verbose_name="تاریخ اپدیت")

    def __str__(self):
        return self.title

    def jdate_cr(self):
        return convert_to_jalali(self.date_cr)

    def jdate_up(self):
        return convert_to_jalali(self.date_up)


class NotificationAdminCenter(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان")
    text = models.TextField(max_length=300, verbose_name="متن")
    read = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ")
    expr_date = models.DateTimeField(verbose_name="تاریخ انقضا")

    def __str__(self):
        return self.title

    def jdate(self):
        return convert_to_jalali(self.date)

    def jexpr_date(self):
        return convert_to_jalali(self.expr_date)


class Message(models.Model):
    to_user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="reciever")
    from_user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="sender")
    title = models.CharField(max_length=50)
    text = models.TextField(max_length=600)
    read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("account:message-detail", kwargs={'pk': self.pk})

    def jdate(self):
        return convert_to_jalali(self.date)


class ChallengeEvent(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")
    slug = models.SlugField(max_length=30, unique=True, verbose_name="اسلاگ")
    info = models.TextField(max_length=11000, verbose_name="توضیحات چالش")
    image = models.ImageField(upload_to=upload_images, null=True, blank=True, verbose_name="تصویر")
    author = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, verbose_name="نویسنده")
    date_c = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ انتشار")
    date_u = models.DateTimeField(auto_now=True, verbose_name="تاریخ اپدیت")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="دسته بندی")
    expr_date = models.DateTimeField(verbose_name="تاریخ انقضا")

    def image_tag(self):
        if self.image:
            return format_html(u"<img src={} height='60'>".format(self.image.url))

    def get_category(self):
        x = []
        for i in self.category.all():
            x.append(i.title)
        return ", ".join(x)

    def get_absolute_url(self):
        return reverse('blog:challenge', kwargs={'slug': self.slug})

    def get_author(self):
        return self.author.user

    def del_obj_after_expr_date(self):
        if self.expr_date < timezone.now():
            self.delete()
        else:
            return "{}".format(self.expr_date - timezone.now())

    def jdate_c(self):
        return convert_to_jalali(self.date_c)

    def jdate_u(self):
        return convert_to_jalali(self.date_u)

    def jexpr_date(self):
        return convert_to_jalali(self.expr_date)
