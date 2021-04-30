# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo

class ArticlePipeline:

    def __init__(self):
        self.db= pymongo.MongoClient('mongodb+srv://jonathan-admin:kusogaki@clustervirginia0.esrr9.mongodb.net/moodscape?retryWrites=true&w=majority')['moodscape']
        #self.db= pymongo.MongoClient('mongodb://localhost:27017')['moodscape']
        self.collection= self.db.articles
        self.collection.delete_many({})

    def process_item(self, article, spider):
        article['_id']= self.collection.find({}).count()+1
        self.collection.update({ 'url': article['url'] }, dict(article), upsert= True)

        return article
