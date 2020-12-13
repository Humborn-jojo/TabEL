#coding=utf8
import sklearn.metrics
import numpy as np
import cPickle as pickle
from operator import itemgetter 
from tableStruct import Mention, DataTable,scan_folder
import sys, json
import database.table as table
reload(sys)
sys.setdefaultencoding('utf8')

classifier = None
samples = []
target = []


def train(dataTable, human_marks):
    global samples
    global target

    for i in xrange(dataTable.row):
        for j in xrange(dataTable.col):
            mention = dataTable[i][j]
            if mention.cid == -1:
                continue
            eids = dataTable.get_eids(i, j)
            words = dataTable.get_words(i, j)
            entites = dataTable.get_entities(i, j)
            true_id = human_marks[i][j]
            for ii, entity in enumerate(mention.candidates):
                prior = entity.popular
                SR = mention.getSR(ii, entites)
                MES_E, MES_W = mention.getMES(ii, eids, words)
                res = int(true_id == entity.id)
                samples.append([prior, SR, MES_E, MES_W])
                target.append(res)

def predict(vec):
    return classifier.predict_proba(vec)[0][1]
     

# return has_changed
def ICA(dataTable):
    has_changed = False
    priRes = [None] * dataTable.row
    for i in xrange(dataTable.row):
        priRes[i] = [None] * dataTable.col
    for i in xrange(dataTable.row):
        for j in xrange(dataTable.col):
            priRes[i][j] = [None] * len(dataTable[i][j].candidates)

    for i in xrange(dataTable.row):
        for j in xrange(dataTable.col):
            mention = dataTable[i][j]
            if mention.cid == -1:
                continue
            eids = dataTable.get_eids(i, j)
            words = dataTable.get_words(i, j)
            entites = dataTable.get_entities(i ,j)
            i_max = (-1,-1)
            for ii, entity in enumerate(mention.candidates):
                prior = entity.popular
                SR = mention.getSR(ii, entites)
                MES_E, MES_W = mention.getMES(ii, eids, words)
                res = predict([[prior, SR, MES_E, MES_W]])
                priRes[i][j][ii] = {'name':entity.title, 'id':entity.id, 'p':-res}

                if res > i_max[1]:
                    i_max = (ii, res)
            if mention.cid != i_max[0]:
                mention.cid = i_max[0]
                has_changed = True

    if has_changed:      
        return has_changed, None

    for i in xrange(dataTable.row):
        for j in xrange(dataTable.col):
            priRes[i][j] = sorted(priRes[i][j], key=itemgetter('p'))
    return has_changed, priRes


            
def main(datapath):
    auto_marks = []
    max_iter = 100
    i=0
    for jsonpath in scan_folder(datapath):
        tableinfo=table.tableManager(jsonpath)
        datatable=DataTable(tableinfo.table_data,[tableinfo.get_col(i) for i in range(tableinfo.col)],tableinfo.table_data)
        mark=tableinfo.table_mark

        train(datatable,mark)

        for n in xrange(max_iter):
            has_changed, res = ICA(datatable)
            if not has_changed:
                auto_marks.append(res)
                break
        print u'第%d张表,迭代%d次'%(i,n)

    global classifier
    from sklearn.linear_model import LogisticRegression
    classifier = LogisticRegression()
    classifier.fit(samples, target)

    ##写入结果
    with open('./result/auto_mark.json','w') as f:
        json.dump(auto_marks, f, ensure_ascii=False)

main('datapath')
    

    


