#! /Users/swahl/anaconda/bin/python
# coding: utf-8

#import pyabc
import numpy as np
import json

import sqlite3

from thesessionDB import thesessionDB

# update the sql database
#db = thesessionDB(delete=True,download=True)

#db.defineTables()
#db.populateTablesFromJSON(Ntest=1000)
#db.populateTablesFromJSON()

# Load the sql database without updating
db = thesessionDB(delete=False,download=False)

class dict_output(object):
    def __init__(self, file_name, method):
        self.file_obj = open(file_name, method)
    def __enter__(self):
        return self.file_obj
    def __exit__(self, type, value, traceback):
        print("Exception has been handled")
        self.file_obj.close()
        return True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class QueryFormat():
    '''
    Context manager to provide a sqlite cursor to a database, which will return query data in json format by default.
    '''
    
    def __init__(self,db,json=True):
        self.db = db
        self.json = json
        
    def __enter__(self,json=True):
        if json: # should figure out how to make this a wrapper
            db.conn.row_factory = dict_factory
            self.cursor = db.conn.cursor()
        else:
            self.cursor = db.cur
        
        return self.cursor
    
    def __exit__(self,*args):
        # reset format
        db.conn.row_factory = sqlite3.Row

def tunesMatchFragment(fragment): # should probablyb change this to return a json 
    '''
    Return all unique tune id's containing a string fragment.
    '''
    db.cur.execute("SELECT * FROM aliases WHERE alias LIKE '%"+fragment+"%'")
    q = db.cur.fetchall()  # fetch all the results of the query

    tune_ids = [x[3] for x in q]

    unique_ids = {x for x in tune_ids}
    
    return list(unique_ids)

def tunesFromID(tid,json=True):
    '''
    Return all fields from tunes matching a list of ids
    '''

    query = 'select * FROM tunes where tune_id in (' + ','.join(map(str, tid)) + ')'
    #db.cur.execute(sql_query)
    #q = db.cur.fetchall()  # fetch all the results of the query

    with QueryFormat(json) as c:
    
        c.execute(query)

        q2 = c.fetchall()
    
    return q2


def tunesFromAlias(fragment,json=True):
    
    # split the fragment on white space
    words = fragment.split()
    
    # join words in the query with wildcards to catch more with SQL LIKE
    querystr = '%' + '%'.join(words) + '%'
    
    # Find all matches for the fragment in the alias table
    #db.cur.execute("SELECT tune_id FROM aliases WHERE alias LIKE '%"+fragment+"%'")
    db.cur.execute("SELECT tune_id FROM aliases WHERE alias LIKE '"+querystr+"'")
    q = db.cur.fetchall()  # fetch all the results of the query

    tune_ids = [x[0] for x in q]

    # find all unique ids
    unique_ids = {x for x in tune_ids}
    
    query = "SELECT * FROM tunes WHERE tune_id IN ({0})".format(', '.join(x for x in unique_ids))

    # switch to json format for query and restore
    with QueryFormat(json) as c:
    
        c.execute(query)

        q2 = c.fetchall()
    
    return q2    
