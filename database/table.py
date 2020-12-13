#coding=utf8
import xlrd
import xlwt
import json
import sys
import os.path as path
reload(sys)
sys.setdefaultencoding('utf8')

class Table:
    def __init__(self, table, row_num, col_num):
        self.table = table
        self.row_num = row_num
        self.col_num = col_num
        self.shape=[self.row_num, self.col_num]

    def __getitem__(self, i):
        return self.table[i]

    def getMentionContext(self, r, c):
        res = []
        for i in range(self.row_num):
            if i == r:
                continue
            res.append(self.table[i][c])

        for j in range(self.col_num):
            if j == c:
                continue
            res.append(self.table[r][j])
        return res

class tableManager:

    def __init__(self, table_dir):

        self.table_directory=table_dir

        self.table_data=[]

        self.table_mark=[]

        if not table_dir=='NULL':

            try:

                self.name=path.splitext(path.split(self.table_directory)[1])[0]

                f = open(table_dir, 'r')

                json_file = json.load(f)

                for cell in json_file:

                    if cell['isheader']:

                        self.col+=1

                    else:

                        break

                f.close()

                self.row=int(len(json_file)/self.col)

                for i in range(self.row):

                    for j in range(self.col):

                        self.table_data[i].append(json_file[i*self.col+j]['text'])

                        self.table_mark[i].append(json_file[i*self.col+j]['mark'])

            except:

                raise Exception('wrong file directory.')

        else:

            print('table directory is \'NULL\' !')

    def updata_shape(self):

        self.row=len(self.table_data)

        self.col=len(self.table_data[0])

        self.shape=[self.row,self.col]

    def get_col(self,index):

        col_data=[]

        try:

            for row in self.table_data:

                col_data.append(row[index])

        except:

            raise Exception('out of index range')

        return col_data

