# coding: utf-8

province_list = u'''
台湾
广东
江苏
北京
辽宁
浙江
上海
山东
黑龙江
陕西
山西
贵州
云南
安徽
福建
江西
甘肃
香港
广西
内蒙古
天津
河南
湖北
重庆
海南
湖南
四川
河北
西藏
青海
吉林
澳门
新疆
宁夏
南海诸岛
'''.split('\n')[1: -1]

default_province_data = {
    province: 1 for province in province_list
}
