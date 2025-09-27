from django.contrib import admin
from .models import Student, Document, Skill, StudentSkill, GovtJob, Scholarship

# Register your models here to make them accessible in the admin panel.

admin.site.register(Student)
admin.site.register(Document)
admin.site.register(Skill)
admin.site.register(StudentSkill)
admin.site.register(GovtJob)
admin.site.register(Scholarship)