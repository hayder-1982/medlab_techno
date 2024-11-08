from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
#pip install python-barcode
import barcode
from barcode.writer import ImageWriter
from io import BytesIO 
#pip install arabic-reshaper
import arabic_reshaper
#pip install python-bidi
from bidi.algorithm import get_display
from django.core.files import File
import random
import datetime 


class Test(models.Model):
    ACTIVE_CHOICES = [
        ('1', '1'),
        ('0', '0'),
    ]
    SampleTest = [
        ('EDTA', 'EDTA'),
        ('Serum', 'Serum'),
        ('Plasma sodium citrate ', 'Plasma sodium citrate'),
        ('CSF fluid', 'CSF fluid'),
        ('Urine', 'Urine'),
        ('Stool', 'Stool'),
    ]
    CategoryTest = [
        ('Hematology', 'Hematology'),
        ('Chemistry', 'Chemistry'),
        ('bacteriology', 'bacteriology'),
        ('Imuntology', 'Imuntology'),
        ('parasitology', 'parasitology'),
    ]
    apprvname = models.CharField(max_length=100)
    fullname = models.CharField(max_length=100)
    testSingle = models.BooleanField(default=False)
    unit = models.CharField(max_length=100,blank=True, null=True)
    category =models.CharField(max_length=100, choices=CategoryTest) #Hematology , Chemistry , Imuntology
    categorySpecific = models.CharField(max_length=100,blank=True, null=True) # in chiled null else parant full
    sample =models.CharField(max_length=100, choices=SampleTest) 
    parent = models.CharField(max_length=10, choices=ACTIVE_CHOICES) # if 1 this parant get categorySpecific  else 0 this chiled
    price = models.FloatField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    active = models.CharField(max_length=10, choices=ACTIVE_CHOICES)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.fullname
    




class Patient(models.Model):
    age_chioce = [
        ('year', 'year'),
        ('month', 'month'),
        ('day', 'day'),
    ]
    sex_chioce = [
        ('Male', 'Male'),
        ('Famle', 'Famle'),
    ]
    name = models.CharField(db_column='name', max_length=300, blank=True, null=True)
    age = models.IntegerField(db_column='age',  blank=True, null=True)
    uage = models.CharField(db_column='uage',max_length=100 , choices=age_chioce )
    sex = models.CharField(db_column='sex', max_length=300, choices=sex_chioce)
    drname = models.CharField(db_column='drname', max_length=300,  blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    imgBarcode = models.ImageField(upload_to='uploads/barcode/', blank = True)
    idBarcode =  models.CharField(max_length=20, blank=True ,unique=True)  # To store the random number as a string
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    views = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('home')
    
    def generate_random_number(self):
        # Get the current date and time
        current_date = datetime.datetime.now()
        
        # Generate a random number using the current date
        #date_str = current_date.strftime('%Y%m%d%H%M%S')  # Format date as a string (e.g., YYYYMMDDHHMMSS)

        # Extract the last 2 digits of the year (e.g., 24 from 2024) and combine it with the day and month
        date_str = current_date.strftime('%m%d')  # Day and hour (e.g., 1312 for the 13th day, 12th hour)
        print('date_str',date_str)
        random_part = str(random.randint(1000, 9999))  # Generate a random 4-digit number
        print('random_part',random_part)
        # Combine the date string with the random number
        return date_str + random_part
    
    # cre Barcodeat
        # ['code128', 'code39', 'ean', 'ean13', 'ean14', 'ean8', 'gs1', 'gs1_128', 'gtin', 'isbn', 'isbn10', 'isbn13', 'issn', 'itf', 'jan', 'pzn', 'upc', 'upca']
    def save(self, *args, **kwargs):
        if not self.idBarcode:
            self.idBarcode = self.generate_random_number()
        
            # EAN = barcode.get_barcode_class('ean13')
            EAN = barcode.get_barcode_class('code128')

            # ean = EAN(f'{self.country_id}{self.manufacturer_id}{self.number_id}', 
            #     writer=ImageWriter())
            # buffer = BytesIO()
            ean =EAN(str(self.idBarcode), writer=ImageWriter())
            buffer = BytesIO()
            # ean.write(buffer)
            ean.write(buffer, text=get_display(arabic_reshaper.reshape(self.name))+'\n'+str(self.idBarcode)+'\n'+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                        options={ 'module_height': 9, 'font_size':5,'text_distance': 2,})
            # options={'module_width':  0.1, 'module_height': 3, 'font_size':2, 'text_distance': 0.8,
            #                 'quiet_zone': 1, 'write_text': True}
            self.imgBarcode.save('barcode.png', File(buffer), save=False)
        return super().save(*args, **kwargs)


class ResultModel(models.Model):
    blog = models.ForeignKey(Patient,to_field='idBarcode', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    test = models.ForeignKey(Test, on_delete=models.PROTECT)
    #patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    #test = models.CharField(max_length=255, blank=True, null=True)
    result = models.CharField(max_length=255, blank=True, null=True)  # Field to store test result
    #unit = models.CharField(max_length=100,blank=True, null=True)
    autherresult = models.CharField(max_length=100,blank=True, null=True)
    categorySpecific = models.CharField(max_length=100,blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    #normalvalue = models.TextField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f'{self.blog.name} - {self.test}'
    


class CBCModel(models.Model):
    idBarcode = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    WBC = models.CharField(max_length=100, blank=True, null=True)
    GRN = models.CharField(max_length=100, blank=True, null=True)
    LYM = models.CharField(max_length=100, blank=True, null=True)
    MID = models.CharField(max_length=100, blank=True, null=True)
    GRN_per = models.CharField(max_length=100, blank=True, null=True)
    LYM_per = models.CharField(max_length=100, blank=True, null=True)
    MID_per = models.CharField(max_length=100, blank=True, null=True)
    RBC = models.CharField(max_length=100, blank=True, null=True)
    HGB = models.CharField(max_length=100, blank=True, null=True)
    HCT = models.CharField(max_length=100, blank=True, null=True)
    MCV = models.CharField(max_length=100, blank=True, null=True)
    MCH = models.CharField(max_length=100, blank=True, null=True)
    MCHC = models.CharField(max_length=100, blank=True, null=True)
    PLT = models.CharField(max_length=100, blank=True, null=True)
    MPV = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.idBarcode}'







class BlogModel(models.Model):
    title = models.CharField(max_length=200, unique=True)
    content = models.TextField()
    media = models.ImageField(upload_to='blog_media/', blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('home')


class CommentModel(models.Model):
    blog = models.ForeignKey(Patient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog.name}"


class LikeModel(models.Model):
    blog = models.ForeignKey(Patient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} liked {self.blog.name}"
