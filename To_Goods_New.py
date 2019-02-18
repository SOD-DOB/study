import re
import xlrd,xlwt
from openpyxl import Workbook
import pymysql.cursors
import numpy as np
import pandas as pd

# 连接MYSQL
sql = pymysql.connect (
    host='rm-2zehi2ns25kee8568o.mysql.rds.aliyuncs.com',
    port=3306,
    user='fwread',
    password='Finewest1127',
    db='finewest'
)
cursor = sql.cursor ()

# 获取原文件
while True:
    try:
        old_name = input ('please input Pre-cleanup filename:')
        old_url = 'C:/Users/SOD/Desktop/' + old_name + '.xlsx'
        data = xlrd.open_workbook(old_url)
        sheet_names = data.sheet_names()
        break
    except FileNotFoundError:
        print('Without this file, try again!')
        continue

# 新建文件
new_sheet = Workbook()
new_name = input('please input Cleaned filename:')
new_url = 'C:/Users/SOD/Desktop/'+ new_name +'.xlsx'
new_sheet.save(new_url)
new_excel = pd.ExcelWriter(new_url)

for sheetname in sheet_names:

    # 子产区
    sql_sub = "SELECT shopping_application.pid, shopping_application.egName, shopping_application.EGnation, shopping_application.grade,shopping_application.Continent, shopping_application.seq from shopping_application where pid in( select id from shopping_application where (egname= '" + sheetname + "' or egnation= '" + sheetname + "')and pid is null)"
    cursor.execute (sql_sub)
    zichanqu = pd.DataFrame (list (cursor.fetchall ()),
                             columns=['pid', 'egName', 'EGnation', 'grand', 'Continent', 'seq'])
    # 大产区
    sql_nation = "SELECT shopping_application.pid, shopping_application.egName, shopping_application.EGnation, shopping_application.grade,shopping_application.Continent, shopping_application.seq from shopping_application where EGnation = '" + sheetname + "' AND pid is NULL"
    cursor.execute (sql_nation)
    dachanqu = pd.DataFrame (list (cursor.fetchall ()),
                             columns=['pid', 'egName', 'EGnation', 'grand', 'Continent', 'seq'])
    # 规范写法
    sql_nation = "SELECT  b.egname,a.`value`,b.nation   from shopping_dictionary_valuelist a,shopping_application b where a.type=5  and a.`key`= b.egname and b.egnation = (SELECT EGnation FROM shopping_application WHERE egName = '" + sheetname + "' and ISNULL(pid))"
    cursor.execute (sql_nation)
    guifan = pd.DataFrame (list (cursor.fetchall ()), columns=['egname', 'value', 'EGnation'])

    exl = pd.read_excel (old_url, sheet_name = sheetname)


    # 筛选数值的正则
    def re_num(x):
        return re.findall (r'[0-9]+|[a-z]+', str (x))

    # 规格中的数值提取
    def vol():
        vol = []
        for x in exl['单位Unit']:
            z = re_num (x)[0]
            vol.append (z)
        #    print(vol)
        return vol

    # 酒名中查找颜色
    def color():
        hongse = [' Red', ' Rouge']
        baise = [' White', ' Blanc']
        meihong = [' Rose']
        name_color = []
        for jiuming, yanse in zip(exl['名字Name'], exl['颜色Color']):
            x = ''
            if yanse in ['Red', 'White', 'Rose']:
                x = yanse
            else:
                for hs in hongse:
                    if jiuming.replace ('-', ' ').find (hs) >= 0:
                        x = 'Red'
                for bs in baise:
                    if jiuming.replace ('-', ' ').find (bs) >= 0:
                        x = 'White'
                for mh in meihong:
                    if jiuming.replace ('-', ' ').find (mh) >= 0:
                        x = 'Rose'
            if len(x) > 0:
                name_color.append(x)
            else:
                name_color.append('')
        return name_color

    # 酒名中搜索小产区
    def cq_sub():
        exl_cq_sub = []
        for y, cq in zip(exl['名字Name'],exl['产区Appellation']):
            x_max = ''
            z_max = ''
            m_max = ''
            # 搜索子产区
            for x in zichanqu['egName']:
                if y.replace ('-', ' ').find (x.replace ('-', ' ')) >= 0:
                    if len (x_max) < len (x):
                        x_max = x
            # 搜索大产区
            for z in dachanqu['egName']:
                if y.replace ('-', ' ').find (z.replace ('-', ' ')) >= 0:
                    if len (z_max) < len (z):
                        z_max = z
            # 搜索规范写法
            for n, m in zip (guifan['value'], guifan['egname']):
                if y.replace ('-', ' ').find (n.replace ('-', ' ')) >= 0:
                    m_max = m

            if len (x_max) > 0:
                exl_cq_sub.append (x_max)
            elif len (x_max) <= 0 and len (z_max) > 0:
                exl_cq_sub.append (z_max)
            elif len (x_max) <= 0 and len (z_max) <= 0 and len (m_max) > 0:
                exl_cq_sub.append (m_max)
            else:
                exl_cq_sub.append (cq)
        return exl_cq_sub


    # 拆分库存
    def kucun():
        num = []
        zhonglei = []
        for x in exl['数量Qty']:
            try:
                a = re_num (x)[0]
                b = re_num (x)[1]
                num.append (a)
                zhonglei.append (b)
            except IndexError:
                num.append ('')
                zhonglei.append ('')
        return num, zhonglei


    # 拆分包装
    def pack():
        pingshu = []
        for x in exl['包装Packing']:
            try:
                a = re_num (x)[1]
                pingshu.append (a)
            except IndexError:
                pingshu.append ('')
        return pingshu

        # 计算单瓶价格和瓶装库存


    def jiage():
        price = []
        btl_num = []
        for x, y, z, g in zip (kucun ()[1], exl['价格Price'], pack (), kucun ()[0]):
            if x in ('case', 'cs', 'cases', 'GiftBox', 'giftbox', 'Gift Box', 'giftbox'):
                try:
                    a = y / int (z)
                    b = int (g) * int (z)
                    price.append (a)
                    btl_num.append (str (b))
                except ValueError:
                    price = price
                    btl_num = btl_num
            else:
                price.append (y)
                btl_num.append (g)
        return price, btl_num


    # 加入新维度至DataFrame
    def vint():
        # 删除列
        new_exl = exl.drop (['单位Unit', '颜色Color', '产区Appellation', '价格Price', '数量Qty'], axis=1)
        # 容量
        new_exl.insert (3, 'Vol', pd.DataFrame (vol ()))
        # 颜色
        new_exl.insert (4, 'Color', pd.DataFrame (color()))
        # 小产区
        new_exl.insert (6, 'Appellation', pd.DataFrame (cq_sub ()))
        # 单瓶价格
        new_exl.insert (10, 'Price', pd.DataFrame (jiage ()[0]))
        # 瓶装库存
        new_exl.insert (11, 'Qty', pd.DataFrame (jiage ()[1]))

        return new_exl


    if __name__ == '__main__':
        # print(vint().head())
        vint ()
    vint ().to_excel (excel_writer=new_excel, sheet_name=sheetname, index=False)

new_excel.save ()
new_excel.close ()
print (' *** 清理完成！！！*** ')