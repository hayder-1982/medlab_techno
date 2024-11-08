from django.contrib import admin

from .models import BlogModel, CommentModel, LikeModel, Patient, Test,ResultModel

admin.site.register(BlogModel)
admin.site.register(CommentModel)
admin.site.register(LikeModel)
admin.site.register(Patient)
admin.site.register(Test)
admin.site.register(ResultModel)