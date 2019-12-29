from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import markdown
from django.utils.html import strip_tags

# Create your models here.
class Category(models.Model):
    """
    django要求模型必须继承models.Model类
    Category只需要一个简单的分类名name就可以了
    CharField指定了分类名name的数据类型，CharField是字符型
    CharField的max_length参数指定其最大长度，超过这个长度的分类名就不能被存入数据库
    当然django还为我们提供了多种其它的数据类型，如日期时间类型DateTimeField、整数类型IntegerField等等
    django内置的全部类型可查看文档：
    https://docs.djangoproject.com/en/2.2/ref/models/fields/#field-types
    """
    name = models.CharField(max_length=100)

    class Meta:
    	verbose_name = '分类'
    	verbose_name_plural = verbose_name
    def __str__(self):
        return self.name

class Tag(models.Model):
    """
    标签Tag也比较简单，和Category一样
    再次强调一定要继承models.Model类
    """
    name = models.CharField(max_length=100)

    class Meta:
    	verbose_name = '标签'
    	verbose_name_plural = verbose_name
    def __str__(self):
        return self.name

class Post(models.Model):
    """
    文章的数据库表稍微复杂一点，主要是涉及的字段更多
    """
    #文章标题
    title = models.CharField('标题', max_length=70)

    #文章正文，使用了TextField
    #存储比较短的字符串可以使用CharField，但对于文章的正文来说可能会是一大段文本，因此使用TextField来存储大段文本
    body = models.TextField('正文')

    #这两个列分别表示文章的创建时间和最后一次的修改时间，存储时间的字段用DateTimeFidld类型
    created_time = models.DateTimeField('创建时间',default=timezone.now)
    modified_time = models.DateTimeField('修改时间')

    #文章摘要，可以没有文章摘要，但默认情况下CharField要求我们必须存入数据，否则就会报错
    #指定CharField的blank=True参数值后就可以允许空值了
    excerpt = models.CharField('摘要', max_length=200, blank=True)

    #这是分类与标签，分类与标签的模型已经定义在上面
    #在这里把文章对应的数据库表和分类、标签对应的数据库关联了起来，但是关联形式稍微有点不同
    #规定一篇文章只能对应一个分类，但是一个分类下可以有多篇文章，所以使用的是ForeignKey，即一
    #对多的关联关系。且django2.0以后，ForeignKey必须传入一个on_delete参数用来指定当关联的数据
    #被删除时，被关联的数据的行为，这里假定当某个分来被删除时，该分类下全部文章也同时被删除，因此  #使用models。CASCADE参数，
    #意为级联删除，而对于标签来说，一篇文章可以有多个标签，同一个标签下也可能有多篇文章，所以使用
    #ManyToManyField，表明这是多对多的关联联系
    #同时规定文章可以没有标签，因此为标签tags指定了blank = True
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)

    #文章作者，这里User是从django。contrib。auth。models导入的
    #django.contrib.auth是django内置的应用，专门用于处理网站用户的注册、登录等流程，User是
    #django为我们已经写好的用户模型
    #这里通过ForeignKey把文章和User关联了起来
    #因为规定一篇文章只能有一个作者，而一个作者可能会写多篇文章，因此这是一对多的关联关系，和
    #Category类似
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)

    class Meta:
    	verbose_name = '文章'
    	verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    #自定义 get_absolute_url 方法
    #记得从 django.urls 中导入 reverse 函数
    def get_absolute_url(self):
    	return reverse('blog:detail', kwargs={'pk':self.pk})

    def save(self, *args, **kwargs):
    	self.modified_time = timezone.now()

    	#首先实例化一个Markdown类，用于渲染body文本，
    	#由于摘要并不需要生成文章目录，所以去掉了目录拓展，
    	md = markdown.Markdown(extensions=[
    			'markdown.extensions.extra',
    			'markdown.extensions.codehilite',
    		])

    	#先将Markdown文本渲染成HTML文本
    	#strip_tags去掉HTML文本的全部HTML标签
    	#从文本摘取前54个字符赋给excerpt
    	self.excerpt = strip_tags(md.convert(self.body))[:54]

    	super().save(*args, **kwargs)
    	



