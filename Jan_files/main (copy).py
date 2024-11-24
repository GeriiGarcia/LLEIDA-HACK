output = processing.run("native:shortestpathpointtopoint", {'INPUT':'postgres://dbname=\'database\' host=localhost port=5432 key=\'id\' srid=25830 type=MultiLineString checkPrimaryKeyUnicity=\'1\' table="eps"."red3" (geom)','STRATEGY':0,'DIRECTION_FIELD':'','VALUE_FORWARD':'','VALUE_BACKWARD':'','VALUE_BOTH':'','DEFAULT_DIRECTION':2,'SPEED_FIELD':'','DEFAULT_SPEED':50,'TOLERANCE':0,'START_POINT':'314639.323911,4248473.692408 [EPSG:25830]','END_POINT':'317161.770618,4248314.043882 [EPSG:25830]','OUTPUT':'TEMPORARY_OUTPUT','POINT_TOLERANCE':None})
print("The execution has finished")
print(output)

o_fc = output.featureCount()
print(o_fc)
#for node in output.getFeatures()