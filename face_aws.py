import boto3

if __name__ == "__main__":

    # Replace sourceFile and targetFile with the image files you want to compare.
    sourceFile='/home/lifetech/face/datasets/vivek/2019-05-29 18:52:30.499063.png'
    targetFile='/home/lifetech/face/Data.jpg'
    client=boto3.client('rekognition')

    fileName='Data.jpg'
    bucket='lifetech-face'
 
    imageSource=open(sourceFile,'rb')
    imageTarget=open(targetFile,'rb')
    #imageTarget=Image={'S3Object':{'Bucket':bucket,'Name':fileName}}

    response=client.compare_faces(SimilarityThreshold=70,
                                  SourceImage={'Bytes': imageSource.read()},
                                  TargetImage={'Bytes': imageTarget.read()},)
    
    for faceMatch in response['FaceMatches']:
        position = faceMatch['Face']['BoundingBox']
        confidence = str(faceMatch['Face']['Confidence'])
        print('The face at ' +
               str(position['Left']) + ' ' +
               str(position['Top']) +
               ' matches with ' + confidence + '% confidence')

    imageSource.close()
    imageTarget.close()
