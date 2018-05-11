import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):

    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:146254080149:deployPortfolioTopic')

    location = {
        "bucketName": 'portfoliobuild.crudeoilmcx.com',
        "objectKey": 'portfoliobuild.zip'
    }
    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        print    "building portfolio from " + str(location)
        s3 = boto3.resource('s3')

        portfolio_bucket = s3.Bucket('portfolio.crudeoilmcx.com')
        build_bucket = s3.Bucket(location["bucketName"])

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')


        print "Job Done!"
        topic.publish(Subject="Portfolio Deployed", Message="potfolio deployed successfully")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
    except:
        topic.publish(Subject="Portfolio Deploy Failed", Message="portfolio deployment failed")
        raise
    return 'Hello from Lambda'
