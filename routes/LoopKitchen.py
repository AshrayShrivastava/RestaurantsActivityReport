from flask import Blueprint, request
from service.LoopKitchenService import *

class LoopKitchen:
    loopKitchen_app = Blueprint('loopKitchen_app', __name__, template_folder='templates')

    @loopKitchen_app.route('/loadData',  methods=['GET'])
    def getData():
        return getData()

    @loopKitchen_app.route('/prepareReport',  methods=['GET'])
    def makeReport():
        return makeReport()

    @loopKitchen_app.route('/getReport',  methods=['GET'])
    def getReport():
        reportId = request.args.get('reportId')
        return getReport(reportId)
    
# print('Yo')