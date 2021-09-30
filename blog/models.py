from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.db import models
from os.path import splitext
from django.urls import reverse
from django.conf import settings
from extensions.converter import convert_to_jalali
from extensions.bot_send_to_channel import send_to_channel
from markdownx.models import MarkdownxField

User = settings.AUTH_USER_MODEL

COLOR_CHOICES = (
    ("danger", "قرمز"),
    ("primary", "آبی"),
    ("warning", "زرد"),
    ("success", "سبز"),
    ("dark", "تیره"),
)
STATUS = (
    ('d', 'پیش نویس'),
    ('p', 'منتشر شده'),
    ('i', 'در انتظار'),
    ('b', 'برگشت داده شده'),
)


def upload_images(instance, filename):
    return "articles/{}/%Y/%m/%d/{}".format(instance.author.username, filename)


def upload_video_validator(value):
    valid_extension = ['.wav', '.mp4', '.avi', '.mkv']
    ext = splitext(value)[1]
    if ext.lower() not in valid_extension:
        raise ValidationError("فرمت فایل پشتیبانی نمیشود!")


# Create your models here.
class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="liked_posts")
    post = models.ForeignKey('Article', on_delete=models.CASCADE, related_name="likes")

    def __str__(self) -> str:
        return "%s liked %s" % (self.user.username, self.post.title)

    def liker(self):
        return self.user.username


class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='child', verbose_name="دسته بالاتر")
    title = models.CharField(max_length=30, verbose_name="عنوان")
    slug = models.SlugField(max_length=30, unique=True, verbose_name="اسلاگ")
    color = models.CharField(max_length=100, choices=COLOR_CHOICES)
    desc = models.TextField(max_length=300, verbose_name="توضیحات", null=True, blank=True)
    date_cr = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ انتشار")
    date_up = models.DateTimeField(auto_now=True, verbose_name="تاریخ ویرایش")

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse('blog:article-related-category', kwargs={'slug':self.slug})

    def get_parents(self):
        full_path = [self.title]                  
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' -> '.join(full_path[::-1])

    def jdate_cr(self):
        return convert_to_jalali(self.date_cr)

    def jdate_up(self):
        return convert_to_jalali(self.date_up)


class ViewsMid(models.Model):
    ip_addr = models.GenericIPAddressField()
    ua = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip_addr
    
    def jdate(self):
        return convert_to_jalali(self.date)

class ArticleHit(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    ip_address = models.ForeignKey(ViewsMid, on_delete=models.CASCADE)
    date_cr = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article.title

    def jdate_cr(self):
        return convert_to_jalali(self.date_cr)


class Article(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان مقاله")
    slug = models.SlugField(max_length=30, unique=True, verbose_name="اسلاگ مقاله")
    image = models.ImageField(upload_to=upload_images, verbose_name="تصویر مقاله")
    video = models.FileField(upload_to=upload_images, validators=[upload_video_validator], null=True, blank=True,
                             verbose_name='ویدئو مقاله',
                             help_text="""توجه داشته باشید که شما فقط میتونید یک محتوای ویدئویی یا محتوای
                              تصویری برای مقاله اتون آپلود کنید، بنابراین اگر فقط محتوای ویدئویی برای اپلود
                              نیاز دارید؛ تصویری که برایش انتخاب میکنید به عنوان آن پستر نمایش داده میشود""")
    text = MarkdownxField(verbose_name="متن مقاله",max_length=15000)
    category = models.ManyToManyField(Category, verbose_name="دسته بندی مقاله")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=" نویسنده مقاله")
    login_required = models.BooleanField(default=False, verbose_name="ثبت نام الزامی",
                                         help_text="اگر این گزینه فعال باشد کاربر باید ثبت نام کند تا پست شما را ببیند")
    date_cr = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ نوشته شدن مقاله")
    date_up = models.DateTimeField(auto_now=True, verbose_name="تاریخ ویرایش مقاله")
    published = models.CharField(choices=STATUS, max_length=10, verbose_name="وضعیت انتشار مقاله")
    hits = models.ManyToManyField(ViewsMid, through=ArticleHit, related_name='hits',
                                  blank=True, verbose_name="تعداد بازدیدهای مقاله")
    back_description = models.TextField(max_length=300, null=True,
                                        blank=True, verbose_name="دلایل برگشت داده شدن مقاله",
                                        help_text="این بخش توسط ادمین نوشته میشود اگر پست شما دارای مشکلاتی باشد")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})

    def get_categories(self):
        l1 = []
        l2 = []
        l3 = []
        l4 = []
        l5 = []
        for i in self.category.all():
            l1.append(i.title)
            if i.child.all():
                l2.append(i.title)
                for i in i.child.all():
                    l3.append(i.title)
                    if i.child.all():
                        l4.append(i.title)
                        for i in i.child.all():
                            l5.append(i.title)
        if l1:
            return "".join(l1)
        elif l1 and l2:
            return "{}>{}".format("".join(l1), "".join(l2))
        elif l1 and l2 and l3:
            return "{}>{}>{}".format("".join(l1), "".join(l2), "".join(l3))
        elif l1 and l2 and l3 and l4:
            return "{}>{}>{}".format("".join(l1), "".join(l2), "".join(l3), "".join(l4))
        elif l1 and l2 and l3 and l4 and l5:
            return "{}>{}>{}".format("".join(l1), "".join(l2), "".join(l3), "".join(l4), "".join(l5))

    def get_author(self):
        return self.author.username

    def image_tag(self):
        if self.image and self.video:
            return format_html(u"<video height='60' controls poster='{}'><source src='{}'></video>".format(
                self.image.url, self.video.url))
        elif self.image:
            return format_html("<img src={} height='60'>".format(self.image.url))

    def jdate_cr(self):
        return convert_to_jalali(self.date_cr)

    def jdate_up(self):
        return convert_to_jalali(self.date_up)

    def send_to_channel_f(self):
        if self.published == 'p':
            return send_to_channel(self.title, self.image.url, self.text, self.get_absolute_url())


class Comment(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="از طرف")
    to_article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name="به مقاله", related_name="comments")
    title = models.CharField(max_length=50, verbose_name="عنوان")
    text = models.TextField(max_length=500, verbose_name="متن")
    published = models.BooleanField(default=False, verbose_name="منتشر شده")
    date_cr = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ انتشار")
    backed_description = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self) -> str:
        return self.title

    def jdate_cr(self):
        return convert_to_jalali(self.date_cr)
