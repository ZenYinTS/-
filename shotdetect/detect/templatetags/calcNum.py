from django import template

register = template.Library() #以上两行代码是获取到Django模板所有tags和filter的library，以便我们写入一个新的方法

def calcNum(value,arg):   #自定义方法，获取当前记录的序号

    return value + (arg - 1) * 5

register.filter('calcNum', calcNum) #将此方法添加到模板中